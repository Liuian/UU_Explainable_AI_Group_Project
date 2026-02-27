from anytree.importer import DictImporter
from anytree import PreOrderIter

# 建立樹狀結構
import json
with open("../coffee.json") as f:
    json_tree = json.load(f)
norm = {}
beliefs = ["haveMoney",'staffCardAvailable']
goal = ["haveCoffee"]
preferences = [["quality", "price", "time"], [1, 0, 2]]
action_to_explain = "getCoffee"

importer = DictImporter()
root = importer.import_(json_tree)
nodes_dict = {node.name: node for node in PreOrderIter(root)}

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
        else: # Obligation
            node.violation = node.name not in actions
    elif node.type == "OR":
        node.violation = all(child.violation for child in node.children)
    else: # SEQ or AND
        node.violation = any(child.violation for child in node.children)

annotate(root)

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

            if not traces: break # Sequence failed
        return traces
    return []

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

################################################
# --- PART 2: 生成解釋因子 (符合系統回饋的格式) --- #
################################################
def get_local_cost(node):
    if node.type == 'ACT':
        return getattr(node, 'costs', [0, 0, 0])
    
    total = [0, 0, 0]
    # 若為 SEQ/AND，須加總所有子節點的成本
    if node.type in ['SEQ', 'AND']:
        for child in node.children:
            child_cost = get_local_cost(child)
            for i in range(3):
                total[i] += child_cost[i]
    # 若為 OR，則根據 selected_trace 決定走哪個分支的成本
    elif node.type == 'OR':
        for child in node.children:
            if child.name in selected_trace:
                return get_local_cost(child)
        return get_local_cost(node.children[0]) if node.children else [0,0,0]
    return total

def generate_output(trace, target_name):
    if not trace or target_name not in trace:
        return []
    res = []
    target_node = nodes_dict[target_name]       # 先定義 target_node，後續邏輯才能引用
    
    # --- 1. 尋找所有 lead to A 的 OR 節點 ---
    explained_or = set()    # 追蹤已解釋過的 OR，避免重複 (雖然 D 不過濾，但 OR 解釋邏輯需要)
    
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
                    continue # 已經處理過 C 了，跳過
                    
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
                    c_costs = get_local_cost(nodes_dict[chosen_child_name])
                    o_costs = get_local_cost(sibling)
                    
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

output = generate_output(selected_trace, action_to_explain)