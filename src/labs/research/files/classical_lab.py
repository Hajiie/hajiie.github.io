"""2주 과정의 scikit-learn 실습. 예: python classical_lab.py --day 4"""
import argparse
import base64
import csv
import html
import json
from pathlib import Path


def split_indices(y, seed=7, stratified=True):
    """먼저 test 20%를 보관하고 나머지를 train 60% / validation 20%로 나눕니다."""
    import numpy as np
    from sklearn.model_selection import train_test_split
    indices = np.arange(len(y))
    pool, test = train_test_split(indices, test_size=0.2, random_state=seed,
                                  stratify=y if stratified else None)
    train, validation = train_test_split(pool, test_size=0.25, random_state=seed,
                                         stratify=y[pool] if stratified else None)
    return train, validation, test


def scaled(model):
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    return make_pipeline(StandardScaler(), model)


def classify(name, model, X, y, train, validation):
    from sklearn.metrics import accuracy_score, f1_score
    model.fit(X[train], y[train])
    predicted = model.predict(X[validation])
    row = {"model": name, "split": "validation",
           "train_accuracy": accuracy_score(y[train], model.predict(X[train])),
           "accuracy": accuracy_score(y[validation], predicted),
           "macro_f1": f1_score(y[validation], predicted, average="macro", zero_division=0)}
    return row, predicted


