from anytree.importer import DictImporter
from anytree import PreOrderIter
from typing import List, Optional, Tuple
import json


######################################################
# --- PART 1: 找出包含 action_to_explain 的最優路徑 --- #
######################################################
def annotate(node):
    # Post-order traversal (bottom-up)
    for child in node.children:
        annotate(child)

    actions = set(norm.get("actions", []))
    n_type = norm.get("type")

    if node.type == "ACT":
        if n_type == "P":
            node.violation = node.name in actions
        else:  # Obligation
            node.violation = node.name not in actions
    elif node.type == "OR":
        node.violation = all(child.violation for child in node.children)
    else:  # SEQ or AND
        node.violation = any(child.violation for child in node.children)

# Generate traces
def generate_traces(node, current_beliefs):
    # Check Preconditions for the internal node itself
    pre = getattr(node, "pre", [])
    if not all(p in current_beliefs for p in pre):
        return []

    if node.type == "ACT":
        new_beliefs = set(current_beliefs)
        post = getattr(node, "post", [])
        for p in post:
            new_beliefs.add(p)

        return [([node.name], getattr(node, "costs", [0.0, 0.0, 0.0]), node.violation, list(new_beliefs))]

    if node.type == "OR":
        traces = []
        for child in node.children:
            for t, c, v, b in generate_traces(child, current_beliefs):
                traces.append(([node.name] + t, c, v, b))
        return traces

    if node.type in ["SEQ", "AND"]:
        # Start with the name of the SEQ node and current beliefs
        traces = [([node.name], [0.0, 0.0, 0.0], False, list(current_beliefs))]

        for child in node.children:
            next_step_traces = []
            for t_acc, c_acc, v_acc, b_curr in traces:
                child_options = generate_traces(child, b_curr)
                for ct, cc, cv, cb in child_options:
                    new_costs = [x + y for x, y in zip(c_acc, cc)]
                    next_step_traces.append((t_acc + ct, new_costs, v_acc or cv, cb))
            traces = next_step_traces

            if not traces: break  # Sequence failed
        return traces
    return []

################################################
# --- PART 2: 生成解釋因子 (符合系統回饋的格式) --- #
################################################
def get_local_cost(node, trace):
    if node.type == 'ACT':
        return getattr(node, 'costs', [0, 0, 0])

    total = [0, 0, 0]
    # 若為 SEQ/AND，須加總所有子節點的成本
    if node.type in ['SEQ', 'AND']:
        for child in node.children:
            child_cost = get_local_cost(child,trace)
            for i in range(3):
                total[i] += child_cost[i]
    # 若為 OR，則根據 selected_trace 決定走哪個分支的成本
    elif node.type == 'OR':
        for child in node.children:
            if child.name in trace:
                return get_local_cost(child, trace)
        return get_local_cost(node.children[0], trace) if node.children else [0, 0, 0]
    return total

