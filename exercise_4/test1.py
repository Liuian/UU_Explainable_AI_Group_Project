from anytree.importer import DictImporter
from anytree import PreOrderIter

# 1. 建立樹狀結構
importer = DictImporter()
root = importer.import_(json_tree)
nodes_dict = {node.name: node for node in PreOrderIter(root)}

# --- PART 1: 找出包含 action_to_explain 的最優路徑 ---

def get_all_paths(node):
    """忽略 Beliefs，找出所有邏輯上可行的路徑組合"""
    if node.type == 'ACT':
        return [[node.name]]
    
    if node.type == 'SEQ':
        res = [[]]
        # 依照 sequence 排序
        children = sorted(node.children, key=lambda x: getattr(x, 'sequence', 0))
        for child in children:
            child_paths = get_all_paths(child)
            if not child_paths: continue
            res = [r + cp for r in res for cp in child_paths]
        return [[node.name] + r for r in res]
    
    if node.type == 'OR':
        res = []
        for child in node.children:
            for cp in get_all_paths(child):
                res.append([node.name] + cp)
        return res
    return []

def calculate_score(trace_names, weights):
    """計算路徑的 Utility 分數"""
    total_costs = [0.0, 0.0, 0.0]
    for name in trace_names:
        node = nodes_dict[name]
        costs = getattr(node, 'costs', [0.0, 0.0, 0.0])
        for i in range(3):
            total_costs[i] += costs[i]
    # Dot product: Score = Cost * Weights
    return sum(total_costs[i] * weights[i] for i in range(3))

# 執行尋路
all_paths = get_all_paths(root)
weights = preferences[1]

# 過濾出包含目標動作的路徑，並選出分數最優者
valid_traces = [t for t in all_paths if action_to_explain in t]

if valid_traces:
    # 這裡選取分數最低（代價最小）的路徑
    selected_trace = min(valid_traces, key=lambda t: calculate_score(t, weights))
else:
    # 萬一真的找不到，保底方案：直接抓 target 的路徑
    selected_trace = [n.name for n in nodes_dict[action_to_explain].path]

# --- PART 2: 生成解釋因子 (符合系統回饋的格式) ---

def generate_output(trace, target_name):
    if not trace: return []
    res = []
    
    # 1. C Factor: 頂層 OR 分支
    branch_name = trace[1]
    res.append(['C', branch_name, getattr(nodes_dict[branch_name], 'pre', [])])
    
    # 2. N Factor: 動態 O/P 標籤
    n_type = norm.get('type', 'P')
    n_acts = ", ".join(norm.get('actions', []))
    n_label = f"{n_type}({n_acts})"
    for child in root.children:
        if child.name != branch_name:
            res.append(['N', child.name, n_label])
            
    # 3. P Factor: 解釋 action_to_explain 的前置動作
    acts = [n for n in trace if nodes_dict[n].type == 'ACT']
    if target_name in acts:
        idx = acts.index(target_name)
        p_act = acts[idx-1] if idx > 0 else target_name
        res.append(['P', p_act, getattr(nodes_dict[p_act], 'pre', [])])
        
    # 4. L Factor: Link (第一個 ACT -> 最後一個 ACT)
    if len(acts) >= 2:
        res.append(['L', acts[0], '->', acts[-1]])
        
    # 5. D Factor: 由下往上
    target_node = nodes_dict[target_name]
    for p in reversed(target_node.ancestors):
        if p.type in ['OR', 'AND', 'SEQ']:
            res.append(['D', p.name])
            
    # 6. U Factor
    res.append(['U', preferences])
    return res

output = generate_output(selected_trace, action_to_explain)


"""
77%

Your answer is:
['getCoffee', 'getAnnOfficeCoffee', 'gotoAnnOffice', 'getPod', 'getCoffeeAnnOffice']
[['C', 'getAnnOfficeCoffee', ['AnnInOffice']], ['N', 'getKitchenCoffee', 'P(gotoKitchen)'], ['N', 'getShopCoffee', 'P(gotoKitchen)'], ['P', 'gotoAnnOffice', ['AnnInOffice']], ['L', 'gotoAnnOffice', '->', 'getCoffeeAnnOffice'], ['D', 'getAnnOfficeCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]]

This answer is incorrect.
The selected trace is correct, but the expected explanation for the selected trace is the following:
[['C', 'getAnnOfficeCoffee', ['AnnInOffice']], ['N', 'getKitchenCoffee', 'P(gotoKitchen)'], ['V', 'getAnnOfficeCoffee', [2, 0, 6], '>', 'getShopCoffee', [0, 3, 9]], ['P', 'gotoAnnOffice', ['AnnInOffice']], ['L', 'gotoAnnOffice', '->', 'getCoffeeAnnOffice'], ['D', 'getAnnOfficeCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [2, 0, 1]]]]
"""

"""
55%

Your answer is:
['getCoffee', 'getShopCoffee', 'gotoShop', 'payShop', 'getCoffeeShop']
[['C', 'getShopCoffee', ['haveMoney']], ['N', 'getKitchenCoffee', 'O(payShop)'], ['N', 'getAnnOfficeCoffee', 'O(payShop)'], ['P', 'gotoShop', []], ['L', 'gotoShop', '->', 'getCoffeeShop'], ['D', 'getShopCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [1, 2, 0]]]]

This answer is incorrect.
The selected trace is correct, but the expected explanation for the selected trace is the following:
[['C', 'getShopCoffee', ['haveMoney']], ['N', 'getKitchenCoffee', 'O(payShop)'], ['N', 'getAnnOfficeCoffee', 'O(payShop)'], ['P', 'payShop', ['haveMoney']], ['L', 'payShop', '->', 'getCoffeeShop'], ['D', 'getShopCoffee'], ['D', 'getCoffee'], ['U', [['quality', 'price', 'time'], [1, 2, 0]]]]
"""