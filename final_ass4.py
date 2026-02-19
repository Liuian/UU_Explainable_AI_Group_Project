
from anytree.importer import DictImporter
from anytree import PreOrderIter
import json

with open("coffee.json") as f:
    json_tree = json.load(f)

# norm={'type': 'P', 'actions': ['gotoKitchen', 'gotoAnnOffice']}
# goal=['haveCoffee']
# beliefs=['haveMoney']
# preferences=[['quality', 'price', 'time'], [2, 0, 1]]
norm={}
goal=['haveCoffee']
beliefs=['AnnInOffice','haveMoney','ownCard','staffCardAvailable']
preferences=[['quality', 'price', 'time'], [2, 0, 1]]
action_to_explain="getCoffeeKitchen"

importer = DictImporter()
root = importer.import_(json_tree)
nodes_dict = {node.name: node for node in PreOrderIter(root)}

######################################################
# --- PART 1: 找出包含 action_to_explain 的最優路徑 --- #
######################################################
# Annotate the tree with violation information

actions = set(norm.get("actions", []))
n_type = norm.get("type")

def annotate(node):
    for child in node.children:
        annotate(child)

    if node.type == "ACT":
        if n_type == "P":
            node.violation = node.name in actions
        else:  # Obligation
            node.violation = node.name not in actions

    elif node.type == "OR":
        node.violation = all(child.violation for child in node.children)

    else:  # SEQ or AND
        node.violation = any(child.violation for child in node.children)

annotate(root)


# Generate traces
def generate_traces(node, current_beliefs):

    pre = getattr(node, "pre", [])
    if not all(p in current_beliefs for p in pre):
        return []

    if node.type == "ACT":
        new_beliefs = set(current_beliefs)
        post = getattr(node, "post", [])
        for p in post:
            new_beliefs.add(p)

        return [(
            [node.name],
            getattr(node, "costs", [0.0, 0.0, 0.0]),
            node.violation,
            list(new_beliefs)
        )]

    if node.type == "OR":
        traces = []
        for child in node.children:
            for trace, cost, vio, belief in generate_traces(child, current_beliefs):
                traces.append(([node.name] + trace, cost, vio, belief))
        return traces

    if node.type in ["SEQ", "AND"]:
        traces = [([node.name], [0.0, 0.0, 0.0], False, list(current_beliefs))]

        for child in node.children:
            next_step_traces = []

            for trace_acc, cost_acc, violation_acc, beliefs_current in traces:
                child_options = generate_traces(child, beliefs_current)

                for child_trace, child_cost, child_violation, child_beliefs_final in child_options:
                    extended_trace = trace_acc + child_trace
                    new_total_costs = [
                        prev + new for prev, new in zip(cost_acc, child_cost)
                    ]
                    combined_violation = violation_acc or child_violation

                    next_step_traces.append((
                        extended_trace,
                        new_total_costs,
                        combined_violation,
                        child_beliefs_final
                    ))

            traces = next_step_traces
            if not traces:
                break

        return traces

    return []


# Filter valid traces
all_traces = generate_traces(root, beliefs)
valid_traces = []

for trace, cost, violation, b in all_traces:
    # Norm filtering
    if norm.get("type") == "P" and violation:
        continue

    if norm.get("type") == "O" and not any(a in trace for a in norm.get("actions", [])):
        continue

    # Goal filtering
    if not all(g in b for g in goal):
        continue

    valid_traces.append((trace, cost))


# Sorting
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
    """
    計算 OR 節點某個分支的局部成本：
    1. 如果是 ACT：直接回傳該 ACT 的 costs。
    2. 如果是 SEQ/AND/OR：加總其所有後代 ACT 的成本。
    """
    if node.type == 'ACT':
        return getattr(node, 'costs', [0, 0, 0])

    total = [0, 0, 0]
    for desc in PreOrderIter(node):
        if desc.type == 'ACT':
            costs = getattr(desc, 'costs', [0, 0, 0])
            total = [a + b for a, b in zip(total, costs)]
    return total