def generate_output(trace, target_name, nodes_dict):
    if not trace or target_name not in trace:
        return []
    res = []
    target_node = nodes_dict[target_name]  # 先定義 target_node，後續邏輯才能引用

    # --- 1. 尋找所有 lead to A 的 OR 節點 ---
    explained_or = set()  # 追蹤已解釋過的 OR，避免重複 (雖然 D 不過濾，但 OR 解釋邏輯需要)

    # 遍歷執行路徑中，直到 target_name 為止的所有節點
    try:
        limit_idx = trace.index(target_name)
        nodes_to_check = trace[:limit_idx + 1]
    except ValueError:
        nodes_to_check = trace

    for node_name in nodes_to_check:
        curr = nodes_dict[node_name]
        if curr.type == 'OR' and node_name not in explained_or:
            explained_or.add(node_name)

            # 1. 確定選中的分支 (Chosen Alternative)
            idx_in_trace = trace.index(node_name)
            chosen_child_name = trace[idx_in_trace + 1]
            chosen_node = nodes_dict[chosen_child_name]

            # 2. 強制第一順位：產出選中分支的 C factor
            res.append(['C', chosen_child_name, getattr(chosen_node, 'pre', [])])

            # 3. 遍歷其他沒被選中的兄弟節點 (Alternatives)
            for sibling in curr.children:
                if sibling.name == chosen_child_name:
                    continue  # 已經處理過 C 了，跳過

                # ----- 剩餘的優先序：N > V > F -----
                # (N) Norm Violation
                n_type = norm.get('type', 'P')
                n_acts = norm.get('actions', [])
                sib_descendants = [n.name for n in PreOrderIter(sibling)]

                violated = False
                if n_type == 'O':
                    if sibling.type != 'ACT':
                        # 判斷如果走 sibling 這條路，義務是否『有可能』被履行
                        can_fulfill = False

                        # 1. 檢查 sibling 分支內部是否包含義務
                        if any(a in sib_descendants for a in n_acts):
                            can_fulfill = True

                        # 2. 檢查 sibling 之後的序列 (不改變 curr，使用 temp)
                        if not can_fulfill:
                            temp_curr = sibling
                            while temp_curr.parent:
                                p = temp_curr.parent
                                if p.type == 'SEQ':
                                    idx = p.children.index(temp_curr)
                                    subsequent_siblings = p.children[idx + 1:]
                                    for s in subsequent_siblings:
                                        # 檢查後續兄弟節點的子孫
                                        s_desc = [node.name for node in PreOrderIter(s)]
                                        if any(a in s_desc for a in n_acts):
                                            can_fulfill = True
                                            break
                                if can_fulfill: break
                                temp_curr = p

                        # 如果『沒做』且『未來也不會做』，才是違反義務
                        if not can_fulfill:
                            res.append(['N', sibling.name, f"O({', '.join(n_acts)})"])
                            violated = True

                else:
                    # 禁止 (P): 若分支包含該動作則違反
                    if any(a in sib_descendants for a in n_acts):
                        # 顯示 norm['actions'] 裡的所有動作
                        res.append(['N', sibling.name, f"P({', '.join(n_acts)})"])
                        violated = True
                if violated: continue

                # (V) Value Statement - 修正成本計算為局部 (get_local_cost)
                sib_pre = getattr(sibling, 'pre', [])
                current_beliefs = beliefs if 'beliefs' in globals() else []

                # 只有在前提滿足的情況下才進行效用比較 (V)
                if all(p in current_beliefs for p in sib_pre):
                    # --- 關鍵修正：使用 get_local_cost 取得局部成本 ---
                    c_costs = get_local_cost(nodes_dict[chosen_child_name], trace)
                    o_costs = get_local_cost(sibling, trace)

                    # 只有當選中的分支在字典序上「優於」或「等於」競爭分支時才回報 V
                    # 或者依系統慣例，只要是合法的 Alternative 且被選中，就出 V 因子
                    res.append(['V', chosen_child_name, c_costs, '>', sibling.name, o_costs])
                    continue

                # (F) Failed Condition (只有當 N 和 V 都不成立時)
                unsatisfied = [p for p in sib_pre if p not in current_beliefs]
                res.append(['F', sibling.name, unsatisfied if unsatisfied else sib_pre])

    # --- 2. P Factor ---
    acts_in_trace = [n for n in trace if nodes_dict[n].type == 'ACT']
    if target_name in acts_in_trace:
        target_idx = acts_in_trace.index(target_name)
        for i in range(target_idx + 1):
            act_name = acts_in_trace[i]
            pre_conditions = getattr(nodes_dict[act_name], 'pre', [])
            if pre_conditions:
                res.append(['P', act_name, pre_conditions])

    # --- 3. L Factor (連鎖反應修正版) ---
    if target_name in acts_in_trace:
        target_idx_in_acts = acts_in_trace.index(target_name)
        # 我們要檢查目標動作之後的所有 ACT
        remaining_acts = acts_in_trace[target_idx_in_acts + 1:]

        current_trigger_name = target_name

        # 使用循環不斷向後尋找因果鏈
        i = 0
        while i < len(remaining_acts):
            next_act_name = remaining_acts[i]
            current_node = nodes_dict[current_trigger_name]
            next_node = nodes_dict[next_act_name]

            # 取得當前動作的後置條件與下一個動作的前置條件
            current_posts = getattr(current_node, 'post', [])
            next_pres = getattr(next_node, 'pre', [])

            # 如果有交集，代表存在因果關係 (Lead to)
            if set(current_posts) & set(next_pres):
                res.append(['L', current_trigger_name, '->', next_act_name])
                # 將「下一個動作」設為新的觸發者，繼續往後找
                current_trigger_name = next_act_name
                # 重新從剩下的動作中尋找 (重置索引)
                # 註：這裡通常是找緊接在後的第一個滿足條件的動作

            i += 1

    # --- 4. D Factor ---
    for p in reversed(target_node.ancestors):
        if getattr(p, 'type', None) in ['OR', 'AND', 'SEQ']:
            res.append(['D', p.name])

    # --- 5. U Factor ---
    res.append(['U', preferences])
    return res

