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
            
    # 3. P Factor: 所有在 A 之前 (含 A) 的 ACT 的 pre，且前提不為空
    acts_in_trace = [n for n in trace if nodes_dict[n].type == 'ACT']
    if target_name in acts_in_trace:
        target_idx = acts_in_trace.index(target_name)
        # 遍歷從開始到 target_name 的所有動作
        for i in range(target_idx + 1):
            act_name = acts_in_trace[i]
            pre_conditions = getattr(nodes_dict[act_name], 'pre', [])
            # 只有當前提條件非空時才加入
            if pre_conditions:
                res.append(['P', act_name, pre_conditions])
        
    # 4. L Factor: Link 修正版 (基於狀態依賴 N1.post -> N2.pre)
    acts_in_trace = [n for n in trace if nodes_dict[n].type == 'ACT']
    if target_name in acts_in_trace:
        target_node = nodes_dict[target_name]
        target_posts = getattr(target_node, 'post', [])
        
        # 只有當 A 有產出 post 時才需要找 Link
        if target_posts:
            target_idx_in_acts = acts_in_trace.index(target_name)
            # 往後找剩餘的動作
            remaining_acts = acts_in_trace[target_idx_in_acts + 1:]
            
            for next_act_name in remaining_acts:
                next_node = nodes_dict[next_act_name]
                next_pres = getattr(next_node, 'pre', [])
                
                # 推論核心：檢查 A 的 post 是否出現在下一個動作的 pre 中
                # 使用 set 交集判斷是否有重疊的狀態
                if set(target_posts) & set(next_pres):
                    res.append(['L', target_name, '->', next_act_name])
                    
                    # 處理 Chain (鏈條): 如果 next_act 也有 link 到更後面的人
                    # 這裡用一個簡單的迴圈繼續往後掃描鏈條
                    curr_link_source = next_act_name
                    curr_posts = getattr(nodes_dict[curr_link_source], 'post', [])
                    
                    # 在剩餘的動作中找下一個連結
                    source_idx = remaining_acts.index(curr_link_source)
                    for further_act_name in remaining_acts[source_idx + 1:]:
                        further_pres = getattr(nodes_dict[further_act_name], 'pre', [])
                        if set(curr_posts) & set(further_pres):
                            res.append(['L', curr_link_source, '->', further_act_name])
                            # 更新起點繼續往下找鏈條
                            curr_link_source = further_act_name
                            curr_posts = getattr(nodes_dict[curr_link_source], 'post', [])
                    
                    # 找到第一條連結路徑後即停止 (避免重複建立非直接依賴的 Link)
                    break
        
    # 5. D Factor: 由下往上
    target_node = nodes_dict[target_name]
    for p in reversed(target_node.ancestors):
        if p.type in ['OR', 'AND', 'SEQ']:
            res.append(['D', p.name])
            
    # 6. U Factor
    res.append(['U', preferences])
    return res

output = generate_output(selected_trace, action_to_explain)