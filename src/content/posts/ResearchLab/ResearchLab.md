---
title: "머신러닝·Neo4j 2주 실습"
published: 2026-03-20
updated: 2026-11-17
draft: true
labDownload: true
description: "회귀·분류·앙상블·군집화·PCA·신경망·준지도학습과 Neo4j 실습 정리."
tags: [머신러닝, Neo4j, Python, scikit-learn, PyTorch, 실습]
category: 실습
lang: ko
---

[실습 코드 ZIP 다운로드](#research-lab-download)

## 실습 환경

- Python 3.11, scikit-learn, PyTorch 사용.
- Neo4j는 Docker Compose로 실행.
- 신경망 학습은 CPU 기준.
- 다운로드한 ZIP을 풀고 `research-lab` 폴더에서 명령 실행.
- `day01`~`day14`에 해당 일자의 `lab.py`, `README.md`, `requirements.txt` 포함. Python 학습 예제에는 `lab.ipynb`도 포함.
- 결과는 각 일자 폴더의 `results/`에 저장. MNIST 다운로드 데이터는 루트의 `data/`에서 공유.

설치: [Python](https://www.python.org/downloads/) / [Docker](https://docs.docker.com/get-started/get-docker/)

### 가상환경

macOS / Linux

```sh
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

PowerShell에서 활성화가 차단되는 경우 `python` 대신 `.\.venv\Scripts\python.exe` 사용.

### 다운로드 구조

```text
research-lab/
├── README.md
├── curriculum.md
├── experiment-log.md
├── requirements-ml.txt
├── requirements-cnn.txt
├── requirements-neo4j.txt
├── day01/ ... day09/
│   ├── README.md
│   ├── lab.py
│   ├── lab.ipynb
│   └── requirements.txt
├── day10/ ... day11/
│   ├── README.md
│   ├── lab.py
│   ├── lab.ipynb
│   └── requirements.txt
├── day12/
│   ├── README.md
│   ├── lab.py
│   ├── requirements.txt
│   ├── compose.yaml
│   ├── .env.example
│   ├── graph.json
│   ├── seed.cypher
│   └── queries.cypher
└── day13/ ... day14/
    ├── README.md
    ├── lab.py
    ├── lab.ipynb
    └── requirements.txt
```

각 `lab.py`에는 해당 날짜의 모델과 처리 코드만 포함. 다른 일자의 Python 파일 없이 실행 가능.
명령은 루트 기준이며 폴더 안에서 `python lab.py`로 실행해도 같은 위치에 결과 저장.

### 패키지 설치

```sh
python -m pip install -r requirements-ml.txt
```

PyTorch와 Neo4j 설치는 아래 실행 환경 참고.

<!-- curriculum:start -->
## 커리큘럼

하루 60~90분, 14일 기준. 개념 정리 → 코드 실행 → 조건 변경 → 결과 비교 순서로 진행.

| 날짜 | 주제 | 실습 |
| --- | --- | --- |
| 1일 | 데이터와 기준 모델 | 데이터 분할, DummyClassifier |
| 2일 | 회귀 | 선형 회귀, Ridge |
| 3일 | 분류 | 로지스틱 회귀, accuracy, macro F1 |
| 4일 | 거리 기반 모델 | kNN, SVM, 표준화 |
| 5일 | 결정 트리 | 깊이 제한, 과적합 |
| 6일 | 앙상블 | Random Forest, Gradient Boosting |
| 7일 | 모델 선택 | 3-fold CV, GridSearchCV |
| 8일 | 군집화 | k-means, silhouette |
| 9일 | 차원 축소 | PCA, 설명 분산 |
| 10일 | 신경망 | MLP, 역전파, 학습률 |
| 11일 | 이미지 분류 | CNN, MLP와 비교 |
| 12일 | 그래프 DB | Neo4j, Cypher, 관계 탐색 |
| 13일 | 준지도학습 | Label Spreading |
| 14일 | 종합 실험 | 모델 비교, 최종 평가 |

### 학습 방식

| 구분 | 학습에 사용하는 정보 | 예시 |
| --- | --- | --- |
| 지도학습 | 입력과 정답 | 회귀, 로지스틱 회귀, kNN, SVM, 트리, MLP, CNN |
| 비지도학습 | 라벨 없는 입력 | k-means, PCA |
| 준지도학습 | 일부 라벨과 라벨 없는 입력 | Label Spreading |

- CNN은 신경망의 구조, 지도·비지도·준지도학습은 학습에 사용하는 정보에 따른 구분.
- Neo4j는 관계를 저장·조회하는 DB. 모델 학습과는 별도 구성.

### 데이터와 평가

- 1일·3~7일·9일·14일: scikit-learn의 Wine 데이터. 178개 샘플, 13개 특성, 3개 클래스.
- 2일: 잡음을 포함한 합성 회귀 데이터.
- 8일: 합성 점군 300개. 라벨 없이 군집화.
- 10~11일: MNIST 28×28 손글씨 숫자.
- 13일: two-moons 합성 데이터.

지도학습 데이터는 train 60% / validation 20% / test 20%로 분할.
1~7일에는 validation으로 비교하고, 14일에 CV로 선택한 모델만 test에서 평가.
표준화·PCA는 train에만 fit하고, 교차검증에서는 Pipeline 내부에서 fold별로 fit.

### 1일 · 데이터와 기준 모델

- `X`: 행은 샘플, 열은 특성. `y`: 정답 라벨.
- `DummyClassifier`: 가장 많은 클래스로만 예측하는 기준 모델.
- 기준 모델의 점수와 학습 모델의 점수를 비교.

데이터를 모델에 넣기 전 먼저 구분할 것은 샘플과 특성. Wine의 `X.shape`는 `(178, 13)`, `y.shape`는 `(178,)`이며 각 행의 13개 값으로 해당 와인 클래스를 예측하는 문제. 클래스 번호는 범주 구분용으로, 번호 사이의 크기나 거리를 뜻하지 않음.

분할은 전체에서 test 20%를 먼저 분리하고 남은 80%의 25%를 validation으로 분리. 최종 비율은 약 60/20/20이며, 정수 개수로 나누므로 정확히 같은 비율이 되지는 않음. 분류에서는 `stratify=y`로 각 집합의 클래스 비율을 비슷하게 유지.

```python
pool, test = train_test_split(indices, test_size=0.2,
                              random_state=seed, stratify=y)
train, validation = train_test_split(pool, test_size=0.25,
                                     random_state=seed, stratify=y[pool])
```

`random_state`는 분할 재현용 seed. 기준 모델은 입력 특성을 보지 않고 train에서 가장 많은 클래스로만 예측. 이후 모델이 단순한 클래스 비율보다 실제 특성을 잘 활용하는지 판단하는 출발점.

```sh
python day01/lab.py
```

비교 항목

- `results.json`의 데이터 분할 수와 baseline accuracy.
- `--seed 17 --out day01/results-seed17`로 분할을 바꾼 결과.

결과 해석

- `split.json`의 train·validation·test 인덱스는 서로 겹치지 않으며 합계는 178개.
- seed만 바꿔도 분할 구성과 점수가 달라질 수 있음. 모델 비교에서는 같은 분할 사용.
- 샘플이 사람·장비·시간별로 묶인 실제 자료라면 행 단위 무작위 분할 대신 그룹·시간 단위 분할도 검토.

### 2일 · 선형 회귀와 Ridge

- 선형 회귀: 입력의 가중합으로 연속값 예측.
- Ridge: L2 규제를 적용해 계수 크기 제한. `alpha`가 규제 강도.
- MAE·RMSE는 작을수록 오차가 작음. R²는 음수가 될 수도 있음.

회귀의 출력은 연속적인 숫자. 입력 8개 중 4개가 정답 생성에 관여하고 잡음을 더한 합성 데이터를 사용. 선형 회귀는 `예측값 = 절편 + 각 특성 × 계수의 합`으로 계산하며, 학습에서는 예측 오차 제곱합이 작아지는 계수를 구함.

Ridge는 여기에 계수 제곱합에 대한 벌점을 추가. alpha가 커질수록 계수가 작아지는 쪽으로 학습되며, 규제가 너무 강하면 데이터의 관계까지 충분히 표현하지 못할 수 있음. Ridge 앞에 표준화를 두어 특성의 단위가 벌점에 미치는 영향을 조정.

```python
model = make_pipeline(StandardScaler(), Ridge(alpha=10))
model.fit(X[train], y[train])
predicted = model.predict(X[validation])
```

MAE는 오차 절댓값의 평균, RMSE는 오차 제곱 평균의 제곱근. 오차가 1과 9인 두 샘플은 MAE가 5, RMSE가 약 6.4로 큰 오차가 RMSE에 더 강하게 반영. R²는 정답 평균을 예측하는 기준과 비교한 값.

```sh
python day02/lab.py
python day02/lab.py --alpha 100 --out day02/results-alpha100
```

비교 항목

- 평균값 기준 모델, 선형 회귀, Ridge의 MAE·RMSE.
- 실제값–예측값 그래프와 `alpha=1, 10, 100`의 차이.

결과 해석

- 산점도의 가로축은 실제값, 세로축은 예측값. 대각선 주변에 모일수록 오차가 작음.
- 규제를 강하게 했는데 MAE·RMSE가 커지면 과도한 규제로 표현력이 줄었는지 확인.
- mean baseline보다 개선되지 않는 경우 데이터 분할, 특성, 규제 강도를 함께 확인.

### 3일 · 로지스틱 회귀

- 로지스틱 회귀: 클래스 분류에 사용하는 선형 모델.
- accuracy: 전체 샘플 중 정답을 맞힌 비율.
- macro F1: 클래스별 F1의 단순 평균. F1은 precision과 recall을 함께 반영.

로지스틱 회귀는 선형 결합을 클래스 확률로 바꾸어 분류. 이 예제는 Wine의 3개 클래스 중 하나를 예측하며, train에서 표준화와 모델 학습을 수행한 뒤 validation에 같은 변환 적용.

```python
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
model.fit(X[train], y[train])
predicted = model.predict(X[validation])
```

precision은 특정 클래스로 예측한 것 중 정답인 비율, recall은 실제 해당 클래스 중 찾아낸 비율. F1은 두 값의 조화평균으로 `2 × precision × recall / (precision + recall)`이며, macro F1은 각 클래스의 F1을 동일한 비중으로 평균.

예를 들어 100개 중 90개가 한 클래스라면 모두 그 클래스로 예측해도 accuracy는 90%. 다른 클래스를 전혀 찾지 못하는 문제는 accuracy 하나로 드러나기 어려워 macro F1과 클래스별 오분류를 함께 확인.

```sh
python day03/lab.py
```

비교 항목

- baseline과 로지스틱 회귀의 validation accuracy·macro F1.
- `predictions.csv`의 오분류와 클래스별 차이.

결과 해석

- `predictions.csv`에서 actual과 predicted가 다른 행을 확인하고 정답 클래스별로 집계.
- accuracy와 macro F1의 차이가 크면 특정 클래스에 예측이 치우쳤는지 확인.
- max_iter는 최적화 반복 상한. 반복을 늘리는 것과 모델의 입력·규제 조건을 바꾸는 것은 별개.

### 4일 · kNN과 SVM

- kNN: 가까운 이웃의 라벨로 분류.
- SVM: 클래스 사이의 결정 경계를 학습. 예제는 RBF 커널 사용.
- `StandardScaler`: train의 평균·표준편차로 표준화하고 validation에 동일하게 적용.

kNN은 새 입력과 가까운 train 샘플 k개를 찾고 이웃의 클래스로 예측. `fit`에서 복잡한 경계를 최적화하기보다는 학습 샘플을 보관하고 예측 시 거리를 계산. k가 작으면 국소 변화에 민감하고, k가 크면 주변을 넓게 평균하는 효과.

Wine의 특성은 값의 범위가 서로 달라 원래 값으로 거리를 계산하면 큰 단위의 특성이 지배할 수 있음. StandardScaler는 train의 평균과 표준편차로 `(값 - 평균) / 표준편차`를 계산. validation의 평균을 다시 구하지 않고 train에서 구한 값을 그대로 사용.

```python
knn = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5))
svm = make_pipeline(StandardScaler(), SVC(C=1, kernel="rbf"))
```

SVM은 클래스 사이의 경계를 학습하고, RBF 커널은 비선형 관계를 다루는 선택지. kNN과 SVM은 동작 방식이 다르지만 모두 입력 특성의 스케일에 영향을 받음.

```sh
python day04/lab.py
python day04/lab.py --neighbors 9 --out day04/results-k9
```

비교 항목

- 표준화 전후 kNN과 SVM의 validation 점수.
- 이웃 수 `k=3, 5, 9`에 따른 차이.

결과 해석

- raw kNN과 scaled kNN 비교는 전처리의 영향, scaled kNN과 scaled SVM 비교는 모델의 영향.
- k를 바꾼 실험에서는 분할·seed를 유지. 한 조건만 바꾸어 변화 원인 구분.
- 전체 데이터를 먼저 표준화하면 validation/test의 통계가 학습에 들어가므로 분할 후 Pipeline 사용.

### 5일 · 결정 트리

- 조건을 순서대로 나누어 예측하는 모델.
- 깊이가 작으면 표현력 제한, 깊이가 커지면 train에 과도하게 맞춰질 수 있음.
- train과 validation 점수 차이로 과소적합·과적합 확인.

결정 트리는 특정 특성이 임계값보다 작은지 비교하며 데이터를 나누는 구조. 각 분기에서 클래스가 더 잘 분리되는 특성과 임계값을 찾고, 마지막 leaf에서 클래스 예측. 깊이는 입력이 통과하는 분기 단계 수와 연결.

```python
shallow = DecisionTreeClassifier(max_depth=3, random_state=seed)
unlimited = DecisionTreeClassifier(random_state=seed)
```

깊이가 1인 트리는 한 번의 분기로만 전체 클래스를 구분하므로 복잡한 관계를 놓칠 수 있음. 제한 없는 트리는 train의 개별 샘플과 잡음까지 나누어 train accuracy가 높아지기 쉬움. 두 모델의 train/validation 막대를 나란히 출력해 학습 점수와 새 데이터 점수의 차이 확인.

트리는 임계값으로 분기하므로 이 예제에서는 별도 표준화 없이 실행. 거리 기반 모델에서 필요했던 전처리가 모든 모델에 똑같이 필요한 것은 아님.

```sh
python day05/lab.py
python day05/lab.py --depth 1 --out day05/results-depth1
```

비교 항목

- 깊이 제한 트리와 무제한 트리.
- `--depth 1, 3, 8`에서 train/validation 점수 변화.

결과 해석

- train과 validation이 모두 낮으면 과소적합 가능성, train만 높고 validation이 낮으면 과적합 가능성 검토.
- 작은 데이터에서는 무제한 트리도 validation 점수가 높게 나올 수 있어 한 분할만으로 결론을 고정하지 않음.
- 깊이 외에도 leaf 최소 샘플 수 같은 제약으로 복잡도를 조절할 수 있음.

### 6일 · Random Forest와 Boosting

- Random Forest: 샘플·특성을 달리한 여러 트리의 예측 결합.
- Gradient Boosting: 이전 오차를 줄이는 모델을 순차적으로 추가.

앙상블은 여러 모델의 예측을 결합하는 방식. Random Forest는 복원추출한 학습 샘플과 분기마다 선택한 특성 일부로 서로 다른 트리를 만들고 예측을 결합. 개별 트리의 변화가 최종 결과에 미치는 영향을 줄이는 효과.

Gradient Boosting은 앞선 모델의 오차를 줄이는 방향으로 다음 트리를 추가. 트리를 독립적으로 많이 만드는 Forest와 순차적으로 보완하는 Boosting의 차이. 제공 코드에서는 scikit-learn의 GradientBoostingClassifier 사용.

```python
forest = RandomForestClassifier(n_estimators=80, max_depth=3,
                                random_state=seed, n_jobs=1)
