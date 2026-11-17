---
title: "연구실 2주 실습: 머신러닝 기초부터 CNN과 Neo4j까지"
published: 2026-03-20
updated: 2026-11-17
draft: true
practice: true
description: "14일 실습 초안: 회귀·분류·앙상블·군집화·PCA·신경망·준지도학습과 Neo4j."
tags: [머신러닝, Neo4j, Python, scikit-learn, PyTorch, 실습]
category: 실습
lang: ko
---

연구실에서 함께 실행해 볼 실습 초안입니다. 하루 60~90분씩 2주 동안 지도·비지도·준지도학습을 실행하고, 그래프 DB의 관계 탐색까지 이어갑니다. 준비 과정, 날짜별 과제와 실행 코드를 함께 넣었습니다.

작성일은 Linker 글보다 앞선 **2026년 3월 20일**로 두었습니다. 코드와 설치 안내는 **2026년 11월 17일** 기준으로 점검합니다. 아직 공개하지 않은 초안입니다. 학습 시간은 안내용이며 설치나 복습에 따라 늘어날 수 있습니다.

## 먼저 브라우저에서 실행하기

[아래 실습 화면으로 이동](#research-lab-playground)해서 두 예제를 실행할 수 있습니다.

1. **그래프 탐색**: 질문을 선택하고 실행하면 관계와 결과 표를 확인합니다. 결과는 CSV로 내려받습니다.
2. **CNN 학습**: 학습 횟수와 학습률을 정하고 실행합니다. loss, 검증 정확도, 필터 변화와 예측을 확인하고 기록·가중치를 내려받습니다.
3. **실습 코드 ZIP**: 14일 가이드, 회귀·분류·군집화 코드, Neo4j 설정, Cypher, Jupyter 노트북과 준비 안내를 한 번에 받습니다.

그래프 화면은 샘플 JSON에서 관계를 계산하는 예제입니다. 실제 Neo4j 서버에 연결하지 않습니다. CNN은 브라우저에서 합성곱과 역전파를 계산하는 작은 모델입니다. 다운로드한 코드는 실제 Neo4j와 PyTorch에서 실행합니다.

## 1. 공통 준비

브라우저 예제에는 별도 설치가 필요 없습니다. 다운로드한 코드를 실행하려면 다음을 준비합니다.

| 준비물 | 용도 |
| --- | --- |
| Python 3.11과 코드 편집기 | Python 예제 실행 |
| 터미널 또는 PowerShell | 설치·실행 명령 입력 |
| Docker Desktop 또는 Docker Engine + Compose v2 | Neo4j 서버 실행 |
| 인터넷과 디스크 여유 공간 | 최초 패키지·컨테이너·데이터 다운로드 |

설치 파일은 [Python 공식 다운로드](https://www.python.org/downloads/)와 [Docker 설치 안내](https://docs.docker.com/get-started/get-docker/)에서 운영체제에 맞게 선택합니다. 아래 명령은 Python 3.11 기준입니다.

PyTorch 예제는 **CPU**로 실행합니다. GPU나 CUDA 설치는 필요 없습니다. Docker는 설치한 뒤 앱 또는 서비스를 실행해야 합니다.

ZIP을 풀고 `research-lab` 폴더에서 가상환경을 만듭니다.

macOS/Linux:

```sh
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

PowerShell에서 활성화가 차단되면 정책을 변경할 필요 없이 이후 명령의 `python`을 `.\.venv\Scripts\python.exe`로 바꾸어 실행할 수 있습니다. `python --version`으로 버전을 확인합니다.

<!-- curriculum:start -->
## 2주 학습 경로

**하루 60~90분, 14일**을 기준으로 합니다. 평일에만 진행하면 약 3주로 나누셔도 됩니다. Python의 변수·리스트·함수와 터미널 명령을 조금 써 본 수준에서 시작합니다. 미분을 직접 계산하지 않아도 진행할 수 있고, 행렬의 크기와 평균·분산은 첫날 다시 확인합니다.

매일 **개념 15분 → 기본 실행 20분 → 조건 하나 변경 20분 → 기록·설명 10~20분** 순서로 진행합니다. 실행에 오래 걸리면 선택 과제는 다음 날로 넘깁니다. 점수보다 “무엇을 입력하고, 무엇을 학습하며, 어떤 데이터로 확인했는가”를 설명하는 데 초점을 둡니다.

| 날짜 | 학습 주제 | 실행 파일 | 남길 결과 |
| --- | --- | --- | --- |
| 1일 | 데이터·분할·기준 모델 | `classical_lab.py --day 1` | 데이터 크기, baseline |
| 2일 | 선형 회귀·Ridge | `--day 2` | 실제값–예측값 그래프, MAE |
| 3일 | 로지스틱 회귀·분류 지표 | `--day 3` | accuracy와 macro F1 |
| 4일 | kNN·SVM·표준화 | `--day 4` | 단위와 거리의 영향 |
| 5일 | 결정 트리·과적합 | `--day 5` | train/validation 차이 |
| 6일 | Random Forest·Boosting | `--day 6` | 단일 모델과 앙상블 비교 |
| 7일 | 교차검증·모델 선택 | `--day 7` | CV 평균·편차, 1주차 정리 |
| 8일 | 비지도학습·k-means | `--day 8` | 군집 그림, silhouette |
| 9일 | PCA·차원 축소 | `--day 9` | 2차원 투영, 설명 분산 |
| 10일 | MLP·역전파·최적화 | `train_cnn.py --model mlp` | validation loss와 오분류 |
| 11일 | CNN·공간 정보 | `train_cnn.py --model cnn` | 같은 조건의 MLP/CNN 비교 |
| 12일 | Neo4j·관계 탐색 | `neo4j_lab.py` | 관계 조회 3종, CSV |
| 13일 | 준지도학습·Label Spreading | `classical_lab.py --day 13` | 라벨 수에 따른 변화 |
| 14일 | 미니 프로젝트·최종 평가 | `classical_lab.py --day 14` | 최종 보고서와 한계 |

### 어떤 학습 방법이 다른가

| 구분 | 사용하는 정보 | 이번 과정의 예 |
| --- | --- | --- |
| 지도학습 | 입력과 정답 라벨 | 회귀, 로지스틱 회귀, kNN, SVM, 트리, MLP, CNN |
| 비지도학습 | 정답 없이 입력의 구조 | k-means, PCA |
| 준지도학습 | 일부 정답과 라벨 없는 입력 | Label Spreading |
| 강화학습 | 행동 후 환경에서 받는 보상 | 후속 주제. 이번 실습 범위에서는 제외 |

CNN은 신경망의 **구조**이고, 지도·비지도·준지도는 주로 **학습에 쓰는 정보의 방식**을 구분합니다. Neo4j는 데이터를 저장하고 관계를 조회하는 DB이며, 자체가 학습 모델은 아닙니다. Label Spreading도 GNN과는 다른 알고리즘입니다.

### 실행 준비와 결과 보는 법

앞의 가상환경을 활성화하고 ZIP을 푼 폴더에서 아래를 실행합니다.

```sh
python -m pip install -r requirements-ml.txt
python classical_lab.py --day 1
```

1~9일과 13~14일 예제는 scikit-learn에 포함된 Wine 데이터 또는 코드로 생성한 데이터를 씁니다. **패키지 설치 후에는 추가 데이터 다운로드가 필요 없습니다.** 10~11일의 PyTorch와 12일의 Docker는 해당 날짜에 설치해도 됩니다.

매번 `results/day01/`처럼 날짜별 폴더에 다음 결과가 생깁니다. `--out results/day04-k9`로 출력 위치를 바꾸면 실험 결과를 따로 보관합니다.

- `report.html`: 그래프가 포함된 단일 HTML. 브라우저로 열어 결과 확인
- `plot.png`: 보고서·발표에 넣을 그림
- `metrics.csv`, `results.json`: 모델별 지표, seed, 옵션, 패키지 버전, 해석 안내
- `predictions.csv`: 샘플별 예측 또는 군집·투영 좌표

`ml_basics.ipynb`는 설치 확인 → 전체 코드 정의 → `DAY` 선택 → 실행 → 보고서 순서로 구성되어 있습니다. Colab에 이 파일 하나를 올려 사용할 수 있습니다. 10~11일은 `cnn_lab.ipynb`, 12일은 아래 Neo4j 준비 안내를 사용합니다.

지도학습 예제는 보통 **train 60% / validation 20% / test 20%**로 나눕니다. 1~7일에는 train에서 학습하고 validation으로 확인하며 test 점수는 출력하지 않습니다. 전처리도 학습 데이터에만 맞춥니다. 8일은 전체 합성 데이터의 탐색이므로 예측 성능을 평가하는 실험과 구분합니다.

### 1일 · 데이터와 기준 모델

**목표:** `X`의 행은 샘플, 열은 특성이고 `y`는 정답이라는 것을 설명합니다. Wine 데이터는 178개 샘플, 13개 수치 특성, 3개 클래스입니다.

```sh
python classical_lab.py --day 1
```

**확인:** 다수 클래스만 고르는 `DummyClassifier`의 정확도가 100%가 아닌 이유를 확인합니다. 모델이 모든 샘플을 같은 클래스로 예측하는데도 얻는 점수가 비교 기준입니다. `results.json`에서 각 분할의 개수를 합하면 178인지 확인합니다.

**과제·점검:** `--seed 17 --out results/day01-seed17`로 다시 실행합니다. 데이터 분할이 달라져도 같은 문제가 유지되는지, 처음부터 test를 보고 조건을 고르면 왜 안 되는지 3문장으로 적습니다. 실습 내장 데이터의 점수를 실제 연구 성능으로 해석하지 않습니다.

### 2일 · 숫자를 예측하는 선형 회귀와 Ridge

**목표:** 분류와 회귀를 구분하고, 입력의 가중합으로 연속값을 예측합니다. Ridge는 가중치 크기에 벌점을 주는 L2 규제로 지나치게 큰 계수를 억제합니다.

```sh
python classical_lab.py --day 2
python classical_lab.py --day 2 --alpha 100 --out results/day02-alpha100
```

**확인:** 평균값만 예측하는 기준 모델, 선형 회귀, Ridge의 MAE·RMSE를 비교합니다. 그래프에서 점이 대각선에 가까울수록 예측이 맞습니다. R²는 음수일 수도 있고 정확도 백분율이 아닙니다.

**과제·점검:** alpha를 1과 100으로 바꾸어 저장합니다. 규제를 강하게 했는데 점수가 반드시 좋아지지는 않는 이유를 적습니다. 데이터는 잡음이 있는 합성이며 실험 측정값이 아닙니다.

### 3일 · 로지스틱 회귀와 분류 지표

**목표:** 이름에 “회귀”가 있어도 로지스틱 회귀는 여기서 클래스 분류에 쓰인다는 것을 이해합니다. accuracy는 전체 중 맞힌 비율, macro F1은 클래스별 F1의 단순 평균입니다. F1은 precision과 recall을 함께 반영합니다.

```sh
python classical_lab.py --day 3
```

**확인:** baseline과 로지스틱 회귀의 validation accuracy·macro F1을 비교합니다. `predictions.csv`에서 틀린 행을 찾고, 어떤 정답 클래스를 다른 것으로 예측했는지 셉니다.

**과제·점검:** 클래스별 표본 수가 크게 다르면 accuracy만으로 무엇을 놓칠지 적습니다. 연구 목적에 따라 오탐과 미탐 중 어느 쪽 비용이 큰지도 정합니다.

### 4일 · kNN, SVM과 표준화

**목표:** kNN은 가까운 이웃의 라벨을, SVM은 클래스를 구분하는 경계를 이용합니다. 거리 기반 모델에서 측정 단위가 중요한 이유를 확인합니다.

```sh
python classical_lab.py --day 4
python classical_lab.py --day 4 --neighbors 9 --out results/day04-k9
```

**확인:** 원래 단위의 kNN, `StandardScaler`를 거친 kNN, RBF 커널 SVM을 비교합니다. 표준화는 학습 데이터의 평균·표준편차를 구한 뒤 validation에 그대로 적용합니다.

**과제·점검:** 이웃 수 3·5·9 중 어느 조건을 선택할지 validation 근거를 적습니다. 전체 데이터를 먼저 표준화한 다음 나누면 어떤 정보가 새는지 설명합니다.

### 5일 · 결정 트리와 과적합

**목표:** 조건을 순서대로 나누는 트리의 깊이와 복잡도를 이해합니다. 학습 점수는 높은데 새 데이터에서 떨어지는 과적합을 살펴봅니다.

```sh
python classical_lab.py --day 5
python classical_lab.py --day 5 --depth 1 --out results/day05-depth1
```

**확인:** 깊이를 제한한 트리와 무제한 트리의 train/validation 막대를 봅니다. 이번 작은 데이터에서는 차이가 작거나 무제한 트리도 잘 맞을 수 있습니다. 모든 실행에서 과적합 그림이 나와야 하는 것은 아닙니다.

**과제·점검:** 깊이 1·3·8로 바꾸고 너무 단순한 모델의 과소적합과 과적합을 구분해 적습니다.

### 6일 · 앙상블: Random Forest와 Boosting

**목표:** 여러 모델을 결합하는 방식도 학습 방법의 중요한 선택지라는 것을 이해합니다. Random Forest는 샘플·특성을 달리한 여러 트리를 결합하고, boosting은 이전 오차를 줄이도록 모델을 순차적으로 더합니다.

```sh
python classical_lab.py --day 6
```

**확인:** 같은 분할에서 단일 트리, Random Forest, Gradient Boosting의 결과를 비교합니다. 데이터가 작으면 차이가 거의 없을 수도 있습니다.

**과제·점검:** 코드의 `n_estimators`를 한 군데씩 바꾸고 별도 폴더에 저장합니다. 점수뿐 아니라 실행 시간과 설명 가능성을 고려해 선택 이유를 적습니다. 이 예제의 boosting은 scikit-learn 구현이며 XGBoost 실행 예제는 아닙니다.

### 7일 · 교차검증과 1주차 정리

**목표:** 한 번의 분할 결과에만 의존하지 않고, 학습 데이터를 여러 fold로 나누어 조건을 선택합니다.

```sh
python classical_lab.py --day 7
```

**확인:** 학습 집합 안의 3-fold CV로 k=3·5·9를 비교하고, 선택한 kNN만 validation에서 확인합니다. 출력의 `train CV`와 `validation`은 서로 다른 평가입니다. CV 표준편차는 이 fold 사이의 변동이며 일반적인 신뢰구간은 아닙니다.

**과제·점검:** 1~6일 결과를 한 표로 정리합니다. “전처리 → 모델 → 지표 → 조건 선택”을 말로 설명할 수 있으면 다음 주로 넘어갑니다. scaler가 `Pipeline` 내부에 있어야 fold 밖 정보가 섞이지 않습니다.

### 8일 · 라벨 없는 데이터의 군집화

**목표:** 정답 없이 비슷한 입력을 묶는 k-means를 실행합니다. 중심점과 각 점까지의 거리를 기준으로 군집을 갱신합니다.

```sh
python classical_lab.py --day 8
python classical_lab.py --day 8 --clusters 5 --out results/day08-k5
```

**확인:** 300개 합성 점의 색과 중심점, silhouette와 inertia를 봅니다. silhouette는 대체로 -1~1 범위의 분리 지표이고, inertia는 군집을 늘리면 작아지기 쉬우므로 단독으로 k를 고르기 어렵습니다.

**과제·점검:** k=2·3·5를 비교합니다. “군집 0”을 “정답 클래스 0”으로 부를 수 없는 이유와, 연구 자료에서 이 군집이 의미 있는지 확인할 추가 정보를 적습니다.

### 9일 · PCA와 차원 축소

**목표:** 13개 특성을 낮은 차원으로 압축해 보면서, 큰 분산을 보존하는 것과 정답 분류를 잘하는 것이 다름을 이해합니다.

```sh
python classical_lab.py --day 9
python classical_lab.py --day 9 --components 5 --out results/day09-pc5
```

**확인:** PCA는 train에서만 맞추고 validation을 투영합니다. 그림은 첫 두 성분이며, `metrics.csv`의 설명 분산 비율을 합하면 지정한 성분의 누적 보존량이 됩니다. 색은 해석을 위해 정답을 표시한 것으로 PCA 학습에는 쓰지 않습니다.

**과제·점검:** 2개와 5개 성분의 누적 비율을 비교합니다. 2차원에서 겹치는 점들이 원래 13차원에서도 반드시 겹친다고 말할 수 있는지 적습니다.

### 10일 · MLP와 경사 기반 학습

**목표:** 입력을 펼쳐 은닉층과 출력층을 통과시키고, loss의 기울기를 역전파해 가중치를 갱신하는 과정을 확인합니다. 아래 PyTorch 설치 안내를 먼저 진행합니다.

```sh
python train_cnn.py --model mlp --epochs 2 --train-limit 2000 --validation-limit 500 --test-limit 500 --out results/day10-mlp
```

**확인:** MNIST 픽셀 784개 → 은닉층 64개 → 숫자 10종을 예측합니다. epoch별 validation loss·accuracy와 `report.html`의 오분류를 확인합니다. 기본 실행은 test를 평가하지 않습니다.

**과제·점검:** `--lr 0.0001`과 기본 0.001을 비교합니다. 학습률은 사람이 정하는 조건이고 가중치는 데이터로 학습한다는 차이를 설명합니다. 다운로드가 어렵다면 `--dataset synthetic`으로 동작만 확인하되 결과 비교에서 데이터 종류를 표시합니다.

### 11일 · CNN과 이미지의 공간 구조

**목표:** MLP와 같은 MNIST·seed·샘플 수에서 합성곱의 특징을 비교합니다. 아래 브라우저 CNN으로 먼저 필터와 loss 변화를 보셔도 됩니다.

```sh
python train_cnn.py --model cnn --epochs 2 --train-limit 2000 --validation-limit 500 --test-limit 500 --out results/day11-cnn
```

**확인:** Conv → ReLU → Pooling을 거쳐 분류합니다. 10일의 지표와 비교하되 학습 시간과 모델 구조도 함께 기록합니다. CNN이 모든 데이터나 작은 학습 횟수에서 반드시 우수한 것은 아닙니다.

**과제·점검:** 모델과 학습 조건을 validation 기준으로 확정한 뒤에만 선택한 모델을 같은 seed·조건으로 재실행하며 `--evaluate-test`를 추가합니다. 이는 마지막 epoch 모델을 test에서 한 번 평가합니다. 다시 조건을 고르고 test를 반복 비교하면 최종 평가로 볼 수 없습니다.

### 12일 · Neo4j로 관계를 질의하기

**목표:** 특성 행렬과 다른 그래프 표현을 이해하고, 노드·관계·속성을 직접 조회합니다. 아래 Neo4j 설치·서버 준비 절을 따라 실행합니다.

```sh
python neo4j_lab.py seed
python neo4j_lab.py queries --out results/day12-neo4j
```

**확인:** 노드 7개·관계 9개, 연구자-주제 3행, 공통 주제 쌍 1행, 민지→소라 최단 경로 3관계를 확인합니다. 그래프 DB 조회 결과와 모델의 예측값을 구분합니다.

**과제·점검:** `graph.json`에 연구자 한 명과 `WORKS_ON` 관계를 추가하고 다시 seed합니다. 공통 주제 쌍이 늘어나는 이유를 설명합니다. 기존 데이터가 있는 서버에서는 아래의 실습 전용 초기화 명령만 사용합니다.

### 13일 · 준지도학습과 관계의 활용

**목표:** 모든 샘플에 라벨을 붙이기 어려울 때, 소수의 라벨과 라벨 없는 입력을 함께 쓰는 방법을 확인합니다. Label Spreading은 입력의 근접 관계를 이용해 라벨 정보를 전파합니다.

```sh
python classical_lab.py --day 13
python classical_lab.py --day 13 --labeled-fraction 0.1 --out results/day13-label10
```

**확인:** two-moons 합성 데이터의 train 안에서 클래스별 라벨 20%만 남깁니다. 같은 라벨 예산의 로지스틱 회귀와 Label Spreading을 validation에서 비교합니다. 나머지 학습 라벨은 `-1`로 숨기며 validation/test의 입력이나 정답을 학습에 넣지 않습니다.

**과제·점검:** 라벨 비율 0.1·0.2·0.5를 비교합니다. 가까운 점이 같은 클래스를 가질 것이라는 가정이 깨지면 왜 잘못 전파될지 적습니다. 이 근접 그래프는 12일의 Neo4j 그래프와 별개로 계산하며 DB·GNN 추가 설치는 필요 없습니다.

### 14일 · 모델 선택부터 보고서까지

**목표:** 점수 하나를 보고 끝내지 않고 재현 가능한 작은 실험을 완성합니다.

```sh
python classical_lab.py --day 14
```

**확인:** 1주차 Wine 데이터의 train+validation 80%를 개발 집합으로 묶습니다. 로지스틱 회귀·kNN·SVM·Random Forest를 3-fold CV의 macro F1로 비교하고 **선택된 모델 하나만** 보관해 둔 test 20%에서 평가합니다. `results.json`의 `selected_model`과 `test_evaluated`를 확인합니다. 동점이면 코드에 나열된 순서를 따릅니다.

**제출:** ZIP의 `experiment-log.md`에 다음을 적어 5분 정도 설명합니다. 문제와 데이터, 분할·seed·버전, baseline, CV 비교, 선택 이유, 최종 test 지표, 실패 사례, 한계와 다음 실험입니다. `metrics.csv`와 `plot.png`를 첨부합니다. 개인 연구 데이터로 바꾸는 과제는 시간 여유가 있을 때 별도로 진행합니다.

**완료 기준:** 회귀·분류·군집화를 구분하고, 전처리 누수를 피하며, validation/CV로 조건을 고르고 test를 마지막에 사용하는 이유를 설명할 수 있어야 합니다. 내장 데이터와 한 seed의 높은 점수만으로 새 연구 자료에서의 성능을 주장하지 않습니다. 실제 연구에서는 주체·시간 단위의 분할, 여러 seed와 충분한 표본 등 추가 설계가 필요합니다.

### 2주 뒤 이어갈 주제

다음에는 텍스트의 TF-IDF·Naive Bayes를 먼저 실행한 뒤 임베딩·Transformer를 비교하거나, 시계열의 시간 순서 분할, GNN의 메시지 전달, 강화학습의 상태·행동·보상으로 확장할 수 있습니다. 이번 과정에 모두 압축하기보다는 위 실험 기록을 완성한 다음 한 가지를 선택하는 편이 좋습니다.
<!-- curriculum:end -->


## Neo4j 상세 준비: 연구 협업 그래프

그래프 DB는 대상을 **노드**, 대상 사이의 연결을 **관계**로 표현합니다. 라벨은 노드의 종류, 속성은 이름 같은 값을 뜻합니다. Cypher는 이 패턴을 질의하는 언어입니다.

이번 데이터에는 연구자 3명, 주제 2개, 논문 2개가 있습니다. 예를 들어 `(민지)-[:WORKS_ON]->(그래프 DB)`는 민지가 그래프 DB를 연구한다는 관계입니다.

### 서버와 예제 데이터 준비

```sh
docker --version
docker compose version
```

macOS/Linux는 `cp .env.example .env`, PowerShell은 `Copy-Item .env.example .env`로 환경 파일을 만듭니다. 기본 비밀번호 `ResearchLabOnly123`은 로컬 실습용입니다.

```sh
docker compose up -d --wait --wait-timeout 180
python -m pip install -r requirements-neo4j.txt
python neo4j_lab.py seed
python neo4j_lab.py queries
```

비밀번호를 물으면 `.env`의 값을 입력합니다. `.env`는 Compose가 읽으며, Python은 입력받거나 `NEO4J_PASSWORD` 환경 변수를 사용합니다.

Neo4j Browser는 `http://127.0.0.1:17474`에서 열고, 연결 URI는 `bolt://127.0.0.1:17687`, 사용자와 DB는 `neo4j`를 사용합니다. 웹 UI와 드라이버 포트는 서로 다릅니다.

`seed` 실행 결과는 **노드 7개, 관계 9개**입니다. 같은 명령을 다시 실행해도 `MERGE`와 고유성 제약으로 중복을 방지합니다. 실습 데이터에는 `ResearchLab` 라벨과 `lab_id: research-lab-v1` 표시를 붙입니다.

### 직접 실행할 Cypher

Browser에서 다음 쿼리를 실행하면 연구자와 주제를 찾습니다. 노드는 `()`, 관계는 `-[:종류]->`로 표현합니다.

```cypher
MATCH (r:ResearchLab:Researcher {lab_id: 'research-lab-v1'})
      -[:WORKS_ON]->(t:ResearchLab:Topic {lab_id: 'research-lab-v1'})
RETURN r.name AS researcher, t.name AS topic
ORDER BY researcher
```

같은 주제를 연구하는 두 사람을 찾는 쿼리입니다. `a.id < b.id`는 자기 자신과 순서만 다른 중복 쌍을 제외합니다.

```cypher
MATCH (a:ResearchLab:Researcher {lab_id: 'research-lab-v1'})
      -[:WORKS_ON]->(t:ResearchLab:Topic {lab_id: 'research-lab-v1'})
      <-[:WORKS_ON]-(b:ResearchLab:Researcher {lab_id: 'research-lab-v1'})
WHERE a.id < b.id
RETURN a.name, b.name, t.name
```

예상 결과는 연구자-주제 **3행**, 같은 주제의 연구자 쌍 **1행**, 민지에서 소라까지 방향을 무시한 최단 경로의 관계 수 **3**입니다. 최단 경로가 여러 개라면 중간 노드는 달라질 수 있습니다.

`results/neo4j/`에서 CSV 3개와 `results.json`을 확인합니다. `queries.cypher`에는 최단 경로 쿼리도 들어 있습니다. Python 없이 데이터를 넣으려면 `seed.cypher` 문장을 순서대로 실행합니다.

### 종료와 실습 데이터 초기화

```sh
docker compose down
```

이 명령은 컨테이너를 종료하고 데이터 volume은 유지합니다. 서버가 실행 중일 때 다음 명령을 쓰면 이번 실습 노드만 지웁니다.

```sh
python neo4j_lab.py reset --confirm research-lab-v1
```

다른 데이터까지 지우는 전체 삭제 쿼리는 실습에 필요하지 않습니다.

## 신경망 실습에서 알아둘 내용: 먼저 알아둘 내용

- **입력과 정답**: 이미지의 픽셀값을 입력하고, 숫자 또는 선의 종류를 정답 라벨로 사용합니다.
- **MLP**: 픽셀을 일렬로 펼쳐 완전연결층에 넣습니다.
- **CNN**: 작은 합성곱 필터를 이미지 위에서 이동시키며 특징을 구합니다. ReLU는 음수를 0으로, pooling은 공간 크기를 줄입니다.
- **loss와 학습률**: 오차를 loss로 계산하고 역전파로 기울기를 구해 가중치를 바꿉니다. 학습률은 한 번에 바꾸는 크기입니다.
- **epoch와 batch**: 학습 데이터를 한 바퀴 보는 횟수와, 한 번의 업데이트에 사용하는 데이터 수입니다.
- **학습·검증·테스트**: 학습에 쓰지 않은 데이터로 확인해야 합니다. 실제 연구에서 조건을 고를 때는 validation set을 따로 두고 최종 test set은 남겨 둡니다.

브라우저 CNN은 12×12 가로·세로선 2종을 사용하며, 학습 80개와 별도 검증 40개를 고정 seed로 만듭니다. 구조는 `Conv 3×3×4 → ReLU → 전역 평균 → Linear 4→2`입니다. 마지막 분류층뿐 아니라 합성곱 필터도 학습합니다.

이후 Python 실습은 **MNIST 28×28 손글씨 숫자 10종**을 사용합니다. 데이터와 모델이 다르므로 두 예제의 정확도를 직접 비교하지 않습니다.

## PyTorch 상세 준비와 MNIST 실행

macOS:

```sh
python -m pip install -r requirements-cnn.txt
```

Windows/Linux CPU:

```sh
python -m pip install -r requirements-cnn.txt --index-url https://download.pytorch.org/whl/cpu
```

설치 확인 후 같은 데이터 수로 MLP와 CNN을 각각 실행합니다.

```sh
python -c "import torch, torchvision; print(torch.__version__, torchvision.__version__)"
python train_cnn.py --model mlp --epochs 1 --train-limit 2000 --test-limit 500 --out results/mlp
python train_cnn.py --model cnn --epochs 1 --train-limit 2000 --test-limit 500 --out results/cnn
```

최초 실행은 MNIST를 `data/`에 내려받습니다. 원본 학습 60,000개에서 학습·검증용 인덱스를 겹치지 않게 선택하고, 공식 테스트 10,000개는 별도로 남깁니다. 기본값은 학습 2,000개·검증 500개·테스트 후보 500개입니다. 기본 실행에서는 테스트를 평가하지 않습니다. 작은 CPU 실습이므로 특정 정확도를 보장하지 않습니다.

CNN의 핵심 구조입니다. 실행 가능한 전체 코드는 ZIP과 노트북에 포함되어 있습니다.

```python
model = nn.Sequential(
    nn.Conv2d(1, 8, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
    nn.Conv2d(8, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
    nn.Flatten(), nn.Linear(16 * 7 * 7, 10),
)
```

학습은 `model.train()`, 평가는 `model.eval()`과 `torch.no_grad()`를 사용합니다. `CrossEntropyLoss`에는 softmax 이전 logits를 넣고, 보고서용 예측 확률을 구할 때만 softmax를 적용합니다.

각 출력 폴더에서 다음 파일을 확인합니다.

| 파일 | 확인할 내용 |
| --- | --- |
| `report.html` | 검증 이미지 12개, 정답과 예측. `--evaluate-test` 사용 시 테스트 이미지. 브라우저로 열기 |
| `metrics.csv` | epoch별 학습 loss, 검증 loss와 정확도 |
| `results.json` | 실행 조건, 버전, 지표와 개별 예측 확률 |
| `weights.pt` | 학습한 모델의 `state_dict` |

`--epochs 3` 또는 `--train-limit 10000`으로 바꾸어 비교합니다. 같은 `--out` 경로를 쓰면 기존 결과를 덮어씁니다.

인터넷 없이 동작만 점검하려면 `--dataset synthetic`을 추가합니다. 이 모드는 합성 선 이미지 2종을 사용하므로 MNIST 성능 검증을 대신하지 않습니다.

## Jupyter / Colab과 결과 보관

`cnn_lab.ipynb`를 Jupyter에서 열거나 Colab에 업로드합니다. 코드가 노트북 안에 있어 `.py` 파일을 따로 올릴 필요가 없습니다. 위에서 아래로 실행하면 설치 확인, 모델 정의, 학습, HTML 보고서를 볼 수 있습니다. Colab 결과는 세션 종료 전에 내려받습니다.

다음 조건을 하나씩 바꾸고 결과와 이유를 기록해 보시면 됩니다.

1. 그래프에 연구자와 주제를 추가하면 같은 주제의 연구자 쌍은 몇 개가 되는가?
2. 최단 경로의 방향을 제한하면 결과가 어떻게 달라지는가?
3. CNN의 학습률 0.1, 0.3, 0.8에서 loss 곡선은 어떻게 달라지는가?
4. MLP와 CNN을 같은 seed·데이터 수·epoch로 비교했을 때 오분류 이미지에 차이가 있는가?

## 실행이 막힐 때

| 상황 | 먼저 확인할 내용 |
| --- | --- |
| Docker 연결 실패 | Docker 앱/서비스 실행 여부, `docker info` |
| 포트 충돌 | Compose의 왼쪽 host 포트 변경 후 Python `--uri`도 변경 |
| Neo4j 인증 실패 | 기존 volume의 암호는 `.env`만 바꿔도 변경되지 않음 |
| 준비 대기 실패 | `docker compose logs neo4j`, 사용 가능한 메모리 |
| Python 모듈 없음 | 가상환경의 Python으로 설치하고 실행했는지 확인 |
| MNIST 다운로드 실패 | 인터넷·기관 프록시 확인. 합성 데이터는 코드 점검용 |
| 학습이 오래 걸림 | `--train-limit 500 --test-limit 100 --epochs 1`로 축소 |

## 참고한 공식 문서

- [scikit-learn 시작하기](https://scikit-learn.org/stable/getting_started.html)
- [모델 선택과 교차검증](https://scikit-learn.org/stable/modules/cross_validation.html)
- [선형 모델](https://scikit-learn.org/stable/modules/linear_model.html)
- [앙상블](https://scikit-learn.org/stable/modules/ensemble.html)
- [군집화](https://scikit-learn.org/stable/modules/clustering.html)
- [PCA](https://scikit-learn.org/stable/modules/decomposition.html#pca)
- [준지도학습](https://scikit-learn.org/stable/modules/semi_supervised.html)
- [데이터 누수와 전처리 주의점](https://scikit-learn.org/stable/common_pitfalls.html)
- [Neo4j Docker 실행](https://neo4j.com/docs/operations-manual/current/docker/introduction/)
- [Neo4j Python 쿼리 실행](https://neo4j.com/docs/python-manual/current/query-simple/)
- [PyTorch 설치](https://pytorch.org/get-started/locally/)
- [PyTorch 기초 튜토리얼](https://docs.pytorch.org/tutorials/beginner/basics/intro.html)
- [torchvision MNIST](https://docs.pytorch.org/vision/main/generated/torchvision.datasets.MNIST.html)
- [CrossEntropyLoss](https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html)
