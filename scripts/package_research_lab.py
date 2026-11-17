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


def cell(kind, text):
    result = {"id": hashlib.sha256((kind + text).encode()).hexdigest()[:12],
              "cell_type": kind, "metadata": {}, "source": text.splitlines(keepends=True)}
    if kind == "code": result.update(execution_count=None, outputs=[])
    return result


def notebook():
    code = (FILES / "train_cnn.py").read_text(encoding="utf-8").split('\nif __name__ == "__main__":')[0]
    return {
        "nbformat": 4, "nbformat_minor": 5,
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": "3.11"}},
        "cells": [
            cell("markdown", "# MLP/CNN 손글씨 분류 실습\nCPU로 MNIST 일부를 학습합니다. 코드는 이 노트북에 모두 포함되어 있습니다.\n먼저 설치 확인, 코드 정의, 학습, 보고서 순서로 실행합니다. GPU는 필요하지 않습니다.\n"),
            cell("code", 'import importlib.util, subprocess, sys\nif any(importlib.util.find_spec(name) is None for name in ("torch", "torchvision")):\n    command = [sys.executable, "-m", "pip", "install", "torch>=2.6,<3", "torchvision>=0.21,<1"]\n    if sys.platform != "darwin": command += ["--index-url", "https://download.pytorch.org/whl/cpu"]\n    subprocess.check_call(command)\n'),
            cell("code", code),
            cell("code", 'result = main(["--model", "cnn", "--epochs", "1", "--train-limit", "2000", "--test-limit", "500", "--out", "results/cnn"])\n'),
            cell("code", 'from IPython.display import HTML, display, FileLink\ndisplay(HTML(Path("results/cnn/report.html").read_text(encoding="utf-8")))\ndisplay(FileLink("results/cnn/metrics.csv"))\ndisplay(FileLink("results/cnn/results.json"))\n'),
            cell("markdown", "## 다음 실험\n10일차에는 학습 셀의 `cnn`을 `mlp`로 바꾸고 `--out`을 `results/mlp`로 바꿉니다. 11일차에는 CNN을 실행합니다.\n같은 데이터 수·seed로 validation loss·정확도·오분류를 비교합니다. 기본 실행은 test를 평가하지 않습니다.\n조건을 확정한 뒤 선택 모델의 인자에 `--evaluate-test`를 추가해 마지막에만 test를 확인합니다.\nColab에서는 Files 패널 또는 링크로 결과를 내려받습니다.\n"),
        ],
    }


def classical_notebook():
    book = notebook()
    code = (FILES / "classical_lab.py").read_text(encoding="utf-8").split('\nif __name__ == "__main__":')[0]
    book["cells"] = [
        cell("markdown", "# 2주 실습: 머신러닝 기초\n1~9일, 13~14일 코드를 포함합니다. `DAY`를 바꾸어 해당 날짜를 실행합니다.\n10~11일은 cnn_lab.ipynb, 12일은 Neo4j 준비 안내를 사용합니다. 날짜별 목표와 과제는 curriculum.md에 있습니다.\nCPU만 사용하며 설치 후 추가 데이터 다운로드는 없습니다. 마지막 14일차만 최종 test를 평가합니다.\n"),
        cell("code", 'import importlib.util, subprocess, sys\nif any(importlib.util.find_spec(name) is None for name in ("sklearn", "matplotlib", "numpy")):\n    subprocess.check_call([sys.executable, "-m", "pip", "install", "scikit-learn>=1.6,<2", "matplotlib>=3.9,<4", "numpy>=1.26,<3"])\n'),
        cell("code", code),
        cell("code", 'DAY = 1  # 1..9, 13, 14 중 선택\nresult = main(["--day", str(DAY)])\n'),
        cell("code", 'from IPython.display import HTML, display, FileLink\nfolder = Path(f"results/day{DAY:02}")\ndisplay(HTML((folder / "report.html").read_text(encoding="utf-8")))\ndisplay(FileLink(str(folder / "metrics.csv")))\ndisplay(FileLink(str(folder / "plot.png")))\n'),
        cell("markdown", "## 조건 바꾸기\n예: `main([\"--day\", \"4\", \"--neighbors\", \"9\", \"--out\", \"results/day04-k9\"])`\n같은 폴더는 덮어씁니다. 바꾼 조건과 결과는 experiment-log.md에 적고 Colab 세션 종료 전에 내려받습니다.\n"),
    ]
    return book


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
    inputs["ml_basics.ipynb"] = json.dumps(classical_notebook(), ensure_ascii=False, indent=2).encode()
    article = (ROOT / "src/content/posts/ResearchLab/ResearchLab.md").read_text(encoding="utf-8")
    inputs["curriculum.md"] = article.split("<!-- curriculum:start -->", 1)[1].split("<!-- curriculum:end -->", 1)[0].strip().encode() + b"\n"
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
