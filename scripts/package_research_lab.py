"""Build the draft's downloadable course: self-contained code for day01..day14."""
import ast
import base64
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parent.parent
LAB = ROOT / "src/labs/research"
FILES = LAB / "files"
CLASSICAL_DAYS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 13, 14)


def cell(kind, source):
    result = {"id": hashlib.sha256((kind + source).encode()).hexdigest()[:12],
              "cell_type": kind, "metadata": {}, "source": source.splitlines(keepends=True)}
    if kind == "code":
        result.update(execution_count=None, outputs=[])
    return result


class SpecializeLesson(ast.NodeTransformer):
    """Retain the selected lesson's algorithm, rather than shipping all day branches."""
    def __init__(self, day):
        self.day = day
        self.model = "mlp" if day == 10 else "cnn"

    def visit_If(self, node):
        condition = ast.unparse(node.test)
        if self.day in CLASSICAL_DAYS and isinstance(node.test, ast.UnaryOp) and isinstance(node.test.op, ast.Not) and "args.neighbors" in condition and "args.labeled_fraction" in condition:
            bounds = {2: "args.alpha > 0", 4: "1 <= args.neighbors <= 20",
                      5: "1 <= args.depth <= 12", 6: "1 <= args.depth <= 12",
                      8: "2 <= args.clusters <= 8", 9: "2 <= args.components <= 13",
                      13: "1 <= args.neighbors <= 20 and 0.1 <= args.labeled_fraction <= 1",
                      14: "1 <= args.neighbors <= 20"}.get(self.day)
            return ast.parse(f"if not ({bounds}):\n    parser.error({('옵션 범위: ' + bounds)!r})").body[0] if bounds else None
        if re.fullmatch(r"args.day (==|!=) \d+", condition):
            operation = node.test.ops[0]
            matches = self.day == node.test.comparators[0].value
            if isinstance(operation, ast.NotEq):
                matches = not matches
            return self._visit_statements(node.body if matches else node.orelse)
        if condition == "name == 'mlp'":
            return self._visit_statements(node.body if self.model == "mlp" else node.orelse)
        return self.generic_visit(node)

    def _visit_statements(self, statements):
        result = []
        for statement in statements:
            visited = self.visit(statement)
            if isinstance(visited, list):
                result.extend(visited)
            elif visited is not None:
                result.append(visited)
        return result

    def visit_Expr(self, node):
        call = node.value
        if (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                and call.func.attr == "add_argument" and call.args):
            flag = call.args[0]
            if self.day in CLASSICAL_DAYS and isinstance(flag, ast.Constant):
                options = {2: {"--alpha"}, 4: {"--neighbors"}, 5: {"--depth"},
                           6: {"--depth"}, 8: {"--clusters"}, 9: {"--components"},
                           13: {"--neighbors", "--labeled-fraction"}, 14: {"--neighbors"}}
                if flag.value not in {"--day", "--seed", "--out"} | options.get(self.day, set()):
                    return None
            if isinstance(flag, ast.Constant) and flag.value in ("--day", "--model"):
                setting = f"day={self.day}" if flag.value == "--day" else f"model={self.model!r}"
                return ast.parse(f"parser.set_defaults({setting})").body[0]
            if isinstance(flag, ast.Constant) and flag.value in ("--out", "--data-dir"):
                value = "Path(__file__).resolve().parent / 'results'" if flag.value == "--out" else "Path(__file__).resolve().parents[1] / 'data'"
                for keyword in call.keywords:
                    if keyword.arg == "default":
                        keyword.value = ast.parse(value, mode="eval").body
        return self.generic_visit(node)

    def visit_Assign(self, node):
        if any(isinstance(target, ast.Name) and target.id == "output" for target in node.targets):
            return ast.parse("output = args.out or Path(__file__).resolve().parent / 'results'").body[0]
        return self.generic_visit(node)

    def visit_FunctionDef(self, node):
        node = self.generic_visit(node)
        for index, statement in enumerate(node.body):
            if isinstance(statement, ast.Return):
                node.body = node.body[:index + 1]
                break
        return node


