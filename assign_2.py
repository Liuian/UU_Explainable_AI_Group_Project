# Insert here your code
from anytree import PreOrderIter
from anytree import RenderTree
from anytree.importer import DictImporter

root = DictImporter().import_(json_tree)

actions = set(norm.get("actions",[]))
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
output = RenderTree(root)# assign a value to the output variable
