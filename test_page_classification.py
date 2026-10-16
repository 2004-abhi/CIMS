import ast
import json
from pathlib import Path

source = Path("build_semester_index.py").read_text(encoding="utf-8")
tree = ast.parse(source)

function_node = next(
    node for node in tree.body
    if isinstance(node, ast.FunctionDef)
    and node.name == "classify_page"
)

module = ast.Module(body=[function_node], type_ignores=[])
namespace = {"re": __import__("re")}
exec(compile(module, "classify_page_test", "exec"), namespace)
classify_page = namespace["classify_page"]

targets = {555, 714, 759, 770, 784, 810, 1086}

with Path("data/pdf_full_text.jsonl").open(encoding="utf-8") as f:
    for line in f:
        record = json.loads(line)
        if record["pdf_page"] in targets:
            print(
                f'Page {record["pdf_page"]}: '
                f'{classify_page(record.get("text", ""))}'
            )