def generate_formal_explanation(norm, beliefs, goal, preferences, action_to_explain):
    with open(TREE_FILE_LOCATION) as f:
        json_tree = json.load(f)
    importer = DictImporter()
    root = importer.import_(json_tree)
    nodes_dict = {node.name: node for node in PreOrderIter(root)}
    annotate(root)
    # Filter and select the best trace
    all_traces = generate_traces(root, beliefs)
    valid_traces = []

    for trace, cost, violation, b in all_traces:
        #  Norm Filtering
        if norm.get("type") == "P" and violation: continue
        if norm.get("type") == "O" and not any(a in trace for a in norm.get("actions", [])): continue

        # Goal Filtering
        if not all(g in b for g in goal): continue

        valid_traces.append((trace, cost))

    # sorting
    weights = preferences[1]

    def get_sort_key(item):
        cost = item[1]
        return tuple(cost[i] for i in weights)

    if valid_traces:
        valid_traces.sort(key=get_sort_key)
        selected_trace = valid_traces[0][0]
    else:
        selected_trace = []

    return generate_output(selected_trace, action_to_explain,nodes_dict), selected_trace

"""
----------NATURAL LANGUAGE EXPLANATION----------
"""

"""
Function to translate user norms (P or O) into natural English
"""
def norm_to_english(norm_code):
    norm_type = norm_code[0]
    actions_list = norm_code[norm_code.find("(")+1:norm_code.find(")")].split(",")
    actions_text = [action_names_present.get(a.strip(), a.strip()) for a in actions_list]

    if norm_type == 'P':
        return f"you were not allowed to {actions_text[0]}" if len(actions_text) == 1 \
            else f"you were not allowed to {', '.join(actions_text[:-1])}, or {actions_text[-1]}"
    elif norm_type == 'O':
        return f"you were supposed to {actions_text[0]}" if len(actions_text) == 1 \
            else f"you were supposed to {', '.join(actions_text[:-1])}, or {actions_text[-1]}"

"""
Function to replace past tenses with the gerund to fit grammar structure for N items
"""
def past_to_gerund(past_text):
    replacements = {
        'got ': 'getting ',
        'obtained ': 'obtaining ',
        'paid ': 'paying ',
        'went ': 'going ',
        'own ': 'owning ',
    }
    for k, v in replacements.items():
        if past_text.startswith(k):
            return past_text.replace(k, v, 1)
    return past_text + "ing"

"""
Function to remove the repeated sentences in the final story
"""
def remove_duplicate_sentences(story_text):
    sentences = story_text.split(".")
    cleaned = [s.strip() for s in sentences if s.strip()]
    seen = set()
    unique_sentences = []
    for s in cleaned:
        if s not in seen:
            unique_sentences.append(s)
            seen.add(s)
    return ". ".join(unique_sentences) + "."

