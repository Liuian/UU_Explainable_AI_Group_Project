# Insert here your code
from anytree import RenderTree
from anytree.importer import DictImporter
root = DictImporter().import_(json_tree)
actions = set(norm["actions"])
norm_type = norm["type"]
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