def lesson_source(day):
    filename = "classical_lab.py" if day in CLASSICAL_DAYS else "train_cnn.py" if day in (10, 11) else "neo4j_lab.py"
    tree = SpecializeLesson(day).visit(ast.parse((FILES / filename).read_text(encoding="utf-8")))
    if day in (2, 8, 13):
        main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main")
        main.body = [node for node in main.body if not (isinstance(node, ast.Assign) and (
            ast.unparse(node).startswith(("wine = load_wine()", "X, y = (wine.data, wine.target)", "dataset = 'sklearn Wine"))
            or (day == 8 and ast.unparse(node).startswith("train, validation, test = split_indices"))))]
    # Discard reporting helpers unused by a particular lesson (e.g. classification in PCA).
    for _ in range(4):
        used_functions = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)}
        class Functions(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                return self.generic_visit(node) if node.name in used_functions else None
        tree = Functions().visit(tree)
    # Only keep imports that the specialized source actually uses.
    used = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)}
    class Imports(ast.NodeTransformer):
        def visit_ImportFrom(self, node):
            node.names = [alias for alias in node.names if (alias.asname or alias.name) in used]
            return node if node.names else None
        def visit_Import(self, node):
            node.names = [alias for alias in node.names if (alias.asname or alias.name.split('.')[0]) in used]
            return node if node.names else None
    tree = Imports().visit(tree)
    tree.body[0] = ast.Expr(value=ast.Constant(value=f"Day {day:02} 실습. 실행: python day{day:02}/lab.py"))
    ast.fix_missing_locations(tree)
    code = ast.unparse(tree) + "\n"
    compile(code, f"day{day:02}/lab.py", "exec")
    return code


def lesson_notebook(day, source, title):
    torch_day = day in (10, 11)
    packages = ["torch>=2.6,<3", "torchvision>=0.21,<1"] if torch_day else ["numpy>=1.26,<3", "scikit-learn>=1.6,<2", "matplotlib>=3.9,<4"]
    modules = ("torch", "torchvision") if torch_day else ("numpy", "sklearn", "matplotlib")
    install = f'''import importlib.util, subprocess, sys
if any(importlib.util.find_spec(name) is None for name in {modules!r}):
    command = [sys.executable, "-m", "pip", "install", *{packages!r}]
'''
    if torch_day:
        install += '    if sys.platform != "darwin": command += ["--index-url", "https://download.pytorch.org/whl/cpu"]\n'
    install += "    subprocess.check_call(command)\n"
    definition = source.rsplit("if __name__ == '__main__':", 1)[0]
    arguments = '["--epochs", "2", "--data-dir", str(Path.cwd() / "data")]' if torch_day else "[]"
    return {"nbformat": 4, "nbformat_minor": 5,
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
            "cells": [cell("markdown", f"# {title}\nCPU 실행. 결과는 `results/`에 저장. 개념과 비교 항목은 같은 폴더의 README.md 참고.\n"),
                      cell("code", install), cell("code", definition),
                      cell("code", f'__file__ = str(Path.cwd() / "lab.py")\nresult = main({arguments})\n'),
                      cell("code", 'from IPython.display import HTML, display, FileLink\nfolder = Path("results")\ndisplay(HTML((folder / "report.html").read_text(encoding="utf-8")))\ndisplay(FileLink(str(folder / "metrics.csv")))\ndisplay(FileLink(str(folder / "results.json")))\n')]}