boosting = GradientBoostingClassifier(n_estimators=60, max_depth=2,
                                      random_state=seed)
```

n_estimators는 트리 수. 늘리면 실행 시간과 모델 크기도 커지며, 특히 Boosting에서는 트리 수와 learning_rate를 함께 고려. 같은 데이터 분할에서 단일 트리와 두 앙상블을 비교.

```sh
python day06/lab.py
```

비교 항목

- 같은 분할에서 단일 트리, Random Forest, Gradient Boosting의 점수.
- 코드의 `n_estimators` 변경에 따른 점수와 실행 시간.

결과 해석

- 단일 트리보다 train/validation 차이가 줄었는지와 validation 지표가 개선되는지 함께 확인.
- Forest의 depth를 바꾸는 실험은 `--depth`, 트리 수 비교는 코드의 n_estimators 변경.
- 점수가 같으면 실행 비용·예측 속도·설명 가능성을 비교 기준으로 사용.

### 7일 · 교차검증과 모델 선택

- 학습 데이터를 3개 fold로 나누어 kNN의 `k=3, 5, 9` 비교.
- `GridSearchCV`로 CV macro F1이 가장 높은 조건 선택.
- 선택한 모델만 validation에서 평가.
- scaler는 Pipeline 안에 배치해 fold 사이의 정보 누수 방지.

한 번의 validation 분할에서 좋은 조건이 다른 분할에서도 좋은지 확인하는 단계. train을 3개 fold로 나누고 두 fold로 학습, 남은 한 fold로 평가하는 과정을 반복. 각 샘플은 한 번씩 fold 평가에 사용되며 validation과 최종 test는 이 CV 안에 넣지 않음.

```python
search = GridSearchCV(
    make_pipeline(StandardScaler(), KNeighborsClassifier()),
    {"kneighborsclassifier__n_neighbors": [3, 5, 9]},
    cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=seed),
    scoring="f1_macro", n_jobs=1,
)
search.fit(X[train], y[train])
```

각 k에 대해 fold별 macro F1의 평균과 표준편차 계산. GridSearchCV는 평균이 가장 높은 조건을 선택하고 전체 train으로 다시 학습한 모델을 제공. scaler도 Pipeline 안에 있으므로 fold가 바뀔 때 해당 학습 fold로만 다시 fit.

```sh
python day07/lab.py
```

비교 항목

- `train CV`의 평균·표준편차와 선택 모델의 `validation` 점수.
- 1~6일 결과의 전처리, 모델, 지표, 선택 조건 정리.

결과 해석

- `train CV`의 평균은 조건 선택용, `validation` 행은 선택 후 별도 집합에서 확인한 결과.
- 표준편차가 크면 fold 구성에 민감한지 검토. 이 값 자체를 일반적인 신뢰구간으로 해석하지 않음.
- 1~6일의 모델별 결과를 정리할 때 분할·지표가 같은 결과끼리 비교.

### 8일 · k-means

- 가까운 중심점에 샘플을 배정하고 중심을 갱신하는 군집화 방법.
- silhouette: 군집 내부의 밀집도와 다른 군집과의 분리 정도. 범위는 대체로 -1~1.
- inertia: 중심점까지 거리 제곱의 합. 군집 수가 늘면 작아지기 쉬움.

k-means는 정답 라벨 없이 입력 사이의 구조를 묶는 방법. 초기 중심점을 정하고, 가까운 중심점에 샘플을 배정한 뒤 각 군집의 평균으로 중심점을 이동시키는 과정을 반복. 제공 코드는 2차원 합성 점군 300개를 사용하며 클래스 정답을 fit에 전달하지 않음.

```python
clusters = KMeans(n_clusters=3, n_init=10, random_state=seed).fit(X)
labels = clusters.labels_
```

n_init은 다른 초기 중심점에서 여러 번 실행하는 횟수. 군집 번호는 묶음을 구분하는 임의의 번호로, 실행이 달라지면 같은 묶음의 번호가 바뀔 수 있음.

silhouette는 같은 군집 내부 거리와 가장 가까운 다른 군집까지의 거리를 비교. 높을수록 현재 거리 기준에서 잘 분리된 모양. inertia는 중심점까지 거리 제곱합이므로 군집 수를 늘리면 줄기 쉬워, inertia가 가장 작은 k를 무조건 고르는 방식은 적절하지 않음.

```sh
python day08/lab.py
python day08/lab.py --clusters 5 --out day08/results-k5
```

비교 항목

- `k=2, 3, 5`의 군집 그림, silhouette, inertia.
- 군집 번호와 정답 클래스의 차이.

결과 해석

- plot.png에서 중심점과 군집 경계를 보고 수치 지표와 함께 해석.
- k=2·3·5의 결과를 같은 seed로 비교. 합성 데이터의 생성 중심 수와 실제 자료의 군집 수 추정은 구분.
- 이 실험은 전체 점군 탐색이며 별도 test 예측 정확도를 보고하지 않음.

### 9일 · PCA

- 라벨 없이 분산이 큰 방향을 찾아 차원 축소.
- train으로 fit한 뒤 validation을 투영. 그림은 첫 두 주성분.
- 그림의 색은 정답 표시용이며 PCA 학습에는 사용하지 않음.

PCA는 특성을 새 축으로 바꾸고 분산이 큰 축부터 선택하는 선형 차원 축소. 먼저 train의 특성을 표준화해 큰 단위의 특성 하나가 분산을 지배하는 영향을 줄임. 첫 주성분은 분산이 가장 큰 방향, 이후 주성분은 앞선 축과 직교하면서 남은 분산이 큰 방향.

```python
projection = make_pipeline(StandardScaler(), PCA(n_components=2))
projection.fit(X[train])
coordinates = projection.transform(X[validation])
```

PCA에는 y를 전달하지 않으므로 클래스를 잘 나누는 방향을 직접 학습하지 않음. 투영 그림의 색은 결과 해석을 위해 정답을 표시한 것. 설명 분산 비율은 각 성분이 전체 분산 중 보존하는 비율이며, 선택한 성분의 비율을 더하면 누적 보존량.

2개 성분으로 압축한 그림과 5개 성분의 누적 비율을 비교. `--components 5`에서도 그림은 첫 두 성분만 표시하고, 수치 파일에는 5개 성분의 비율 저장.

```sh
python day09/lab.py
python day09/lab.py --components 5 --out day09/results-pc5
```

비교 항목

- 2개·5개 성분의 누적 설명 분산 비율.
- 2차원 투영에서 클래스가 겹치는 구간.

결과 해석

- 설명 분산이 높다는 것이 분류 정확도가 높다는 뜻은 아님.
- 2차원에서 겹치는 샘플도 버린 축에서는 구분될 수 있음.
- validation을 포함해 PCA를 fit하면 평가 집합의 구조가 전처리에 반영되므로 train에만 fit.

### 10일 · MLP

- MNIST 픽셀 784개 → 은닉층 64개 → 숫자 10종 분류.
- loss의 기울기를 역전파해 가중치 갱신.
- epoch: 학습 데이터 전체를 보는 횟수. batch: 한 번의 업데이트에 사용하는 샘플 수.

MNIST의 픽셀값을 0~1 범위의 tensor로 바꾼 뒤 28×28 이미지를 길이 784의 벡터로 펼침. Linear 층에서 가중합을 계산하고 ReLU를 거쳐 마지막 Linear 층이 숫자 0~9의 점수(logits) 10개를 출력.

```python
model = nn.Sequential(
    nn.Flatten(), nn.Linear(784, 64), nn.ReLU(), nn.Linear(64, 10)
)
loss = criterion(model(images), labels)
optimizer.zero_grad()
loss.backward()
optimizer.step()
```

CrossEntropyLoss는 logits와 정답 클래스를 받아 loss 계산. backward는 각 가중치의 기울기를 계산하고 Adam이 그 기울기로 업데이트. zero_grad는 이전 batch의 기울기가 누적되지 않도록 초기화하는 단계. 학습률은 업데이트 크기를 조절하는 설정이며 가중치와 달리 사람이 정함.

학습은 train에서만 수행. epoch마다 validation의 loss와 accuracy를 기록하고, report.html에는 검증 이미지 12개의 정답·예측 표시. 같은 데이터 인덱스와 seed를 다음 날 CNN에서도 사용.

```sh
python day10/lab.py --epochs 2 --train-limit 2000 --validation-limit 500 --test-limit 500
```

비교 항목

- epoch별 validation loss·accuracy와 오분류 이미지.
- `--lr 0.0001`과 기본 학습률 `0.001`의 차이.

결과 해석

- train loss가 줄어도 validation loss가 함께 줄어드는지 확인. accuracy는 맞힌 개수, loss는 정답에 부여한 확률까지 반영.
- 학습률 비교에서는 epoch·샘플 수·seed 유지. 출력 폴더를 바꾸어 기록 보관.
- `weights.pt`는 모델의 state_dict. 모델 구조를 동일하게 만든 뒤 읽어야 가중치와 연결 가능.

### 11일 · CNN

- 합성곱 필터로 이미지의 공간적 특징 추출.
- Conv → ReLU → Pooling → Linear 순서로 분류.
- 10일과 같은 MNIST·seed·샘플 수·epoch 사용.

합성곱은 작은 필터를 이미지의 여러 위치에 같은 가중치로 적용. 입력을 바로 펼치는 MLP와 달리 이웃 픽셀의 배치를 유지한 상태에서 특징을 계산. ReLU는 음수를 0으로 바꾸고 MaxPool2d(2)는 각 2×2 영역의 최댓값으로 공간 크기를 절반으로 축소.

```text
입력      : batch × 1 × 28 × 28
Conv1/ReLU: batch × 8 × 28 × 28
Pooling   : batch × 8 × 14 × 14
Conv2/ReLU: batch × 16 × 14 × 14
Pooling   : batch × 16 × 7 × 7
Flatten   : batch × 784
Linear    : batch × 10
```

두 합성곱의 padding=1은 3×3 필터 적용 전후 공간 크기를 유지하기 위한 설정. 채널 수 8·16은 각 층에서 추출하는 특징 맵 수. 마지막 16×7×7 값을 펼쳐 10개 클래스의 logits로 변환.

10일과 같은 데이터 수·seed·epoch로 실행하되 구조와 계산 비용이 달라 정확도뿐 아니라 실행 시간과 오분류도 함께 비교. validation으로 조건을 확정한 뒤 선택 모델에만 `--evaluate-test`를 추가. 이 옵션은 학습을 마친 마지막 모델을 test에서 한 번 평가.

```sh
python day11/lab.py --epochs 2 --train-limit 2000 --validation-limit 500 --test-limit 500
```

비교 항목

- MLP와 CNN의 validation loss·accuracy, 오분류, 학습 시간.
- validation 기준으로 조건 확정 후 선택 모델에 `--evaluate-test`를 추가해 최종 test 평가.

결과 해석

- 표의 각 tensor 크기를 코드의 Conv2d·MaxPool2d·Linear 설정과 연결.
- CNN이 작은 데이터·적은 epoch에서도 항상 우수한 것은 아니므로 실제 지표로 비교.
- test 결과를 본 뒤 조건을 다시 고르면 그 test는 최종 평가용으로 독립적이지 않음.

### 12일 · Neo4j

- 노드·관계·속성으로 연구자, 주제, 논문 표현.
- Cypher로 연구 주제, 공통 주제, 최단 경로 조회.

그래프 DB에서 노드는 대상, 관계는 대상 사이의 연결, 속성은 이름 같은 값. Researcher·Topic·Paper는 노드 라벨이고 WORKS_ON은 연구자에서 주제로 향하는 관계 종류. 관계에도 방향이 있으며 조회 패턴에서 방향을 지정하거나 생략할 수 있음.

```cypher
MATCH (r:ResearchLab:Researcher {lab_id: 'research-lab-v1'})
      -[:WORKS_ON]->(t:ResearchLab:Topic {lab_id: 'research-lab-v1'})
