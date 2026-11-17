# 머신러닝·Neo4j 2주 실습

- `curriculum.md`: 날짜별 개념·명령·비교 항목.
- `experiment-log.md`: 실험 기록 양식.
- 브라우저 CNN: 12×12 합성 선 이미지. Python 신경망 예제: 28×28 MNIST.

## 1. 공통 준비

- Python 3.11, 터미널, 코드 편집기, 최신 브라우저를 준비합니다.
- Neo4j를 실행하려면 Docker와 Compose v2가 필요합니다. Docker Desktop 또는 Docker Engine을 먼저 실행합니다.
- PyTorch 실습은 CPU로 실행하며 GPU/CUDA가 필요하지 않습니다.
- 최초 설치, Neo4j 이미지, MNIST 다운로드에는 인터넷과 디스크 여유 공간이 필요합니다.
- ZIP을 압축 해제한 `research-lab` 폴더에서 명령을 실행합니다.

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

PowerShell에서 활성화가 차단되면 정책을 바꾸지 않아도 됩니다.
아래 명령의 `python`을 `.\.venv\Scripts\python.exe`로 바꾸어 실행합니다.
가상환경을 활성화한 뒤 `python --version`으로 사용할 인터프리터를 확인합니다.

## 날짜별 시작 명령

공통 준비 뒤 먼저 아래를 실행합니다.

```sh
python -m pip install -r requirements-ml.txt
python classical_lab.py --day 1
```

- 1~9일: 같은 명령의 `--day`를 해당 날짜로 변경합니다.
- 10~11일: 아래 PyTorch 설치 후 `train_cnn.py`의 `--model mlp` / `--model cnn`을 실행합니다.
- 12일: 아래 Neo4j 준비·실행을 따릅니다.
- 13~14일: `python classical_lab.py --day 13` / `--day 14`를 실행합니다.
- 날짜별 개념·실행 명령·비교 항목은 `curriculum.md`에 있습니다.

`results/day01/report.html`을 브라우저로 열면 그림과 지표를 바로 볼 수 있습니다.
`plot.png`, `metrics.csv`, `predictions.csv`, `split.json`, `results.json`도 생성됩니다.
`--out results/day04-k9`처럼 실험별 출력 폴더를 지정합니다. 같은 폴더는 덮어씁니다.

1~9일과 13~14일은 패키지 설치 후 추가 데이터 다운로드가 없습니다.
Wine 내장 데이터와 합성 데이터를 사용하며 실제 연구 자료의 성능을 나타내지 않습니다.
표준화는 train에만 맞추고, CV에서는 Pipeline 내부에서 fold별로 다시 맞춥니다.
최종 test는 14일차에서 CV로 선택한 모델 하나만 평가합니다.
8일차 군집화는 전체 합성 점군 탐색이며 정확도 평가와 구분합니다.

## 2. Neo4j 실행

```sh
docker --version
docker compose version
```

macOS/Linux는 `cp .env.example .env`, PowerShell은 `Copy-Item .env.example .env`를 실행합니다.
`.env`의 기본 비밀번호는 **로컬 실습 전용** `ResearchLabOnly123`입니다.

```sh
docker compose up -d --wait --wait-timeout 180
python -m pip install -r requirements-neo4j.txt
python neo4j_lab.py seed
python neo4j_lab.py queries
```

Python 실행 시 비밀번호를 물으면 `.env`에 설정한 값을 입력합니다.
`NEO4J_PASSWORD` 환경 변수를 이미 설정했다면 그 값을 사용합니다.

- Neo4j Browser: http://127.0.0.1:17474
- 연결 URI: `bolt://127.0.0.1:17687`
- 사용자와 DB: `neo4j`
- 17474는 웹 UI, 17687은 드라이버 연결용 포트입니다. 컨테이너 내부 포트는 각각 7474와 7687입니다.

`seed`는 `ResearchLab` 라벨과 `lab_id: research-lab-v1` 표시가 있는 실습 노드를 만듭니다.
같은 명령을 다시 실행해도 `MERGE`로 중복을 만들지 않습니다.
다른 라벨/실습 ID의 기존 데이터는 지우지 않습니다.

예상 결과:

```json
{"nodes": 7, "relationships": 9}
```

`queries`는 연구자-주제 3개, 같은 주제의 연구자 쌍 1개, 민지→소라 최단 경로의 관계 수 3을 반환합니다.
최단 경로가 여러 개라면 중간 노드가 달라도 관계 수는 같습니다. 방향은 무시하는 탐색입니다.
`results/neo4j/`에 `topics.csv`, `shared.csv`, `path.csv`, `results.json`이 생성됩니다.

Browser에서 직접 실행하려면 `queries.cypher`의 쿼리를 하나씩 선택해 실행합니다.
`seed.cypher`는 Python 없이 같은 실습 그래프를 만들 때 쓰는 대안이며, 문장을 순서대로 실행합니다.

실습 종료:

```sh
docker compose down
```

컨테이너는 종료되지만 이름 있는 volume의 데이터는 유지됩니다.
실습 그래프만 초기화하려면 서버가 실행 중일 때 다음 명령을 명시적으로 실행합니다.

```sh
python neo4j_lab.py reset --confirm research-lab-v1
```

