import json
from anytree import AnyNode, RenderTree

# Load tree from json file into json object -> comment out for PrairieLearn
with open("coffee.json") as f:
    json_tree = json.load(f)


def build_anytree(json_node, parent=None):
    """
    Recursively build an anytree Node structure from JSON.
    """
    kwargs = {"name": json_node["name"]}
    
    # Include attributes only if they exist
    for attr in ["type", "pre", "post", "sequence", "link", "costs"]:
        if attr in json_node:
            kwargs[attr] = json_node[attr]
    
    node = AnyNode(**kwargs, parent=parent)

    for child in json_node.get("children", []):
        build_anytree(child, node)

    return node


# Build the anytree from the provided json_tree
root = build_anytree(json_tree)

# Visualize the tree with RenderTree
lines = []
for pre, _, node in RenderTree(root):
    lines.append(f"{pre}{node!r}")  # !r ensures AnyNode(...) format

# Output variable as string
global output
output = "\n".join(lines)

print(output)


