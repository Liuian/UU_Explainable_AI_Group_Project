import json
from anytree import AnyNode

# Load tree from json file into json object -> comment out for PrairieLearn!
with open("coffee.json") as f:
    json_tree = json.load(f)

with open("coffee_advanced_tree.json") as v:
    json_adv_tree = json.load(v)


def create_anytree(starting_node, parent=None):
    """
    Converts json tree object into anytree object using AnyNode class.
    Only adds attribute values to node in tree if such value is present 
    for that node. Parent-child connections are preserved using recursion.

    Input params:
    starting_node: starting node associated with given starting node name
    parent: a parent node in the anytree object
    """

    # Initialization of name attribute of starting node (key)
    attributes = {"name": starting_node["name"]}

    # Initialization of other node attributes (values) if present for node in json tree
    for attr in ["type", "pre", "post", "sequence", "link", "costs"]:
        if attr in starting_node:
            attributes[attr] = starting_node[attr]
    
    # Create new AnyNode object and set parent 
    node = AnyNode(**attributes, parent=parent)
    
    # Collect children of node object and pass current node as parent of those child nodes
    for child in starting_node.get("children", []):
        create_anytree(child, node)
    
    return node


def find_starting_node(anytree_obj, starting_node_name):
    """
    Locates the location of the given starting node. Checks if starting node is 
    root node and if not the case, recursively visits the child nodes of the
    root and subsequent node until starting node is located. 

    Input params:
    starting_node_name: string containing name starting node
    anytree_obj: anytree object containing json tree 
    """
    # Check if starting node is root node
    if anytree_obj.name == starting_node_name:
        return anytree_obj
    
    # Recursive search to find starting node
    for child in anytree_obj.children:
        result = find_starting_node(child, starting_node_name)
        if result is not None:
            return result
        
    return None


def find_traces(node):
    """
    Finds all possible execution traces starting from given node
    in tree using recursion. Uses the semantics of the tree regarding
    OR, SEQ and AND nodes. 
    
    Returns a list of traces, each trace is a list of node names. 
    """
    # Returns name of leaf node (ACT type or no children)
    if node.type == "ACT" or len(node.children) == 0:
        return [[node.name]]
    
    # Initialize list of all possible traces
    all_traces = []
    
    # Computes all traces for each child of OR nodes
    if node.type == "OR":
        for child in node.children:
            child_traces = find_traces(child)

            # Append name of current node at start of trace child
            for child_trace in child_traces:
                all_traces.append([node.name] + child_trace)
    
    # Computes all traces for each child of AND/SEQ nodes
    elif node.type in ["SEQ", "AND"]:

        # Initialize partial trace list 
        part_traces = [[]]

        # Compute trace for each child in order
        for child in node.children:

            # Recursively find all traces current node
            child_traces = find_traces(child)

            # Generate all extensions of partial trace
            new_part = []
            for pt in part_traces:
                for child_trace in child_traces:
                    new_part.append(pt + child_trace)

            # Update partial trace
            part_traces = new_part
        
        # Append name of current node at start of each trace
        for pt in part_traces:
            all_traces.append([node.name] + pt)
    
    return all_traces

# Define starting node 
starting_node_name = "getKitchenCoffee"

# Build json tree into anytree object
anytree_obj = create_anytree(json_tree)

# Locate the starting node in the anytree object
starting_node = find_starting_node(anytree_obj, starting_node_name)

# Collect all the traces starting from starting_node
output = find_traces(starting_node)

# Comment out for Prairielearn!
print(output)


"""
Testing the advanced tree 
"""
# # Define starting node 
# starting_node_name_adv = "chooseSource"

# # Build json tree into anytree object
# anytree_obj_adv = create_anytree(json_adv_tree)

# # Locate the starting node in the anytree object
# starting_node_adv = find_starting_node(anytree_obj_adv, starting_node_name_adv)

# # Collect all the traces starting from starting_node
# output_adv = find_traces(starting_node_adv)

# # Comment out for Prairielearn!
# print(output_adv)