def cypher_files(graph):
    def quote(value):
        return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"
    lab = quote(graph["labId"])
    seed = ["// ResearchLab 데이터 생성"]
    for node in graph["nodes"]:
        seed.append(f"MERGE (n:ResearchLab:{node['label']} {{lab_id: {lab}, id: {quote(node['id'])}}}) SET n.name = {quote(node['name'])};")
    for edge in graph["edges"]:
        seed.append("MATCH (a:ResearchLab {lab_id: %s, id: %s}), (b:ResearchLab {lab_id: %s, id: %s}) MERGE (a)-[:%s]->(b);" % (lab, quote(edge["source"]), lab, quote(edge["target"]), edge["type"]))
    spec = importlib.util.spec_from_file_location("neo4j_lab_source", FILES / "neo4j_lab.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    queries = "// Neo4j Browser에서 한 문장씩 실행\n\n" + "\n\n".join(f"// {name}\n{query.replace('$lab', lab)};" for name, query in module.QUERIES.items()) + "\n"
    return {"seed.cypher": "\n".join(seed) + "\n", "queries.cypher": queries}


def archive_inputs():
    article = (ROOT / "src/content/posts/ResearchLab/ResearchLab.md").read_text(encoding="utf-8")
    curriculum = article.split("<!-- curriculum:start -->", 1)[1].split("<!-- curriculum:end -->", 1)[0].strip() + "\n"
    inputs = {name: (FILES / name).read_bytes() for name in ("README.md", "experiment-log.md", "requirements-ml.txt", "requirements-cnn.txt", "requirements-neo4j.txt")}
    inputs["curriculum.md"] = curriculum.encode()
    headings = list(re.finditer(r"^### (\d+)일 · (.+)$", curriculum, re.MULTILINE))
    if [int(item[1]) for item in headings] != list(range(1, 15)):
        raise ValueError("커리큘럼에 1~14일 설명이 순서대로 필요합니다")
    for index, heading in enumerate(headings):
        day = int(heading[1])
        folder = f"day{day:02}"
        end = headings[index + 1].start() if index + 1 < len(headings) else curriculum.find("### 실행 결과", heading.end())
        if end == -1:
            end = len(curriculum)
        guide = curriculum[heading.start():end].strip()
        inputs[f"{folder}/README.md"] = (f"# {heading[0][4:]}\n\n명령은 압축을 푼 `research-lab` 폴더 기준. 결과는 `{folder}/results/`에 저장.\n\n" + guide.split("\n", 1)[1].lstrip() + "\n").encode()
        source = lesson_source(day)
        inputs[f"{folder}/lab.py"] = source.encode()
        requirement = "requirements-cnn.txt" if day in (10, 11) else "requirements-neo4j.txt" if day == 12 else "requirements-ml.txt"
        inputs[f"{folder}/requirements.txt"] = (FILES / requirement).read_bytes()
        if day != 12:
            inputs[f"{folder}/lab.ipynb"] = json.dumps(lesson_notebook(day, source, heading[0][4:]), ensure_ascii=False, indent=2).encode()
    graph = json.loads((LAB / "graph-data.json").read_text())
    inputs["day12/graph.json"] = (LAB / "graph-data.json").read_bytes()
    for name in ("compose.yaml", ".env.example"):
        inputs[f"day12/{name}"] = (FILES / name).read_bytes()
    inputs.update({f"day12/{name}": source.encode() for name, source in cypher_files(graph).items()})
    return inputs


def build():
    inputs = archive_inputs()
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(inputs.items()):
            entry = zipfile.ZipInfo("research-lab/" + name, date_time=(2026, 3, 20, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, content)
    data = output.getvalue()
    manifest = {"filename": "research-lab.zip", "sha256": hashlib.sha256(data).hexdigest(),
                "files": [{"name": name, "sha256": hashlib.sha256(content).hexdigest()} for name, content in sorted(inputs.items())],
                "base64": base64.b64encode(data).decode()}
    (LAB / "bundle.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Packaged {len(inputs)} files, {len(data)} bytes, SHA-256 {manifest['sha256']}")


if __name__ == "__main__":
    build()