다른 실습이나 운영 DB에서 전체 노드를 지우는 명령은 사용하지 않습니다.

## 3. PyTorch MLP/CNN 설치

macOS:

```sh
python -m pip install -r requirements-cnn.txt
```

Windows/Linux CPU:

```sh
python -m pip install -r requirements-cnn.txt --index-url https://download.pytorch.org/whl/cpu
```

환경에 맞는 설치 명령은 공식 안내에서 확인합니다: https://pytorch.org/get-started/locally/

```sh
python -c "import torch, torchvision; print(torch.__version__, torchvision.__version__)"
```

## 4. MNIST: 먼저 MLP, 다음 CNN

```sh
python train_cnn.py --model mlp --epochs 1 --train-limit 2000 --test-limit 500 --out results/mlp
python train_cnn.py --model cnn --epochs 1 --train-limit 2000 --test-limit 500 --out results/cnn
```

처음에는 MNIST를 `data/`에 내려받습니다. 다음 실행부터는 다운로드한 데이터를 재사용합니다.
공식 학습 60,000개에서 학습 2,000개·검증 500개를 겹치지 않게 선택합니다.
공식 테스트 10,000개 중 500개는 최종 평가용으로 남깁니다. 기본 실행에서는 test를 평가하지 않습니다.
`--epochs 3`이나 `--train-limit 10000`으로 조건을 바꾸어 비교할 수 있습니다.
예측이 같지 않을 수 있으므로 특정 정확도를 보장하는 예제가 아닙니다.

출력 폴더:

- `report.html`: 브라우저로 열어 검증 이미지 12개와 정답/예측 확인. 최종 test 옵션 사용 시 test 이미지 표시
- `metrics.csv`: epoch별 train loss, validation loss, validation accuracy
- `results.json`: 설정, 버전, 지표와 개별 예측 확률
- `weights.pt`: 학습한 가중치. 앱이 실행 중인 모델의 `state_dict`만 저장

학습 코드는 `model.train()`과 `model.eval()`을 구분하고, 평가는 `torch.no_grad()` 안에서 수행합니다.
`CrossEntropyLoss`에는 softmax 이전 logits를 넣습니다. softmax는 보고서의 예측 확률을 계산할 때만 사용합니다.
`--validation-limit 500`으로 검증 샘플 수를 정합니다. 조건은 validation 결과로 고릅니다.
조건을 확정한 뒤 선택한 모델을 같은 seed와 조건으로 재실행하며 `--evaluate-test`를 추가하면
마지막 모델만 test에서 한 번 평가합니다. `results.json`의 `final_test`에 저장됩니다.
반복해서 test를 보고 조건을 고르면 더는 독립적인 최종 평가가 아닙니다.

인터넷 없이 코드의 동작만 확인하려면:

```sh
python train_cnn.py --dataset synthetic --epochs 2 --train-limit 128 --test-limit 64 --out results/synthetic
```

이 모드는 합성 선 이미지 2종을 사용하므로 MNIST 성능 검증 결과가 아닙니다.

## 5. Jupyter / Colab

`ml_basics.ipynb`(1~9·13~14일) 또는 `cnn_lab.ipynb`(10~11일)를 Jupyter에서 열거나 Colab에 업로드합니다.
노트북 안에 학습 코드가 포함되어 있어 `.py` 파일을 추가 업로드하지 않아도 됩니다.
필요한 패키지가 없는 경우에만 첫 셀이 설치합니다. GPU는 선택하지 않아도 됩니다.
학습 셀을 실행하고 마지막 셀에서 보고서와 CSV를 확인합니다.
Colab 런타임의 결과는 영구 저장되지 않으므로 `results/` 파일을 내려받습니다.

## 6. 막히는 지점

| 상황 | 확인할 것 |
| --- | --- |
| Docker 연결 실패 | Docker 앱/서비스 실행 여부와 `docker info` |
| 포트 사용 중 | 다른 프로그램을 종료하는 대신 compose의 왼쪽 host 포트를 변경하고 Python `--uri`도 맞추기 |
| Neo4j 인증 실패 | 기존 volume은 `.env` 비밀번호 변경만으로 암호가 바뀌지 않음. 기존 DB의 암호 사용 |
| DB 준비 대기 실패 | `docker compose logs neo4j`와 사용 가능한 메모리 확인 |
| Python 모듈 없음 | 가상환경의 Python으로 설치/실행했는지 확인 |
| MNIST 다운로드 실패 | 인터넷/기관 프록시 확인. `synthetic`은 코드 확인용 대안 |
| 학습이 오래 걸림 | `--train-limit 500 --test-limit 100 --epochs 1`로 줄이기 |
| 결과가 이전 것과 다름 | model, seed, 데이터 수, 패키지 버전 비교. 같은 `--out`은 결과를 덮어씀 |

## 참고

- https://scikit-learn.org/stable/getting_started.html
- https://scikit-learn.org/stable/modules/cross_validation.html
- https://scikit-learn.org/stable/modules/semi_supervised.html

- https://neo4j.com/docs/operations-manual/current/docker/introduction/
- https://neo4j.com/docs/python-manual/current/query-simple/
- https://docs.pytorch.org/tutorials/beginner/basics/intro.html
- https://docs.pytorch.org/vision/main/generated/torchvision.datasets.MNIST.html
- https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html
