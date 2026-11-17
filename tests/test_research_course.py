"""CPU integration checks; install the ZIP's requirements-ml.txt and requirements-cnn.txt first."""
import contextlib
import base64
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import subprocess
import sys
import zipfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
CACHE = tempfile.TemporaryDirectory(prefix="research-course-mpl-")
os.environ.setdefault("MPLCONFIGDIR", CACHE.name)


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "src/labs/research/files" / f"{name}.py")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class CourseTests(unittest.TestCase):
    def test_downloaded_daily_scripts_are_standalone_and_save_locally(self):
        manifest = json.loads((ROOT / "src/labs/research/bundle.json").read_text())
        archive = zipfile.ZipFile(io.BytesIO(base64.b64decode(manifest["base64"])))
        self.assertIsNone(archive.testzip())
        for entry in manifest["files"]:
            self.assertEqual(hashlib.sha256(archive.read("research-lab/" + entry["name"])).hexdigest(), entry["sha256"])
        with tempfile.TemporaryDirectory() as extracted, tempfile.TemporaryDirectory() as outside:
            archive.extractall(extracted)
            root = Path(extracted) / "research-lab"
            for day in range(1, 15):
                directory = root / f"day{day:02}"
                arguments = [sys.executable, str(directory / "lab.py")]
                if day == 12:
                    # Database integration is separate. CLI parsing requires no active DB.
                    arguments += ["--help"]
                elif day in (10, 11):
                    arguments += ["--dataset", "synthetic", "--epochs", "1", "--train-limit", "64",
                                  "--validation-limit", "32", "--test-limit", "16"]
                completed = subprocess.run(arguments, cwd=outside, capture_output=True, text=True)
                self.assertEqual(completed.returncode, 0, f"day{day:02}: {completed.stderr}")
                if day == 12:
                    continue
                result = json.loads((directory / "results/results.json").read_text())
                self.assertEqual(result["test_evaluated"], day == 14)
                if day in (10, 11):
                    self.assertEqual(result["model"], "mlp" if day == 10 else "cnn")
                else:
                    self.assertEqual(result["day"], day)
                self.assertTrue((directory / "results/report.html").is_file())
            self.assertFalse((Path(outside) / "results").exists())
            self.assertNotIn("Conv2d", (root / "day10/lab.py").read_text())
            self.assertNotIn("KMeans", (root / "day03/lab.py").read_text())
            self.assertNotIn("--day", (root / "day03/lab.py").read_text())
            self.assertNotIn("--model", (root / "day10/lab.py").read_text())

    def test_notebooks_embed_complete_daily_code(self):
        manifest = json.loads((ROOT / "src/labs/research/bundle.json").read_text())
        archive = zipfile.ZipFile(io.BytesIO(base64.b64decode(manifest["base64"])))
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stdout(io.StringIO()):
            for day in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14]:
                book = json.loads(archive.read(f"research-lab/day{day:02}/lab.ipynb"))
                namespace = {"__name__": "notebook"}
                for index, cell in enumerate(book["cells"]):
                    if cell["cell_type"] == "code":
                        compile("".join(cell["source"]), f"day{day}:cell{index}", "exec")
                exec("".join(book["cells"][2]["source"]), namespace)
                output = Path(folder) / f"day{day:02}"
                namespace["__file__"] = str(output / "lab.py")
                arguments = []
                if day in (10, 11):
                    arguments = ["--dataset", "synthetic", "--epochs", "1", "--train-limit", "32", "--validation-limit", "16", "--test-limit", "16"]
                result = namespace["main"](arguments)
                self.assertTrue((output / "results/report.html").is_file())
                self.assertEqual(result["test_evaluated"], day == 14)

    def test_split_is_disjoint_stratified_and_reproducible(self):
        import numpy as np
        lab = module("classical_lab")
        labels = np.arange(300) % 3
        first = lab.split_indices(labels)
        again = lab.split_indices(labels)
        self.assertEqual([len(part) for part in first], [180, 60, 60])
        self.assertEqual(len(set().union(*map(set, first))), 300)
        for i, part in enumerate(first):
            np.testing.assert_array_equal(part, again[i])
            self.assertEqual(set(labels[part]), {0, 1, 2})
            for other in first[i + 1:]:
                self.assertFalse(set(part) & set(other))

    def test_all_classical_days_and_final_selection(self):
        lab = module("classical_lab")
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stdout(io.StringIO()):
            for day in [1, 2, 3, 4, 5, 6, 7, 8, 9, 13, 14]:
                out = Path(folder) / str(day)
                result = lab.main(["--day", str(day), "--out", str(out)])
                self.assertEqual(result["test_evaluated"], day == 14)
                self.assertTrue((out / "plot.png").read_bytes().startswith(b"\x89PNG"))
                self.assertIn("data:image/png;base64,", (out / "report.html").read_text())
                for name in ["metrics.csv", "predictions.csv", "results.json", "split.json"]:
                    self.assertGreater((out / name).stat().st_size, 0)
                if day == 8:
                    self.assertEqual(result["split_counts"], {"exploration": 300})
                    self.assertTrue(-1 <= result["metrics"][0]["silhouette"] <= 1)
                if day == 13:
                    self.assertEqual(result["metrics"][0]["labeled_train"], 36)
                    self.assertEqual(result["metrics"][0]["unlabeled_train"], 144)
                if day == 14:
                    cv = result["metrics"][:-1]
                    winner = max(cv, key=lambda row: row["macro_f1"])["model"]
                    self.assertEqual(result["selected_model"], winner)
                    self.assertEqual(result["metrics"][-1]["model"], winner)
                    self.assertEqual(result["metrics"][-1]["split"], "final test")

    def test_semi_supervised_never_fits_validation_or_hidden_labels(self):
        import numpy as np
        from sklearn.semi_supervised import LabelSpreading
        lab = module("classical_lab")
        original = LabelSpreading.fit
        calls = []
        def inspect(estimator, X, y):
            calls.append((X.copy(), y.copy()))
            return original(estimator, X, y)
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stdout(io.StringIO()), patch.object(LabelSpreading, "fit", inspect):
            lab.main(["--day", "13", "--out", folder])
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0].shape, (180, 2))
        self.assertEqual(int(np.sum(calls[0][1] == -1)), 144)

    def test_pytorch_uses_validation_until_final_test_requested(self):
        lab = module("train_cnn")
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stdout(io.StringIO()):
            for model in ["mlp", "cnn"]:
                for final in [False, True]:
                    arguments = ["--model", model, "--dataset", "synthetic", "--epochs", "1",
                                 "--train-limit", "64", "--validation-limit", "32", "--test-limit", "16", "--out", folder]
                    if final:
                        arguments.append("--evaluate-test")
                    # Count evaluations, including the reported data source for image predictions.
                    with patch.object(lab, "evaluate", wraps=lab.evaluate) as evaluate:
                        result = lab.main(arguments)
                        self.assertEqual(evaluate.call_count, 2 if final else 1)
                        self.assertEqual(len(evaluate.call_args.args[2].dataset), 16 if final else 32)
                    self.assertEqual(result["test_evaluated"], final)
                    self.assertEqual(result["prediction_split"], "test" if final else "validation")
                    self.assertIn("validation_loss", result["metrics"][0])
                    self.assertNotIn("test_loss", result["metrics"][0])
                    self.assertEqual(result["final_test"] is not None, final)
                    self.assertGreater((Path(folder) / "weights.pt").stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
