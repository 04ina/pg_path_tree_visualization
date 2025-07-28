# Визуализация дерева путей SQL запроса для СУБД PostgreSQL

## Как пользоваться 
  
1. Получаем csv дамп таблицы ee_result, сгенерированной с помощью расширенияя [extended_explain]():
```bash
 COPY ee_result TO '/directory/file.csv';
```
2. С помощью скрипта pg_path_tree_visualization.py генерируем dot файл query_plan.dot
```bash
python3 pg_path_tree_visualization.py /directory/file.csv
```
3. Генерируем svg файл с помощью [graphviz](https://graphviz.org/)
```bash
dot -Tsvg query_plan.dot > output.svg
```
4. Запускаем svg файл в браузере
```bash
firefox output.svg
```