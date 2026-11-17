---
title: "머신러닝·Neo4j 2주 실습"
published: 2026-03-20
updated: 2026-11-17
draft: true
practice: true
description: "회귀·분류·앙상블·군집화·PCA·신경망·준지도학습과 Neo4j 실습 정리."
tags: [머신러닝, Neo4j, Python, scikit-learn, PyTorch, 실습]
category: 실습
lang: ko
---

[브라우저 실습 및 코드 다운로드](#research-lab-playground)

## 실습 환경

- Python 3.11, scikit-learn, PyTorch 사용.
- Neo4j는 Docker Compose로 실행.
- 신경망 학습은 CPU 기준.
- 다운로드한 ZIP을 풀고 `research-lab` 폴더에서 명령 실행.

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

```sh
python classical_lab.py --day 1
```

비교 항목

- `results.json`의 데이터 분할 수와 baseline accuracy.
- `--seed 17 --out results/day01-seed17`로 분할을 바꾼 결과.

### 2일 · 선형 회귀와 Ridge

- 선형 회귀: 입력의 가중합으로 연속값 예측.
- Ridge: L2 규제를 적용해 계수 크기 제한. `alpha`가 규제 강도.
- MAE·RMSE는 작을수록 오차가 작음. R²는 음수가 될 수도 있음.

```sh
python classical_lab.py --day 2
python classical_lab.py --day 2 --alpha 100 --out results/day02-alpha100
```

비교 항목

- 평균값 기준 모델, 선형 회귀, Ridge의 MAE·RMSE.
- 실제값–예측값 그래프와 `alpha=1, 10, 100`의 차이.

### 3일 · 로지스틱 회귀

- 로지스틱 회귀: 클래스 분류에 사용하는 선형 모델.
- accuracy: 전체 샘플 중 정답을 맞힌 비율.
- macro F1: 클래스별 F1의 단순 평균. F1은 precision과 recall을 함께 반영.

```sh
python classical_lab.py --day 3
```

비교 항목

- baseline과 로지스틱 회귀의 validation accuracy·macro F1.
- `predictions.csv`의 오분류와 클래스별 차이.

### 4일 · kNN과 SVM

- kNN: 가까운 이웃의 라벨로 분류.
- SVM: 클래스 사이의 결정 경계를 학습. 예제는 RBF 커널 사용.
- `StandardScaler`: train의 평균·표준편차로 표준화하고 validation에 동일하게 적용.

```sh
python classical_lab.py --day 4
python classical_lab.py --day 4 --neighbors 9 --out results/day04-k9
```

비교 항목

- 표준화 전후 kNN과 SVM의 validation 점수.
- 이웃 수 `k=3, 5, 9`에 따른 차이.

### 5일 · 결정 트리

- 조건을 순서대로 나누어 예측하는 모델.
- 깊이가 작으면 표현력 제한, 깊이가 커지면 train에 과도하게 맞춰질 수 있음.
- train과 validation 점수 차이로 과소적합·과적합 확인.

```sh
python classical_lab.py --day 5
python classical_lab.py --day 5 --depth 1 --out results/day05-depth1
```

비교 항목

- 깊이 제한 트리와 무제한 트리.
- `--depth 1, 3, 8`에서 train/validation 점수 변화.

### 6일 · Random Forest와 Boosting

- Random Forest: 샘플·특성을 달리한 여러 트리의 예측 결합.
- Gradient Boosting: 이전 오차를 줄이는 모델을 순차적으로 추가.

```sh
python classical_lab.py --day 6
```

비교 항목

- 같은 분할에서 단일 트리, Random Forest, Gradient Boosting의 점수.
- 코드의 `n_estimators` 변경에 따른 점수와 실행 시간.

### 7일 · 교차검증과 모델 선택

- 학습 데이터를 3개 fold로 나누어 kNN의 `k=3, 5, 9` 비교.
- `GridSearchCV`로 CV macro F1이 가장 높은 조건 선택.
- 선택한 모델만 validation에서 평가.
- scaler는 Pipeline 안에 배치해 fold 사이의 정보 누수 방지.

```sh
python classical_lab.py --day 7
```

비교 항목

- `train CV`의 평균·표준편차와 선택 모델의 `validation` 점수.
- 1~6일 결과의 전처리, 모델, 지표, 선택 조건 정리.

### 8일 · k-means

- 가까운 중심점에 샘플을 배정하고 중심을 갱신하는 군집화 방법.
- silhouette: 군집 내부의 밀집도와 다른 군집과의 분리 정도. 범위는 대체로 -1~1.
- inertia: 중심점까지 거리 제곱의 합. 군집 수가 늘면 작아지기 쉬움.

```sh
python classical_lab.py --day 8
python classical_lab.py --day 8 --clusters 5 --out results/day08-k5
```

비교 항목

- `k=2, 3, 5`의 군집 그림, silhouette, inertia.
- 군집 번호와 정답 클래스의 차이.

### 9일 · PCA

- 라벨 없이 분산이 큰 방향을 찾아 차원 축소.
- train으로 fit한 뒤 validation을 투영. 그림은 첫 두 주성분.
- 그림의 색은 정답 표시용이며 PCA 학습에는 사용하지 않음.

```sh
python classical_lab.py --day 9
python classical_lab.py --day 9 --components 5 --out results/day09-pc5
```

비교 항목

- 2개·5개 성분의 누적 설명 분산 비율.
- 2차원 투영에서 클래스가 겹치는 구간.

### 10일 · MLP

- MNIST 픽셀 784개 → 은닉층 64개 → 숫자 10종 분류.
- loss의 기울기를 역전파해 가중치 갱신.
- epoch: 학습 데이터 전체를 보는 횟수. batch: 한 번의 업데이트에 사용하는 샘플 수.

```sh
python train_cnn.py --model mlp --epochs 2 --train-limit 2000 --validation-limit 500 --test-limit 500 --out results/day10-mlp
```

비교 항목

- epoch별 validation loss·accuracy와 오분류 이미지.
- `--lr 0.0001`과 기본 학습률 `0.001`의 차이.

### 11일 · CNN

- 합성곱 필터로 이미지의 공간적 특징 추출.
- Conv → ReLU → Pooling → Linear 순서로 분류.
- 10일과 같은 MNIST·seed·샘플 수·epoch 사용.

```sh
python train_cnn.py --model cnn --epochs 2 --train-limit 2000 --validation-limit 500 --test-limit 500 --out results/day11-cnn
```

비교 항목

- MLP와 CNN의 validation loss·accuracy, 오분류, 학습 시간.
- validation 기준으로 조건 확정 후 선택 모델에 `--evaluate-test`를 추가해 최종 test 평가.

### 12일 · Neo4j

- 노드·관계·속성으로 연구자, 주제, 논문 표현.
- Cypher로 연구 주제, 공통 주제, 최단 경로 조회.

```sh
python neo4j_lab.py seed
python neo4j_lab.py queries --out results/day12-neo4j
```

확인 항목

- 노드 7개·관계 9개.
- 연구자–주제 3행, 공통 주제 쌍 1행, 민지→소라 최단 경로 3관계.
- `graph.json`에 연구자와 `WORKS_ON` 관계를 추가한 뒤 공통 주제 쌍 변화.

### 13일 · Label Spreading

- 소수의 라벨과 입력 간 근접 관계를 이용하는 준지도학습.
- train의 클래스별 라벨 20%만 남기고 나머지는 `-1`로 설정.
- 같은 라벨 수의 로지스틱 회귀와 validation 점수 비교.
- 근접 그래프는 입력에서 계산하며 Neo4j와는 별개.

```sh
python classical_lab.py --day 13
python classical_lab.py --day 13 --labeled-fraction 0.1 --out results/day13-label10
```

비교 항목

- 라벨 비율 `0.1, 0.2, 0.5`에 따른 점수 변화.
- 가까운 입력끼리 라벨이 비슷하다는 가정과 잘못된 라벨 전파.

### 14일 · 종합 실험

- Wine의 train+validation 80%를 개발 집합으로 사용.
- 로지스틱 회귀·kNN·SVM·Random Forest를 3-fold CV macro F1로 비교.
- CV 점수가 가장 높은 모델 하나만 test 20%에서 평가. 동점이면 코드의 나열 순서 적용.

```sh
python classical_lab.py --day 14
```

정리 항목

- 데이터, 분할, seed, 패키지 버전.
- baseline, CV 비교 결과, 선택 모델과 선택 이유.
- 최종 test 지표, 오분류, 다음 실험.

### 실행 결과

`results/day01/`처럼 날짜별 폴더에 저장. `--out results/day04-k9`로 실험별 경로 지정.

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

- macOS / Linux: `cp .env.example .env`
- PowerShell: `Copy-Item .env.example .env`

```sh
docker compose up -d --wait --wait-timeout 180
python -m pip install -r requirements-neo4j.txt
```

| 항목 | 값 |
| --- | --- |
| Neo4j Browser | `http://127.0.0.1:17474` |
| 드라이버 URI | `bolt://127.0.0.1:17687` |
| 사용자 / DB | `neo4j` |
| 기본 비밀번호 | `ResearchLabOnly123` — 로컬 실습용 |

Python 실행 시 `.env`의 비밀번호 입력. `NEO4J_PASSWORD` 환경 변수를 설정한 경우 해당 값 사용.

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
최단 경로는 관계 방향을 무시하며, 전체 쿼리는 `queries.cypher`에 포함.
Python 없이 데이터 생성 시 `seed.cypher` 사용.

### 종료와 초기화

컨테이너 종료. 데이터 volume은 유지.

```sh
docker compose down
```

실행 중인 서버에서 실습 노드만 삭제.

```sh
python neo4j_lab.py reset --confirm research-lab-v1
```

## Jupyter / Colab

- `ml_basics.ipynb`: 1~9일, 13~14일. `DAY` 값으로 실행 날짜 선택.
- `cnn_lab.ipynb`: 10~11일. `--model`로 MLP·CNN 선택.
- 설치 확인 → 코드 정의 → 학습 → 보고서 순서로 셀 실행.
- Colab에서 결과 파일은 세션 종료 전 다운로드.

## 트러블슈팅

| 문제 | 확인 및 처리 |
| --- | --- |
| Docker 연결 실패 | Docker 앱/서비스, `docker info` 확인 |
| 포트 충돌 | Compose의 host 포트와 Python `--uri`를 함께 변경 |
| Neo4j 인증 실패 | 기존 volume의 암호는 `.env` 수정만으로 변경되지 않음 |
| DB 준비 대기 실패 | `docker compose logs neo4j`, 메모리 확인 |
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
