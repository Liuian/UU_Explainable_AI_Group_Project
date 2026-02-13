
import json
from anytree.importer import DictImporter

# Load the tree
with open("coffee.json") as f:
    json_tree = json.load(f)
root = DictImporter().import_(json_tree)

# Inputs
norm = {'type': 'P', 'actions': ['gotoAnnOffice']}
goal = ['haveCoffee']
beliefs = ['staffCardAvailable', 'ownCard']
preferences = [['quality', 'price', 'time'], [2, 0, 1]]

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
order = preferences[1]
def get_sort_key(item):
    cost = item[1]
    return tuple(cost[i] for i in order)

if valid_traces:
    valid_traces.sort(key=get_sort_key)
    output = valid_traces[0][0]
else:
    output = []
