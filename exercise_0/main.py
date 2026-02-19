import json
from anytree import RenderTree
from anytree.importer import DictImporter
from anytree.exporter import DotExporter


# 1. Read coffee.json file and store to json_tree
file_path = '../coffee_advanced_tree.json'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        json_tree = json.load(f)
    print("Successfully loaded coffee.json!\n")
except FileNotFoundError:
    print(f"Error: Cannot find {file_path}. Please check if the file exists.")


# 2. Initialize AnyTree importer
# DictImporter converts Python dictionary into anytree Node objects
importer = DictImporter()
root = importer.import_(json_tree)


# 3. Store visualization results into output variable
lines = []  # Use join to combine lines with proper line breaks, no trailing newline to match PrairieLearned format
for pre, fill, node in RenderTree(root):
    lines.append(f"{pre}{node}")

output = "\n".join(lines)


# 4. Print the result to verify
print(output)

# 4. 寫入 txt 檔案
output_txt = './coffee_advanced_tree_info.txt'
try:
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"✓ 成功將詳細樹狀資訊存檔至: {output_txt}")
except Exception as e:
    print(f"✗ 存檔失敗: {e}")


# 5. Graphical visualization - generate PNG image
# DotExporter uses Graphviz to generate tree diagram
try:
    output_image = './exercise_0/coffee_tree.png'
    DotExporter(root).to_picture(output_image)
    print(f"\n✓ Tree diagram successfully saved to: {output_image}")
except Exception as e:
    print(f"\n✗ Failed to generate image: {e}")
    print("  Please ensure Graphviz is installed: brew install graphviz")
    print("  And Python packages: pip install graphviz pydot")