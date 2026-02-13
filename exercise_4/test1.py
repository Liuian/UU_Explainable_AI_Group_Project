from anytree.importer import DictImporter
from anytree import PreOrderIter

# 建立樹狀結構
importer = DictImporter()
root = importer.import_(json_tree)
nodes_dict = {node.name: node for node in PreOrderIter(root)}

######################################################
# --- PART 1: 找出包含 action_to_explain 的最優路徑 --- #
######################################################

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

################################################
# --- PART 2: 生成解釋因子 (符合系統回饋的格式) --- #
################################################

def generate_output(trace, target_name):
    if not trace: return []
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
            
            # 找到 trace 中緊跟在 OR 後面的節點，即為選中的分支 (Alternative)
            idx_in_trace = trace.index(node_name)
            chosen_child_name = trace[idx_in_trace + 1]
            
            for sibling in curr.children:
                if sibling.name == chosen_child_name:
                    # (C) Choice Factor
                    res.append(['C', sibling.name, getattr(sibling, 'pre', [])])
                else:
                    # 遵循優先序：N > V > F
                    
                    # (N) Norm Violation
                    n_type = norm.get('type', 'P')
                    n_acts = norm.get('actions', [])
                    sib_descendants = [n.name for n in PreOrderIter(sibling)]
                    
                    violated = False
                    if n_type == 'O':
                        # 義務 (O): 若分支沒包含該動作則違反
                        if not any(a in sib_descendants for a in n_acts):
                            res.append(['N', sibling.name, f"O({', '.join(n_acts)})"])
                            violated = True
                    else:
                        # 禁止 (P): 若分支包含該動作則違反
                        if any(a in sib_descendants for a in n_acts):
                            res.append(['N', sibling.name, f"P({n_acts[0]})"])
                            violated = True
                    if violated: continue

                    # (V) Value Statement (只有當 N 不成立時)
                    # 計算雙方 Utility 分數進行比較
                    chosen_acts = [n for n in trace if nodes_dict[n].type == 'ACT']
                    chosen_score = calculate_score(chosen_acts, weights)
                    
                    other_paths = get_all_paths(sibling)
                    if other_paths:
                        # 找到失敗分支中的最優路徑
                        best_other = min(other_paths, key=lambda t: calculate_score(t, weights))
                        other_acts = [n for n in best_other if nodes_dict[n].type == 'ACT']
                        other_score = calculate_score(other_acts, weights)
                        
                        # 只有當「這條路徑比較貴」或是「至少它是合法的替代方案」時
                        # 注意：系統有時將 V 視為「只要前提滿足且不違規」的預設比較
                        # 這裡假設如果前提滿足，就進行 V 比較
                        sib_pre = getattr(sibling, 'pre', [])
                        current_beliefs = beliefs if 'beliefs' in globals() else []
                        if all(p in current_beliefs for p in sib_pre):
                            c_costs = [sum(getattr(nodes_dict[n], 'costs', [0,0,0])[j] for n in chosen_acts) for j in range(3)]
                            o_costs = [sum(getattr(nodes_dict[n], 'costs', [0,0,0])[j] for n in other_acts) for j in range(3)]
                            res.append(['V', chosen_child_name, c_costs, '>', sibling.name, o_costs])
                            continue

                    # (F) Failed Condition (只有當 N 和 V 都不成立時)
                    sib_pre = getattr(sibling, 'pre', [])
                    current_beliefs = beliefs if 'beliefs' in globals() else []
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
        
    # --- 3. L Factor ---
    target_posts = getattr(target_node, 'post', [])
    if target_posts and target_name in acts_in_trace:
        target_idx_in_acts = acts_in_trace.index(target_name)
        remaining_acts = acts_in_trace[target_idx_in_acts + 1:]
        
        for next_act_name in remaining_acts:
            next_node = nodes_dict[next_act_name]
            if set(target_posts) & set(getattr(next_node, 'pre', [])):
                res.append(['L', target_name, '->', next_act_name])
                
                # 鏈條邏輯 (Chain)
                curr_src = next_act_name
                curr_idx = remaining_acts.index(curr_src)
                for further_name in remaining_acts[curr_idx + 1:]:
                    if set(getattr(nodes_dict[curr_src], 'post', [])) & set(getattr(nodes_dict[further_name], 'pre', [])):
                        res.append(['L', curr_src, '->', further_name])
                        curr_src = further_name
                break
        
    # --- 4. D Factor ---
    for p in reversed(target_node.ancestors):
        if getattr(p, 'type', None) in ['OR', 'AND', 'SEQ']:
            res.append(['D', p.name])
            
    # --- 5. U Factor ---
    res.append(['U', preferences])
    return res

output = generate_output(selected_trace, action_to_explain)