RETURN r.name, t.name
```

MATCH는 연결 패턴에 맞는 대상을 찾고 RETURN은 결과에 포함할 값을 선택. seed에서는 MERGE로 같은 lab_id·id의 노드를 재사용하고 고유성 제약으로 중복 생성 방지. 실습 데이터는 ResearchLab 라벨과 lab_id로 다른 데이터와 구분.

공통 주제 조회는 같은 Topic을 사이에 둔 연구자 두 명을 찾는 패턴. `a.id < b.id`로 자기 자신과 A–B/B–A 중복 제외. 최단 경로는 방향을 무시하고 관계 1~6개 범위에서 연결을 찾으며, 결과의 hops는 노드 수가 아닌 관계 수.

```sh
python day12/lab.py seed
python day12/lab.py queries
```

확인 항목

- 노드 7개·관계 9개.
- 연구자–주제 3행, 공통 주제 쌍 1행, 민지→소라 최단 경로 3관계.
- `day12/graph.json`에 연구자와 `WORKS_ON` 관계를 추가한 뒤 공통 주제 쌍 변화.

결과 해석

- seed를 두 번 실행해도 기본 그래프는 7노드·9관계 유지.
- CSV의 topics·shared·path를 Browser의 Cypher 조회와 비교.
- graph.json 수정 후 MERGE는 추가·갱신을 수행하며 파일에서 지운 노드를 자동 삭제하는 동기화는 아님. 초기화가 필요하면 아래 실습 ID 지정 reset 사용.

### 13일 · Label Spreading

- 소수의 라벨과 입력 간 근접 관계를 이용하는 준지도학습.
- train의 클래스별 라벨 20%만 남기고 나머지는 `-1`로 설정.
- 같은 라벨 수의 로지스틱 회귀와 validation 점수 비교.
- 근접 그래프는 입력에서 계산하며 Neo4j와는 별개.

라벨 없는 데이터가 많고 일부에만 정답을 붙일 수 있는 경우의 준지도학습. 이 예제는 정답이 있는 합성 데이터를 만든 뒤 train 안에서 클래스별 라벨 일부만 남겨 상황을 재현. 감춘 라벨은 -1로 전달하며 평가용 정답은 별도로 유지.

```python
observed = np.full(len(train), -1)
observed[chosen_indices] = y[train][chosen_indices]
model = LabelSpreading(kernel="knn", n_neighbors=5, max_iter=100)
model.fit(train_scaled, observed)
```

Label Spreading은 입력의 근접 관계를 이용해 라벨 정보를 전파. 가까운 샘플이 비슷한 클래스를 가진다는 구조적 가정을 사용. 같은 라벨 수만 사용하는 로지스틱 회귀는 알려진 샘플만으로 경계를 학습하고, Label Spreading은 라벨 없는 train의 위치 정보도 함께 활용.

표준화에는 train 입력만 사용하고 validation/test의 입력·정답은 fit에 전달하지 않음. 근접 그래프는 이 입력에서 계산하며 12일의 연구 협업 그래프와 별도. DB나 GNN 실행 과정은 포함하지 않음.

```sh
python day13/lab.py
python day13/lab.py --labeled-fraction 0.1 --out day13/results-label10
```

비교 항목

- 라벨 비율 `0.1, 0.2, 0.5`에 따른 점수 변화.
- 가까운 입력끼리 라벨이 비슷하다는 가정과 잘못된 라벨 전파.

결과 해석

- metrics.csv의 labeled_train·unlabeled_train 합계가 train 개수와 같은지 확인.
- 라벨 비율 0.1·0.2·0.5에서 점수와 오류 사례 비교. 클래스별로 라벨을 남기는 합성 실험 조건도 기록.
- 서로 다른 클래스가 가까이 섞이면 잘못된 라벨 정보도 전파될 수 있으므로 라벨 수 증가만으로 결과를 단정하지 않음.

### 14일 · 종합 실험

- Wine의 train+validation 80%를 개발 집합으로 사용.
- 로지스틱 회귀·kNN·SVM·Random Forest를 3-fold CV macro F1로 비교.
- CV 점수가 가장 높은 모델 하나만 test 20%에서 평가. 동점이면 코드의 나열 순서 적용.

앞선 단계에서 사용한 train과 validation을 합쳐 개발 집합으로 사용. 후보 모델별로 이 개발 집합 안에서 3-fold CV를 수행하고 평균 macro F1로 선택. test는 이 선택 과정에 사용하지 않음.

```python
scores = cross_val_score(model, X[development], y[development],
                         cv=cv, scoring="f1_macro", n_jobs=1)
