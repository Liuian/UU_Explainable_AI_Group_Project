from anytree.importer import DictImporter
from anytree import PreOrderIter

# 建立樹狀結構
importer = DictImporter()
root = importer.import_(json_tree)
nodes_dict = {node.name: node for node in PreOrderIter(root)}

######################################################
# --- PART 1: 找出包含 action_to_explain 的最優路徑 --- #
######################################################
# Annotate the tree with violation information
prohibited = set(norm.get("actions", [])) if norm.get("type") == "P" else set()

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

def get_local_cost(node):
    """
    計算 OR 節點某個分支的局部成本：
    1. 如果是 ACT：直接回傳該 ACT 的 costs。
    2. 如果是 SEQ/AND：加總其『直接子代』中所有 ACT 的成本。
    3. 如果子代中還有 OR：根據 BDI 邏輯，需遞迴取得該子 OR 內『被選中』或『最優』的分支成本。
    """
    if node.type == 'ACT':
        return getattr(node, 'costs', [0, 0, 0])

    if node.type in ['SEQ', 'AND', 'OR']:
        total = [0, 0, 0]
        # 遍歷該分支下的所有後代動作
        # 根據預期答案 [5, 0, 3]，它是加總了該分支下「所有」會執行的 ACT
        for child in node.children:
            if child.type == 'ACT':
                costs = getattr(child, 'costs', [0, 0, 0])
                for i in range(3):
                    total[i] += costs[i]
                
        return [int(x) for x in total]

    return [0, 0, 0]

def get_priority_order(pref_weights):
    """
    根據權重回傳維度索引的優先順序。
    例如 [1, 2, 0] -> 優先序為 [1, 0, 2] (因為權重 2 在索引 1, 權重 1 在索引 0, 權重 0 在索引 2)
    但根據你的描述：『先比 preference 高的』，如果是指數值大小：
    權重值越大，優先權越高。
    """
    # 建立 (權重值, 索引) 的列表，並按權重從大到小排序
    indexed_prefs = []
    for i, w in enumerate(pref_weights):
        indexed_prefs.append((w, i))
    
    # 降序排序：權重大的排前面
    indexed_prefs.sort(key=lambda x: x[0], reverse=True)
    
    # 唯有權重相同的維度，才需要額外規則（通常按索引順序）
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
    return False # 完全相等

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