import csv
import sys
from collections import defaultdict

def read_csv(file_path):
    data = []
    with open(file_path, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            # Преобразуем пустые строки в None и обрабатываем массивы
            processed_row = []
            for item in row:
                if item == '\\N':
                    processed_row.append(None)
                elif item.startswith('{') and item.endswith('}'):
                    # Обрабатываем массивы, удаляя фигурные скобки
                    processed_row.append(item[1:-1].split(','))
                else:
                    processed_row.append(item)
            data.append(processed_row)
    return data

def generate_dot(data):
    dot_lines = [
        "digraph query_plan {",
        "  rankdir=TB;  // Направление графа снизу вверх",
        "  nodesep=0.5;",
        "  ranksep=0.5;",
        "  node [shape=box, style=\"rounded,filled\", fillcolor=\"lightblue\"];",
        "",
    ]
    
    # Собираем все узлы и связи
    nodes = set()
    edges = set()
    level_nodes = defaultdict(list)

    for row in data:
        level, path_name, path_type, child_paths, startup_cost, total_cost, rows, is_del = row

        nodes.add(path_name)
        level_nodes[int(level)].append(path_name)
        
        if child_paths:
            for child in child_paths:
                edges.add((child.strip(), path_name))

    
    # Добавляем узлы с атрибутами
    for row in data:
        level, path_name, path_type, child_paths, startup_cost, total_cost, rows, is_del = row
        
        # is join path
        if child_paths and len(child_paths) == 2:
            label = (
                f"{path_name}({child_paths[0].strip()}⋈{child_paths[1].strip()})\\n"
                f"Type: {path_type}\\n"
                f"Cost: {startup_cost}..{total_cost}\\n"
                f"Rows: {rows}"
            )
        else:
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
    
    # Добавляем связи
    for src, dst in edges:
        dot_lines.append(f'  {src} -> {dst};')
    
    # Упорядочиваем узлы по уровням
    max_level = max(level_nodes.keys())
    for level in sorted(level_nodes.keys()):
        same_rank = " ".join(f'"{node}";' for node in level_nodes[level])
        dot_lines.append(f'  {{ rank=same; level_{level} [shape=plaintext, label="Level {level}", fillcolor=none]; {same_rank} }}')
    
    dot_lines.append("}")
    return "\n".join(dot_lines)

def main():
    if len(sys.argv) != 2:
        print("Usage: python query_visualizer.py <input.csv>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = "query_plan.dot"
    
    data = read_csv(input_file)
    dot_content = generate_dot(data)
    
    with open(output_file, 'w') as f:
        f.write(dot_content)
    
    print(f"DOT file generated: {output_file}")
    print("You can render it with Graphviz using:")
    print(f"dot -Tpng {output_file} -o query_plan.png")

if __name__ == "__main__":
    main()