def write_csv(path, rows):
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--day", type=int, choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 13, 14], required=True)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--neighbors", type=int, default=5)
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--clusters", type=int, default=3)
    parser.add_argument("--components", type=int, default=2)
    parser.add_argument("--alpha", type=float, default=10.0, help="Ridge의 규제 강도")
    parser.add_argument("--labeled-fraction", type=float, default=0.2)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    if not (1 <= args.neighbors <= 20 and 1 <= args.depth <= 12 and 2 <= args.clusters <= 8
            and 2 <= args.components <= 13 and args.alpha > 0 and 0.1 <= args.labeled_fraction <= 1):
        parser.error("neighbors 1..20, depth 1..12, clusters 2..8, components 2..13, alpha > 0, labeled-fraction 0.1..1")
    import numpy as np
    import sklearn
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.datasets import load_wine, make_blobs, make_moons, make_regression
    from sklearn.dummy import DummyClassifier, DummyRegressor
    from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
    from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
    from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, mean_squared_error, r2_score
    from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.svm import SVC
    from sklearn.tree import DecisionTreeClassifier

    output = args.out or Path(f"results/day{args.day:02}")
    output.mkdir(parents=True, exist_ok=True)
    wine = load_wine()
    X, y = wine.data, wine.target
    dataset = "sklearn Wine: 178 samples, 13 features, 3 classes"
    if args.day == 2:
        X, y = make_regression(n_samples=300, n_features=8, n_informative=4, noise=25, random_state=args.seed)
        dataset = "synthetic linear regression with noise"
    if args.day == 13:
        X, y = make_moons(n_samples=300, noise=0.15, random_state=args.seed)
        dataset = "synthetic two moons"
    train, validation, test = split_indices(y, args.seed, stratified=args.day != 2)
    rows, predictions, notes = [], [], []
    selected_model = None
    figure, axis = plt.subplots(figsize=(7, 4.5), layout="constrained")

    def record_predictions(name, predicted, indices=validation):
        predictions.extend({"model": name, "sample_id": int(i), "actual": float(y[i]),
                            "predicted": float(p)} for i, p in zip(indices, predicted))

    def comparison(models):
        for name, model in models:
            row, predicted = classify(name, model, X, y, train, validation)
            rows.append(row)
            record_predictions(name, predicted)
        positions = np.arange(len(rows))
        axis.bar(positions - 0.18, [r["train_accuracy"] for r in rows], width=0.36, label="train accuracy")
        axis.bar(positions + 0.18, [r["accuracy"] for r in rows], width=0.36, label="validation accuracy")
        axis.set_xticks(positions, [r["model"] for r in rows], rotation=15)
        axis.set_ylim(0, 1.05)
        axis.legend()

    if args.day == 1:
        comparison([("majority baseline", DummyClassifier(strategy="most_frequent"))])
        notes.append("X.shape=(178,13), y.shape=(178,). 비교 기준은 다수 클래스만 고르는 baseline입니다.")
    elif args.day == 2:
        for name, model in [("mean baseline", DummyRegressor()), ("linear", LinearRegression()),
                            ("ridge", scaled(Ridge(alpha=args.alpha)))]:
            model.fit(X[train], y[train])
            predicted = model.predict(X[validation])
            rows.append({"model": name, "split": "validation", "mae": mean_absolute_error(y[validation], predicted),
                         "rmse": float(np.sqrt(mean_squared_error(y[validation], predicted))),
                         "r2": r2_score(y[validation], predicted)})
            record_predictions(name, predicted)
            axis.scatter(y[validation], predicted, alpha=0.6, label=name)
        low, high = float(y[validation].min()), float(y[validation].max())
        axis.plot([low, high], [low, high], linestyle="--", color="gray")
        axis.set(xlabel="Actual", ylabel="Predicted")
        axis.legend()
        notes.append("MAE·RMSE는 작을수록 좋습니다. Ridge는 alpha로 가중치 크기를 제한합니다.")
    elif args.day == 3:
        comparison([("baseline", DummyClassifier(strategy="most_frequent")),
                    ("logistic", scaled(LogisticRegression(max_iter=2000)))])
        notes.append("로지스틱 회귀는 분류 모델입니다. 정확도와 클래스별 F1을 평균한 macro F1을 함께 봅니다.")
    elif args.day == 4:
        comparison([("raw kNN", KNeighborsClassifier(n_neighbors=args.neighbors)),
                    ("scaled kNN", scaled(KNeighborsClassifier(n_neighbors=args.neighbors))),
                    ("scaled SVM", scaled(SVC(C=1, kernel="rbf")))])
        notes.append("단위가 다른 특성의 거리 영향을 비교합니다. scaler는 학습 데이터에만 fit합니다.")
    elif args.day == 5:
        comparison([("shallow tree", DecisionTreeClassifier(max_depth=args.depth, random_state=args.seed)),
                    ("unlimited tree", DecisionTreeClassifier(random_state=args.seed))])
        notes.append("train과 validation의 차이를 확인합니다. 작은 데이터에서는 깊은 트리도 높은 검증 점수를 낼 수 있습니다.")
    elif args.day == 6:
        comparison([("single tree", DecisionTreeClassifier(max_depth=args.depth, random_state=args.seed)),
                    ("random forest", RandomForestClassifier(n_estimators=80, max_depth=args.depth, random_state=args.seed, n_jobs=1)),
                    ("boosting", GradientBoostingClassifier(n_estimators=60, max_depth=2, random_state=args.seed))])
        notes.append("Random Forest는 여러 트리를 결합하고, boosting은 이전 오차를 줄이는 모델을 순차적으로 더합니다.")
    elif args.day == 7:
        cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=args.seed)
        search = GridSearchCV(scaled(KNeighborsClassifier()), {"kneighborsclassifier__n_neighbors": [3, 5, 9]},
                              cv=cv, scoring="f1_macro", n_jobs=1)
        search.fit(X[train], y[train])
        for params, mean, std in zip(search.cv_results_["params"], search.cv_results_["mean_test_score"], search.cv_results_["std_test_score"]):
            rows.append({"model": f"kNN k={params['kneighborsclassifier__n_neighbors']}", "split": "train CV", "macro_f1": mean, "cv_std": std})
        predicted = search.predict(X[validation])
        rows.append({"model": "CV-selected kNN", "split": "validation", "accuracy": accuracy_score(y[validation], predicted),
                     "macro_f1": f1_score(y[validation], predicted, average="macro")})
        record_predictions("CV-selected kNN", predicted)
        axis.bar([r["model"] for r in rows[:3]], [r["macro_f1"] for r in rows[:3]], yerr=[r["cv_std"] for r in rows[:3]])
        axis.set_ylabel("Train cross-validation macro F1")
        notes.append(f"선택 조건: {search.best_params_}. Pipeline 내부에서 fold마다 scaler를 다시 fit합니다.")
    elif args.day == 8:
        from sklearn.cluster import KMeans
        from sklearn.metrics import silhouette_score
        X, _ = make_blobs(n_samples=300, centers=3, cluster_std=1.2, random_state=args.seed)
        dataset = "synthetic blobs; labels are not supplied to KMeans"
        clusters = KMeans(n_clusters=args.clusters, n_init=10, random_state=args.seed).fit(X)
        rows.append({"model": "k-means", "split": "exploration, all 300 points", "clusters": args.clusters,
                     "silhouette": silhouette_score(X, clusters.labels_), "inertia": clusters.inertia_})
        predictions = [{"sample_id": i, "x": float(point[0]), "y": float(point[1]), "cluster": int(label)}
                       for i, (point, label) in enumerate(zip(X, clusters.labels_))]
        axis.scatter(X[:, 0], X[:, 1], c=clusters.labels_, cmap="viridis", s=24)
        axis.scatter(clusters.cluster_centers_[:, 0], clusters.cluster_centers_[:, 1], marker="X", c="red", s=100)
        notes.append("군집 번호는 정답 라벨이 아닙니다. silhouette는 거리 기반 분리 정도이며 도메인 의미를 보장하지 않습니다.")
    elif args.day == 9:
        from sklearn.decomposition import PCA
        reducer = scaled(PCA(n_components=args.components))
        reducer.fit(X[train])
        projected = reducer.transform(X[validation])
        ratio = reducer.named_steps["pca"].explained_variance_ratio_
        rows.extend({"component": i + 1, "explained_variance_ratio": float(value)} for i, value in enumerate(ratio))
        predictions = [{"sample_id": int(i), "pc1": float(point[0]), "pc2": float(point[1]), "label_for_display": int(y[i])}
                       for i, point in zip(validation, projected)]
        axis.scatter(projected[:, 0], projected[:, 1], c=y[validation], cmap="viridis")
        axis.set(xlabel="PC1", ylabel="PC2")
        notes.append(f"누적 설명 분산: {sum(ratio):.3f}. PCA는 라벨 없이 분산 방향을 찾습니다. 색은 결과 해석용입니다.")
    elif args.day == 13:
        from sklearn.preprocessing import StandardScaler
        from sklearn.semi_supervised import LabelSpreading
        rng = np.random.default_rng(args.seed)
        observed = np.full(len(train), -1)
        for label in np.unique(y[train]):
            candidates = np.flatnonzero(y[train] == label)
            chosen = rng.choice(candidates, max(1, int(len(candidates) * args.labeled_fraction)), replace=False)
            observed[chosen] = label
        known = observed != -1
        scaler = StandardScaler().fit(X[train])
        train_scaled, validation_scaled = scaler.transform(X[train]), scaler.transform(X[validation])
        models = [("labeled-only logistic", LogisticRegression(max_iter=2000), train_scaled[known], observed[known]),
                  ("label spreading", LabelSpreading(kernel="knn", n_neighbors=args.neighbors, max_iter=100), train_scaled, observed)]
        for name, model, data, labels in models:
            model.fit(data, labels)
            predicted = model.predict(validation_scaled)
            rows.append({"model": name, "split": "validation", "labeled_train": int(known.sum()),
                         "unlabeled_train": int((~known).sum()), "accuracy": accuracy_score(y[validation], predicted),
                         "macro_f1": f1_score(y[validation], predicted, average="macro")})
            record_predictions(name, predicted)
        axis.scatter(train_scaled[~known, 0], train_scaled[~known, 1], c="lightgray", label="unlabeled train")
        axis.scatter(train_scaled[known, 0], train_scaled[known, 1], c=observed[known], cmap="viridis", edgecolors="black", label="labeled train")
        axis.legend()
        notes.append("학습 집합 안에서만 라벨 일부를 숨깁니다. validation/test 특성과 정답은 fit에 전달하지 않습니다. GNN이나 Neo4j 쿼리 실행은 아닙니다.")
    else:  # day 14: 조건 선택은 개발 데이터의 CV로만, 최종 test는 선택된 모델만 평가
        from sklearn.base import clone
        development = np.concatenate([train, validation])
        cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=args.seed)
        candidates = [("logistic", scaled(LogisticRegression(max_iter=2000))),
                      ("kNN", scaled(KNeighborsClassifier(n_neighbors=args.neighbors))),
                      ("SVM", scaled(SVC(C=1))),
                      ("random forest", RandomForestClassifier(n_estimators=80, random_state=args.seed, n_jobs=1))]
        scores = []
        for name, model in candidates:
            values = cross_val_score(model, X[development], y[development], cv=cv, scoring="f1_macro", n_jobs=1)
            scores.append(float(values.mean()))
            rows.append({"model": name, "split": "development CV", "macro_f1": float(values.mean()), "cv_std": float(values.std())})
        name, prototype = candidates[int(np.argmax(scores))]
        selected_model = name
        final = clone(prototype).fit(X[development], y[development])
        predicted = final.predict(X[test])
        rows.append({"model": name, "split": "final test", "accuracy": accuracy_score(y[test], predicted),
                     "macro_f1": f1_score(y[test], predicted, average="macro")})
        record_predictions(name, predicted, test)
        axis.bar([r["model"] for r in rows[:-1]], scores)
        axis.set_ylabel("Development CV macro F1")
        notes.append(f"CV로 선택: {name}")
        notes.append("최종 test는 선택된 모델 하나만 평가했습니다. 결과를 보고 조건을 다시 고르면 더는 독립적인 최종 평가가 아닙니다.")

    if args.day != 8:
        splits = {"train": train.tolist(), "validation": validation.tolist(), "test": test.tolist()}
        counts = {key: len(value) for key, value in splits.items()}
        (output / "split.json").write_text(json.dumps(splits, indent=2), encoding="utf-8")
    else:
        counts = {"exploration": 300}
        # 군집화는 이 파일에서 전체 점군 탐색입니다. 감독학습 분할로 표시하지 않습니다.
        (output / "split.json").write_text(json.dumps({"exploration": list(range(300))}), encoding="utf-8")
    figure.suptitle(f"Day {args.day:02}")
    figure.savefig(output / "plot.png", dpi=130)
    plt.close(figure)
    write_csv(output / "metrics.csv", rows)
    if predictions:
        write_csv(output / "predictions.csv", predictions)
    payload = {"day": args.day, "dataset": dataset, "seed": args.seed, "split_counts": counts,
               "test_evaluated": args.day == 14, "selected_model": selected_model, "sklearn_version": sklearn.__version__,
               "numpy_version": np.__version__, "options": {key: str(value) if isinstance(value, Path) else value for key, value in vars(args).items()},
               "metrics": rows, "notes": notes}
    (output / "results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    image = base64.b64encode((output / "plot.png").read_bytes()).decode()
    fields = list(dict.fromkeys(key for row in rows for key in row))
    headings = "".join(f"<th>{html.escape(key)}</th>" for key in fields)
    table_rows = "".join("<tr>" + "".join(f"<td>{html.escape(format(row[key], '0.4f') if isinstance(row.get(key), float) else str(row.get(key, '')))}</td>" for key in fields) + "</tr>" for row in rows)
    report = f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Day {args.day:02} 실습 결과</title><style>body{{font:16px system-ui;max-width:900px;margin:32px auto;padding:16px;line-height:1.7}}img{{width:100%}}th,td{{padding:12px;border-bottom:1px solid #ddd;overflow-wrap:anywhere}}table{{border-collapse:collapse;min-width:600px}}.table-wrap{{overflow-x:auto}}</style>
<h1>Day {args.day:02} 실습 결과</h1><p>{html.escape(dataset)}</p><p>분할: {html.escape(str(counts))} / 최종 test 평가: {args.day == 14}</p>
<ul>{''.join('<li>'+html.escape(note)+'</li>' for note in notes)}</ul><img alt="실험 결과 그래프" src="data:image/png;base64,{image}"><div class="table-wrap"><table><thead><tr>{headings}</tr></thead><tbody>{table_rows}</tbody></table></div></html>'''
    (output / "report.html").write_text(report, encoding="utf-8")
    print(json.dumps({"day": args.day, "metrics": rows}, ensure_ascii=False, indent=2))
    print(f"보고서: {(output / 'report.html').resolve()}")
    return payload


if __name__ == "__main__":
    main()