# 평균 CV 점수로 후보 하나를 선택한 뒤
final = clone(selected_model).fit(X[development], y[development])
predicted = final.predict(X[test])
```

선택한 모델을 개발 집합 전체에 다시 fit한 뒤 남겨 둔 test 20%에서 평가. metrics.csv에서 development CV 행은 후보 비교, final test 행은 최종 선택 모델 한 개의 결과. 동점은 후보를 나열한 순서로 결정.

보고서에는 최종 점수뿐 아니라 데이터·분할·seed·버전, baseline, CV 비교, 선택 근거와 오분류를 함께 정리. 서로 다른 데이터셋의 점수는 한 순위표로 섞지 않고 같은 조건의 결과끼리 비교.

```sh
python day14/lab.py
```

정리 항목

- 데이터, 분할, seed, 패키지 버전.
- baseline, CV 비교 결과, 선택 모델과 선택 이유.
- 최종 test 지표, 오분류, 다음 실험.

결과 해석

- results.json의 selected_model과 final test 행의 모델이 일치하는지 확인.
- 다른 seed나 실제 연구 데이터로 확장할 때는 별도 실험으로 기록. 같은 test를 반복해서 조건 선택에 사용하지 않음.
- 점수 차이가 작으면 표본 수와 분할 변동도 함께 고려하고 다음에 검증할 조건을 구체적으로 정리.

### 실행 결과

`day01/results/`처럼 날짜별 폴더에 저장. `--out day04/results-k9`로 실험별 경로 지정.

| 파일 | 내용 |
| --- | --- |
| `report.html` | 그래프와 지표를 포함한 HTML 보고서 |
| `plot.png` | 결과 그래프 |
| `metrics.csv` | 모델별 지표 |
| `predictions.csv` | 예측값, 군집 번호 또는 투영 좌표 |
| `split.json` | 데이터 분할 인덱스 |
| `results.json` | 실행 조건, 버전, 지표 |

같은 `--out` 경로는 기존 결과를 덮어씀. 실험 기록 양식은 `experiment-log.md` 사용.
<!-- curriculum:end -->

## PyTorch 실행 환경

macOS

```sh
python -m pip install -r requirements-cnn.txt
```

Windows / Linux CPU

```sh
python -m pip install -r requirements-cnn.txt --index-url https://download.pytorch.org/whl/cpu
```

설치 확인

```sh
python -c "import torch, torchvision; print(torch.__version__, torchvision.__version__)"
```

- 최초 실행 시 MNIST를 `data/`에 다운로드.
- 공식 학습 60,000개에서 학습·검증용 인덱스를 겹치지 않게 선택.
- 기본값: 학습 2,000개, 검증 500개, 테스트 후보 500개.
- epoch별 평가는 validation 사용. `--evaluate-test` 지정 시 마지막 모델을 test에서 평가.

CNN 구성

```python
model = nn.Sequential(
    nn.Conv2d(1, 8, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
    nn.Conv2d(8, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
    nn.Flatten(), nn.Linear(16 * 7 * 7, 10),
)
```

- 학습은 `model.train()`, 평가는 `model.eval()`과 `torch.no_grad()` 사용.
- `CrossEntropyLoss`에는 softmax 이전 logits 입력.
- `report.html`에 이미지 12개와 정답·예측 표시. `weights.pt`에 `state_dict` 저장.
- `--dataset synthetic`은 28×28 합성 선 이미지로 실행하는 옵션.

## Neo4j 실행 환경

### 서버 실행

Docker 실행 후 환경 파일 생성.

```sh
docker --version
docker compose version
```

- macOS / Linux: `cp day12/.env.example day12/.env`
- PowerShell: `Copy-Item day12/.env.example day12/.env`

```sh
docker compose --project-directory day12 --env-file day12/.env up -d --wait --wait-timeout 180
python -m pip install -r requirements-neo4j.txt
```

| 항목 | 값 |
| --- | --- |
| Neo4j Browser | `http://127.0.0.1:17474` |
| 드라이버 URI | `bolt://127.0.0.1:17687` |
| 사용자 / DB | `neo4j` |
| 기본 비밀번호 | `ResearchLabOnly123` — 로컬 실습용 |

Python 실행 시 `day12/.env`의 비밀번호 입력. `NEO4J_PASSWORD` 환경 변수를 설정한 경우 해당 값 사용.

### 데이터와 쿼리

- 노드: 연구자 3명, 주제 2개, 논문 2개.
- 관계: `WORKS_ON`, `AUTHORED`, `ABOUT`, `COLLABORATES_WITH`.
- 실습 데이터는 `ResearchLab` 라벨과 `lab_id: research-lab-v1`로 구분.
- `seed`는 `MERGE`와 고유성 제약으로 중복 생성 방지.

연구자별 주제 조회

```cypher
MATCH (r:ResearchLab:Researcher {lab_id: 'research-lab-v1'})
      -[:WORKS_ON]->(t:ResearchLab:Topic {lab_id: 'research-lab-v1'})
RETURN r.name AS researcher, t.name AS topic
ORDER BY researcher
```

공통 주제 조회

```cypher
MATCH (a:ResearchLab:Researcher {lab_id: 'research-lab-v1'})
      -[:WORKS_ON]->(t:ResearchLab:Topic {lab_id: 'research-lab-v1'})
      <-[:WORKS_ON]-(b:ResearchLab:Researcher {lab_id: 'research-lab-v1'})
WHERE a.id < b.id
RETURN a.name, b.name, t.name
```

`a.id < b.id`로 자기 자신과 순서만 다른 중복 쌍 제외.
최단 경로는 관계 방향을 무시하며, 전체 쿼리는 `day12/queries.cypher`에 포함.
Python 없이 데이터 생성 시 `day12/seed.cypher` 사용.

### 종료와 초기화

컨테이너 종료. 데이터 volume은 유지.

```sh
docker compose --project-directory day12 --env-file day12/.env down
```

실행 중인 서버에서 실습 노드만 삭제.

```sh
python day12/lab.py reset --confirm research-lab-v1
```

## Jupyter / Colab

각 날짜 폴더의 `lab.ipynb` 사용. 설치 확인 → 코드 정의 → 실행 → 보고서 순서.
해당 날짜의 전체 코드가 포함되어 Colab에는 노트북 하나만 업로드해도 실행 가능.
결과는 노트북 실행 위치의 `results/`에 저장. Colab 결과는 세션 종료 전 다운로드.
12일은 Docker·터미널·Neo4j Browser로 실행.

## 트러블슈팅

| 문제 | 확인 및 처리 |
| --- | --- |
| Docker 연결 실패 | Docker 앱/서비스, `docker info` 확인 |
| 포트 충돌 | Compose의 host 포트와 Python `--uri`를 함께 변경 |
| Neo4j 인증 실패 | 기존 volume의 암호는 `.env` 수정만으로 변경되지 않음 |
| DB 준비 대기 실패 | `docker compose --project-directory day12 --env-file day12/.env logs neo4j`, 메모리 확인 |
| Python 모듈 없음 | 가상환경의 Python으로 설치·실행 |
| MNIST 다운로드 실패 | 네트워크·프록시 확인. 코드 동작 확인은 `--dataset synthetic` 사용 |
| 학습 시간 단축 | `--train-limit 500 --validation-limit 100 --test-limit 100 --epochs 1` |

## 참고 자료

- [scikit-learn](https://scikit-learn.org/stable/getting_started.html)
- [교차검증](https://scikit-learn.org/stable/modules/cross_validation.html)
- [선형 모델](https://scikit-learn.org/stable/modules/linear_model.html)
- [앙상블](https://scikit-learn.org/stable/modules/ensemble.html)
- [군집화](https://scikit-learn.org/stable/modules/clustering.html)
- [PCA](https://scikit-learn.org/stable/modules/decomposition.html#pca)
- [준지도학습](https://scikit-learn.org/stable/modules/semi_supervised.html)
- [전처리와 데이터 누수](https://scikit-learn.org/stable/common_pitfalls.html)
- [Neo4j Docker](https://neo4j.com/docs/operations-manual/current/docker/introduction/)
- [Neo4j Python](https://neo4j.com/docs/python-manual/current/query-simple/)
- [PyTorch 설치](https://pytorch.org/get-started/locally/)
- [PyTorch 기초](https://docs.pytorch.org/tutorials/beginner/basics/intro.html)
- [MNIST](https://docs.pytorch.org/vision/main/generated/torchvision.datasets.MNIST.html)
- [CrossEntropyLoss](https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html)
