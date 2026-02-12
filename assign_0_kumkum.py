import json
from anytree import RenderTree
from anytree.importer import DictImporter
from anytree.exporter import DotExporter

with open("coffee.json") as f:
    json_tree = json.load(f)

importer = DictImporter()
root = importer.import_(json_tree)

lines = []
for pre, _, node in RenderTree(root):
    lines.append(f"{pre}{node}")

output = "\n".join(lines)

print(output)

DotExporter(root).to_picture("coffee_tree_kumkum.png")