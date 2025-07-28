import csv
import sys
from collections import defaultdict

def read_csv(file_path):
    data = []
    with open(file_path, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            processed_row = []
            for item in row:
                if item == '\\N':
                    processed_row.append(None)
                elif item.startswith('{') and item.endswith('}'):
                    processed_row.append(item[1:-1].split(','))
                else:
                    processed_row.append(item)
            data.append(processed_row)
    return data

def generate_dot_with_levels(data):
    dot_lines = [
        "digraph query_plan {",
        "  rankdir=TB;",
        "  nodesep=0.5;",
        "  ranksep=1.0;",
        "  node [shape=box, style=\"rounded,filled\", fillcolor=\"lightblue\"];",
        "  edge [arrowhead=normal];",
        "",
    ]
    
    nodes = set()
    edges = set()
    level_nodes = defaultdict(list)

    for row in data:
        level, path_name, path_type, child_paths, startup_cost, total_cost, rows, is_del = row

        nodes.add(path_name)
        level_nodes[int(level)].append(path_name)
        
        if child_paths:
            for child in child_paths:
                if child and child.strip():
                    edges.add((child.strip(), path_name))

    for row in data:
        level, path_name, path_type, child_paths, startup_cost, total_cost, rows, is_del = row
        
        label = (
            f"{path_name}\\n"
            f"Type: {path_type}\\n"
            f"Cost: {startup_cost}..{total_cost}\\n"
            f"Rows: {rows}"
        )
        
        color = "lightcoral" if is_del == 't' else "lightblue"
        dot_lines.append(
            f'  {path_name} [label="{label}", fillcolor="{color}"];'
        )
    
    for src, dst in edges:
        dot_lines.append(f'  {src} -> {dst};')
    
    sorted_levels = sorted(level_nodes.keys())
    
    for level in sorted_levels:
        dot_lines.extend([
            f'  subgraph cluster_{level} {{',
            f'    rank=same;',
            f'    style=rounded;',
            f'    color=lightgray;',
            f'    label="Level {level}";',
            f'    fontsize=16;',
            f'    fontname="bold";'
        ])
        
        for node in level_nodes[level]:
            dot_lines.append(f'    {node};')
        
        dot_lines.append('  }')
        dot_lines.append('')
    
    dot_lines.append("}")
    return "\n".join(dot_lines)

def generate_html_with_fixed_levels(data):
    
    dot_content = generate_dot_with_levels(data)
    
    with open("query_plan.dot", 'w') as f:
        f.write(dot_content)
    
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Query Plan Visualization</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }
        .container {
            display: flex;
            height: 100vh;
        }
        .levels {
            width: 100px;
            background-color: #f0f0f0;
            border-right: 1px solid #ccc;
            position: fixed;
            height: 100%;
            overflow: hidden;
        }
        .level-item {
            padding: 10px;
            text-align: center;
            font-weight: bold;
            border-bottom: 1px solid #ddd;
            background-color: #e0e0e0;
        }
        .graph-container {
            flex: 1;
            margin-left: 100px;
            overflow: auto;
        }
        .graph-wrapper {
            min-width: 1000px;
            min-height: 800px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="levels" id="levels">
        </div>
        <div class="graph-container">
            <div class="graph-wrapper">
                <img src="query_plan.png" alt="Query Plan" id="graph">
            </div>
        </div>
    </div>
    
    <script>
        function createLevels() {
            const levelsContainer = document.getElementById('levels');
            const levels = """ + str(sorted(list(set(int(row[0]) for row in data)))) + """;
            
            levels.forEach(level => {
                const levelDiv = document.createElement('div');
                levelDiv.className = 'level-item';
                levelDiv.textContent = `Level ${level}`;
                levelsContainer.appendChild(levelDiv);
            });
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            createLevels();
        });
    </script>
</body>
</html>
    """
    
    with open("query_plan.html", 'w') as f:
        f.write(html_content)

def main():
    if len(sys.argv) != 2:
        print("Usage: python query_visualizer.py <input.csv>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    data = read_csv(input_file)
    
    dot_content = generate_dot_with_levels(data)
    with open("query_plan.dot", 'w') as f:
        f.write(dot_content)
    
    print("DOT file generated: query_plan.dot")

if __name__ == "__main__":
    main()