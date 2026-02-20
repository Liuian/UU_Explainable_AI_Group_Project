from anytree.importer import DictImporter
from anytree import PreOrderIter

root = DictImporter().import_(json_tree)

# Annotate the tree with violation information

actions = set(norm.get("actions", []))
norm_type = norm.get("type")

for i, node in enumerate(PreOrderIter(root)):
    if not hasattr(node, "name"):
        node.name = f"default_name_{i}"
    if not hasattr(node, "type"):
        node.type = "UNKNOWN"
    if not hasattr(node, "children"):
        node.children = []

def annotate(node):
    for child in node.children:
        annotate(child)
        
    # Check for empty norm 
    if norm_type is None:
     node.violation = False
     return
    
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

all_traces = []

def generate_traces(node, current_beliefs):
    
    # Check Preconditions for the internal node itself
    pre = getattr(node, "pre", [])
    if not all(p in current_beliefs for p in pre):
        return []

    # Post conditions for ACT nodes
    if node.type == "ACT":
        # New independent beliefs for the trace
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

        # print('traces in OR', traces)
        return traces
    
    if node.type in ["SEQ", "AND"]:
        # Start with the name of the SEQ node and current beliefs
        traces = [([node.name], [0.0, 0.0, 0.0], False, list(current_beliefs))]

        for child in node.children:
            next_step_traces = []

            # Iterate over the accumulated traces so far for this SEQ node
            for trace_acc, cost_acc, violation_acc, beliefs_current in traces:
                
                # Get possible ways to complete the current child step, hanldes deep children as well
                child_options = generate_traces(child, beliefs_current)

                for child_trace, child_cost, child_violation, child_beliefs_final in child_options:
              
                    # Combine the traces
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

value_names, preference = preferences

all_traces = generate_traces(root, beliefs)


def find_valid_traces(all_traces, goal):
    valid_traces = []
    for path_trace, total_costs, is_violating, final_beliefs in all_traces:
        if norm_type == "P" and is_violating:
            continue
        if norm_type == "O":
            if not any(action in path_trace for action in actions): 
              continue

        if all(g in final_beliefs for g in goal):
            valid_traces.append((path_trace, total_costs, is_violating, final_beliefs))

    return valid_traces

valid_traces = find_valid_traces(all_traces, goal)

# sorting
order = preferences[1]

# Sort the valid traces based on the specified preference order of costs
def get_sorted_cost(item):
    cost = item[1]
    return tuple(cost[i] for i in order)

if valid_traces:
    valid_traces.sort(key=get_sorted_cost)
    output = valid_traces[0][0]
else:
    output = []
