"""Build a deterministic, browser-downloadable ZIP without publishing public assets."""
import base64
import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent.parent
LAB = ROOT / "src/labs/research"
FILES = LAB / "files"


def notebook():
    code = (FILES / "train_cnn.py").read_text(encoding="utf-8").split('\nif __name__ == "__main__":')[0]
    def cell(kind, text):
        result = {"cell_type": kind, "metadata": {}, "source": text.splitlines(keepends=True)}
        if kind == "code": result.update(execution_count=None, outputs=[])
        return result
    return {
        "nbformat": 4, "nbformat_minor": 5,
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": "3.11"}},
        "cells": [
            cell("markdown", "# MLP/CNN 손글씨 분류 실습\nCPU로 MNIST 일부를 학습합니다. 코드는 이 노트북에 모두 포함되어 있습니다.\n먼저 설치 확인, 코드 정의, 학습, 보고서 순서로 실행합니다. GPU는 필요하지 않습니다.\n"),
            cell("code", 'import importlib.util, subprocess, sys\nif any(importlib.util.find_spec(name) is None for name in ("torch", "torchvision")):\n    command = [sys.executable, "-m", "pip", "install", "torch>=2.6,<3", "torchvision>=0.21,<1"]\n    if sys.platform != "darwin": command += ["--index-url", "https://download.pytorch.org/whl/cpu"]\n    subprocess.check_call(command)\n'),
            cell("code", code),
            cell("code", 'result = main(["--model", "cnn", "--epochs", "1", "--train-limit", "2000", "--test-limit", "500", "--out", "results/cnn"])\n'),
            cell("code", 'from IPython.display import HTML, display, FileLink\ndisplay(HTML(Path("results/cnn/report.html").read_text(encoding="utf-8")))\ndisplay(FileLink("results/cnn/metrics.csv"))\ndisplay(FileLink("results/cnn/results.json"))\n'),
            cell("markdown", "## 다음 실험\n학습 셀의 `cnn`을 `mlp`로 바꾸고 `--out`을 `results/mlp`로 바꿉니다.\n같은 데이터 수·seed로 비교하고 정확도뿐 아니라 loss와 오분류 이미지도 확인합니다.\nColab에서는 Files 패널 또는 링크로 결과를 내려받습니다.\n"),
        ],
    }


def cypher_files(graph):
    def quote(value): return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"
    lab = quote(graph["labId"])
    seed = ["// 연구실 실습 데이터만 생성합니다. 기존 전체 DB를 삭제하지 않습니다."]
    for node in graph["nodes"]:
        seed.append(f"MERGE (n:ResearchLab:{node['label']} {{lab_id: {lab}, id: {quote(node['id'])}}}) SET n.name = {quote(node['name'])};")
    for edge in graph["edges"]:
        seed.append("MATCH (a:ResearchLab {lab_id: %s, id: %s}), (b:ResearchLab {lab_id: %s, id: %s}) MERGE (a)-[:%s]->(b);" % (lab, quote(edge["source"]), lab, quote(edge["target"]), edge["type"]))
    import importlib.util
    spec = importlib.util.spec_from_file_location("neo4j_lab_source", FILES / "neo4j_lab.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    queries = "// Neo4j Browser에서 한 문장씩 선택해 실행합니다.\n\n" + "\n\n".join(f"// {name}\n{query.replace('$lab', lab)};" for name, query in module.QUERIES.items()) + "\n"
    return {"seed.cypher": "\n".join(seed) + "\n", "queries.cypher": queries}


def build():
    graph = json.loads((LAB / "graph-data.json").read_text(encoding="utf-8"))
    inputs = {path.name: path.read_bytes() for path in FILES.iterdir() if path.is_file()}
    inputs["graph.json"] = (LAB / "graph-data.json").read_bytes()
    inputs["cnn_lab.ipynb"] = json.dumps(notebook(), ensure_ascii=False, indent=2).encode()
    inputs.update({name: content.encode() for name, content in cypher_files(graph).items()})
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