"""
Function to generate the full natural English story based on the explanation of 
assignment 4. Loops through the explanation to identify items (N, F, D etc.) and
replace their parts with natural English structures. 
"""
def generate_nl_explanation(explanation):
    story = []
    criteria, priorities = None, None

    # Determine overall goal (last D)
    overall_goal = None
    for f in reversed(explanation):
        if f[0] == 'D' and isinstance(f[1], str):
            overall_goal = action_names_present.get(f[1], f[1])
            break

    # Turn overall goal into natural English part
    if overall_goal:
        story.append(f"The agent's goal was to {overall_goal}.")

    # Extract priorities
    for f in explanation:
        if f[0] == 'U':
            criteria, priorities = f[1][0], f[1][1]


    # Extract N actions to merge all N sentences for explaining
    n_explanation = {}
    f_explanation = []
    non_nf_explanation = []

    for f in explanation:
        if f[0] == 'N':
            alt, norm_code = f[1], f[2]
            n_explanation.setdefault(norm_code, []).append(alt)
        elif f[0] == 'F':
            f_explanation.append(f)
        else:
            non_nf_explanation.append(f)

    # Process explanation lines
    for f in non_nf_explanation:
        key = f[0]

        if len(f) > 1 and isinstance(f[1], str):
            if key in ['F', 'N']:
                action_text = action_names_present.get(f[1], f[1])
            else:
                action_text = action_names_past.get(f[1], f[1])
        else:
            continue

        preconds = f[2] if len(f) > 2 else []

        # Map C and P items to respective natural language parts
        if key in ['P', 'C']:
            meaningful = [pc for pc in preconds if pc in precondition_mapping]
            if meaningful:
                text = " and ".join(precondition_mapping[pc] for pc in meaningful)
                story.append(f"The agent {action_text} because {text}.")
            else:
                story.append(f"The agent {action_text}.")

        # Determine mapping of user preferences and choose correct nl mapping
        elif key == 'V':
            chosen, other = f[1], f[4]
            chosen_costs, other_costs = f[2], f[5]
            if criteria and priorities:
                sorted_idx = sorted(range(len(priorities)), key=lambda i: -priorities[i])
                for idx2 in sorted_idx:
                    if chosen_costs[idx2] != other_costs[idx2]:
                        reason = criteria[idx2]
                        break
                else:
                    reason = criteria[0]

                # Append explanation of priorities agent
                story.append(
                    f"Given the agent's priorities, the agent chose "
                    f"{past_to_gerund(action_names_past.get(chosen, chosen))} over "
                    f"{past_to_gerund(action_names_past.get(other, other))} because "
                    f"it was better in terms of {reason}."
                )

    # For all Skipped actions, only explain the reason once
    for norm_code, alts in n_explanation.items():
        alts_gerund = [past_to_gerund(action_names_past.get(alt, alt)) for alt in alts]
        if len(alts_gerund) == 1:
            skipped_actions = alts_gerund[0]
        else:
            skipped_actions = ", ".join(alts_gerund[:-1]) + " and " + alts_gerund[-1]
        story.append(f"The agent skipped {skipped_actions} because {norm_to_english(norm_code)}.")

    # Map F parts to their respective natural language parts
    for f in f_explanation:
        if len(f) > 1 and isinstance(f[1], str):
            action_text = action_names_present.get(f[1], f[1])
        else:
            continue

        preconds = f[2]
        meaningful = [pc for pc in preconds if pc in negated_precondition_mapping]
        if meaningful:
            text = " and ".join(negated_precondition_mapping[pc] for pc in meaningful)
            story.append(f"The agent didn't {action_text} because {text}.")
        else:
            story.append(f"The agent didn't {action_text}.")
    nl_explanation = " ".join(story)
    nl_explanation = remove_duplicate_sentences(nl_explanation)
    return nl_explanation

"""
Function to explain the reason why the chosen action is not executed
"""
def non_executed_action_explanation(norm, beliefs, goal, action_to_explain):
    overall_goal = action_names_present.get(goal[0], goal[0])
    story = [f"The agent's goal was to {overall_goal}."]

    with open(TREE_FILE_LOCATION) as f:
        json_tree = json.load(f)
    root = DictImporter().import_(json_tree)
    nodes_dict = {node.name: node for node in PreOrderIter(root)}
    annotate(root)


    if norm:
        n_type = norm.get("type")
        n_actions = norm.get("actions",[])
        if n_type =="P" and action_to_explain in n_actions:
            n_actions = norm.get("actions")
            norm_code = f"P({', '.join(n_actions)})"
            alts_gerund = [past_to_gerund(action_names_past.get(action_to_explain, action_to_explain))]
            story.append(f"The agent skipped {alts_gerund[0]} because {norm_to_english(norm_code)}.")
            return " ".join(story)

    all_traces = generate_traces(root, beliefs)

    if not any(action_to_explain in t for t, _, _, _ in all_traces):
        pre = getattr(nodes_dict[action_to_explain], "pre", [])
        action_text = action_names_present.get(action_to_explain, action_to_explain)
        meaningful = [pc for pc in pre if pc in negated_precondition_mapping]
        if meaningful:
            text = " and ".join(negated_precondition_mapping[pc] for pc in meaningful)
            story.append(f"The agent didn't {action_text} because {text}.")

    if norm and norm.get("type") == "O":
        o_actions = norm.get("actions",[])

        target_action_traces = [t for t, _, _, _ in all_traces if action_to_explain in t]
        if target_action_traces:
            O_satisfying = any(any(o in t for o in o_actions) for t in target_action_traces)
            if not O_satisfying:
                o_actions = norm.get("actions")
                norm_code = f"O({', '.join(o_actions)})"
                alts_gerund = [past_to_gerund(action_names_past.get(action_to_explain, action_to_explain))]
                story.append(f"The agent skipped {alts_gerund[0]} because {norm_to_english(norm_code)}.")
    return " ".join(story)

