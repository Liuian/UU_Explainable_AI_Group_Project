
import json
from anytree.importer import DictImporter

# Load the tree
with open("coffee_advanced_tree.json") as f:
    json_tree = json.load(f)
root = DictImporter().import_(json_tree)

# Inputs check this last case
norm = {'type': 'P', 'actions': ['gotoAnnOffice']}
goal = ['haveCoffee']
beliefs = ['staffCardAvailable', 'ownCard']
preferences = [['quality', 'price', 'time'], [2, 0, 1]]

# norm = {'type': 'P', 'actions': ['gotoShop']}
# goal = ['haveCoffee', 'awake']
# beliefs = ['staffCardAvailable', 'ownCard', 'haveMoney']
# preferences = [['quality', 'price', 'time'], [1, 2, 0]]

# norm = {'type': 'P', 'actions': []}
# goal = ['haveCoffee']
# beliefs = ['machineAvailable', 'haveCoin', 'haveMoney'] # Missing 'ownCard'
# preferences = [['quality', 'price', 'time'], [2, 0, 1]]

# norm = {'type': 'P', 'actions': ['dispenseCoffee']}
# goal = ['haveCoffee']
# beliefs = ['haveMoney', 'bankCard'] 
# preferences = [['quality', 'price', 'time'], [0, 1, 2]]

actions = set(norm.get("actions", []))
norm_type = norm.get("type")

def annotate(node):
    for child in node.children:
        annotate(child)
    if node.type == "ACT":
        if norm_type == "P":
            node.violation = node.name in actions
        else:
            node.violation = node.name not in actions
        return
    if node.type == "OR":
        node.violation = all(child.violation for child in node.children)
        return
    if node.type in ["SEQ","AND"]:
        if norm_type == "P":
            node.violation = any(child.violation for child in node.children)
        else:
            node.violation = all (child.violation for child in node.children)
        return

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
            for trace, cost, vio, belief in generate_traces(child, current_beliefs):
                traces.append(([node.name] + trace, cost, vio, belief))
        return traces

    if node.type in ["SEQ", "AND"]:
        # Start with the name of the SEQ node and current beliefs
        traces = [([node.name], [0.0, 0.0, 0.0], False, list(current_beliefs))]
        
        for child in node.children:
            next_step_traces = []
          
            for trace_acc, cost_acc, violation_acc, beliefs_current in traces:
                # Get possible ways to complete the current child step
                child_options = generate_traces(child, beliefs_current)
                
                for child_trace, child_cost, child_violation, child_beliefs_final in child_options:
                    # Combine the paths
                    extended_trace = trace_acc + child_trace
                    
                    # Sum the costs of the previous steps and the new step
                    new_total_costs = [prev + new for prev, new in zip(cost_acc, child_cost)]
                    
                    # The path is a violation if the previous steps OR this step is a violation
                    combined_violation = violation_acc or child_violation
                    
                    # Add the new combined path to our list for the next iteration of the sequence
                    next_step_traces.append((
                        extended_trace, 
                        new_total_costs, 
                        combined_violation, 
                        child_beliefs_final
                    ))
            traces = next_step_traces

            if not traces: break # Sequence failed
        return traces
    return []

# Filter and select the best trace
all_traces = generate_traces(root, beliefs)
valid_traces = []

for path_trace, total_costs, is_violating, final_beliefs in all_traces:
    
    # Norm Filtering 
    if norm_type == "P" and is_violating: 
        continue
        
    if norm_type == "O":
        # At least one obligated action must be present in the path
        obligated_actions = norm.get("actions", [])
        if not any(action in path_trace for action in obligated_actions): 
            continue
    
    # Goal Filtering (Success check)
    if not all(goal_belief in final_beliefs for goal_belief in goal): 
        continue
    
    # Store only the viable candidates for preference sorting
    valid_traces.append((path_trace, total_costs))

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

print(output)