def get_priority_order(pref_weights):
    """
    根據權重回傳維度索引的優先順序。
    例如 [1, 2, 0] -> 優先序為 [1, 0, 2] (因為權重 2 在索引 1, 權重 1 在索引 0, 權重 0 在索引 2)
    但根據你的描述：『先比 preference 高的』，如果是指數值大小：
    權重值越大，優先權越高。
    """
    indexed_prefs = [(w, i) for i, w in enumerate(pref_weights)]
    indexed_prefs.sort(reverse=True)
    return [item[1] for item in indexed_prefs]


def is_better_than(cost_a, cost_b, pref_weights):
    """
    比較兩組成本。回傳 True 代表 cost_a 優於 cost_b (成本更低)。
    使用字典序比較。
    """
    order = get_priority_order(pref_weights)
    for idx in order:
        if cost_a[idx] < cost_b[idx]:
            return True
        if cost_a[idx] > cost_b[idx]:
            return False
    return False


def generate_output(trace, target_name):
    # print(trace)
    if not trace or target_name not in trace:
        return []

    res = []
    target_node = nodes_dict[target_name]

    # --- 1. OR factors ---
    explained_or = set()
    limit_idx = trace.index(target_name)
    nodes_to_check = trace[:limit_idx + 1]

    for node_name in nodes_to_check:

        curr = nodes_dict[node_name]

        if curr.type == 'OR' and node_name not in explained_or:

            explained_or.add(node_name)

            idx_in_trace = trace.index(node_name)
            chosen_child_name = trace[idx_in_trace + 1]
            chosen_node = nodes_dict[chosen_child_name]

            # C factor
            res.append(['C', chosen_child_name, getattr(chosen_node, 'pre', [])])

            for sibling in curr.children:

                if sibling.name == chosen_child_name:
                    continue

                sib_descendants = [n.name for n in PreOrderIter(sibling)]
                violated = False

                # N factor
                if n_type == "P":
                    if any(a in sib_descendants for a in actions):
                        res.append(['N', sibling.name, f"P({', '.join(actions)})"])
                        violated = True
                if n_type == "O":
                    if not any(a in sib_descendants for a in actions):
                        res.append(['N', sibling.name, f"O({', '.join(actions)})"])
                        violated = True

                if violated:
                    continue

                sib_pre = getattr(sibling, 'pre', [])

                # V factor
                if all(p in beliefs for p in sib_pre):

                    c_costs = get_local_cost(chosen_node)
                    o_costs = get_local_cost(sibling)

                    if is_better_than(c_costs, o_costs, preferences[1]):
                        res.append(['V', chosen_child_name, c_costs, '>', sibling.name, o_costs])
                        continue

                # F factor
                unsatisfied = [p for p in sib_pre if p not in beliefs]
                if len(unsatisfied) > 0:
                    res.append(['F', sibling.name, unsatisfied])

    # --- 2. P Factor ---
    acts_in_trace = [n for n in trace if nodes_dict[n].type == 'ACT']

    if target_name in acts_in_trace:
        target_idx = acts_in_trace.index(target_name)

        for i in range(target_idx + 1):
            act_name = acts_in_trace[i]
            pre_conditions = getattr(nodes_dict[act_name], 'pre', [])
            if pre_conditions:
                res.append(['P', act_name, pre_conditions])

    # --- 3. L Factor ---
    current = target_node

    while hasattr(current, 'link') and current.link:

        links = current.link

        # FIX: flatten nested lists safely
        flat_links = []
        if isinstance(links, list):
            for item in links:
                if isinstance(item, list):
                    flat_links.extend(item)
                else:
                    flat_links.append(item)
        else:
            flat_links = [links]

        next_node = None

        for linked_name in flat_links:
            if isinstance(linked_name, str) and linked_name in nodes_dict:
                res.append(['L', current.name, '->', linked_name])
                next_node = nodes_dict[linked_name]
                break

        if not next_node:
            break

        current = next_node

    # --- 4. D Factor ---
    for p in reversed(target_node.ancestors):
        if getattr(p, 'type', None) in ['OR', 'AND', 'SEQ']:
            res.append(['D', p.name])

    # --- 5. U Factor ---
    res.append(['U', preferences])

    return res


output = generate_output(selected_trace, action_to_explain)
print(output)

# actions_to_explain =['getCoffee', 'getShopCoffee', 'gotoShop', 'payShop', 'getCoffeeShop']
# for action in actions_to_explain:
#     output = generate_output(trace, action)
#     print(output)