"""
These dictionaries of actions and preconditions consists of the variables from
the assignment 4 explanations translated into English natural language parts of
sentences.  
"""
# Names of translated actions in past tense
action_names_past = {
    'haveCoffee': "had coffee",
    'getKitchenCoffee': "got coffee in the kitchen",
    'getAnnOfficeCoffee': "got coffee from Ann's office",
    'getShopCoffee': "got coffee from the shop",
    'getOwnCard': "obtained your own card",
    'getOthersCard': "obtained someone else's card",
    'getCoffeeKitchen': "got coffee in the kitchen",
    'getCoffeeShop': "got coffee from the shop",
    'getCoffee': "got coffee",
    'getStaffCard': "got a staff card",
    'gotoKitchen': "went to the kitchen",
    'gotoAnnOffice': "went to Ann's office",
    'gotoShop': "went to the shop",
    'getPod': "obtained a coffee pod",
    'payShop': "paid at the shop"
}

# Function to map tense of action variables into present tense for F and D items
action_names_present = {k: v.replace("got", "get").replace("obtained", "obtain").replace("paid", "pay").replace("went", "go").replace("had", "have")
                        for k, v in action_names_past.items()}

# Precondition variable names mapped to natural English sentence parts
# atShop, atAnnOffice, atKitchen excluded since they are not valuable
precondition_mapping = {
    "ownCard": "you owned a card",
    "colleagueAvailable": "the colleague was available to lend a card",
    "haveCard": "you had a card available",
    "staffCardAvailable": "a staff card was available",
    "haveMoney": "you had enough money",
    "AnnInOffice": "Ann was present in her office",
    "havePod": "you had a coffee pod",
    "paidShop": "you had paid at the shop"
}

# Function to negate preconditions for F items
negated_precondition_mapping = {k: v.replace("were", "were not").replace("had", "did not have").replace("was", "was not")
                               for k, v in precondition_mapping.items()}

# 5 inputs given in peer review
inputs = [
    {
        "norm": {"type": "P", "actions": ["payShop"]},
        "beliefs": ["staffCardAvailable", "ownCard", "colleagueAvailable", "haveMoney", "AnnInOffice"],
        "goal": ["haveCoffee"],
        "preferences": [["quality", "price", "time"], [1, 2, 0]],
        "action_to_explain": "payShop"
    },
    {
        "norm": {},
        "beliefs": ["staffCardAvailable", "ownCard"],
        "goal": ["haveCoffee"],
        "preferences": [["quality", "price", "time"], [0, 1, 2]],
        "action_to_explain": "getCoffeeKitchen"
    },
    {
        "norm": {},
        "beliefs": ["haveMoney", "AnnInOffice"],
        "goal": ["haveCoffee"],
        "preferences": [["quality", "price", "time"], [0, 1, 2]],
        "action_to_explain": "getCoffeeShop"
    },
    {
        "norm": {"type": "P", "actions": ["gotoAnnOffice"]},
        "beliefs": ["staffCardAvailable", "ownCard", "colleagueAvailable", "haveMoney", "AnnInOffice"],
        "goal": ["haveCoffee"],
        "preferences": [["quality", "price", "time"], [0, 1, 2]],
        "action_to_explain": "payShop"
    },
    {
        "norm": {"type": "P", "actions": ["payShop"]},
        "beliefs": ["staffCardAvailable", "ownCard", "colleagueAvailable", "haveMoney"],
        "goal": ["haveCoffee"],
        "preferences": [["quality", "price", "time"], [1, 2, 0]],
        "action_to_explain": "gotoKitchen"
    }
]
TREE_FILE_LOCATION = "../coffee.json"
with open("nl_output_5inputs_v3.txt", "w", encoding="utf-8") as f:
    for idx,params in enumerate(inputs, 1):
        norm = params["norm"]
        beliefs = params["beliefs"]
        goal = params["goal"]
        preferences = params["preferences"]
        action_to_explain = params["action_to_explain"]

        formal_explanation, selected_trace = generate_formal_explanation(norm, beliefs, goal, preferences, action_to_explain)
        if len(formal_explanation) == 0:
            nl_explanation = non_executed_action_explanation(norm, beliefs, goal, action_to_explain)
            f.write(f"{idx}.explanation:\n{formal_explanation}\nstory:\n{nl_explanation}\n\n\n")
        else:
            nl_explanation = generate_nl_explanation(formal_explanation)
            f.write(f"{idx}.explanation:\n{formal_explanation}\nstory:\n{nl_explanation}\n\n\n")
