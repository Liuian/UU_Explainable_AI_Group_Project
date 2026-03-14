## Setup environment
1. `pip install anytree` 
2. `brew install graphviz`
3. `pip install graphviz pydot`

## Uninstall graphviz
- `brew uninstall graphviz`
- `brew autoremove`

## Note
### **DictImporter**
- Converts Python dictionary structure into `anytree` Node objects
- Input: Nested dictionary (like your `coffee.json`)
- Output: Node tree structure that can be operated using various anytree methods
```python
importer = DictImporter()
root = importer.import_(json_tree)  # Convert dictionary to tree object
```

### **RenderTree**
- Visualizes tree structure into **text format** (ASCII tree diagram)
- Produces this kind of effect in terminal:
```
Coffee
├── Espresso
│   ├── Lungo
│   └── Ristretto
└── Latte
```
```python
for pre, fill, node in RenderTree(root):
    print(f"{pre}{node}")  # Text version of the tree
```

### **DotExporter**
- Converts tree structure into **Graphviz DOT format** and then generates **images**
- Can generate PNG, PDF, SVG and other visualization formats
- More beautiful and professional than RenderTree
```python
DotExporter(root).to_picture('./coffee_tree.png')  # Generate image file
```

**Simple Comparison:**

| Tool | Output Format | Purpose |
|------|--------|----------|
| DictImporter | Node Object | Read Data |
| RenderTree | Text | Terminal Display |
| DotExporter | Image | Visualization |

