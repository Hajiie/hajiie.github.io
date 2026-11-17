---
title: "연구실 실습: Neo4j 그래프 DB와 MLP·CNN 기초"
published: 2026-03-20
updated: 2026-11-17
draft: true
practice: true
description: "준비부터 실행까지: 연구 협업 그래프 탐색, 작은 CNN 학습, Neo4j·PyTorch 실습 코드."
tags: [Neo4j, Python, PyTorch, CNN, 실습]
category: 실습
lang: ko
---

연구실에서 함께 실행해 볼 실습 초안입니다. 그래프 DB의 관계 탐색과 신경망의 학습 과정을 작은 데이터로 확인합니다. 준비 과정부터 결과 파일을 확인하는 순서까지 적었습니다.

작성일은 Linker 글보다 앞선 **2026년 3월 20일**로 두었습니다. 코드와 설치 안내는 **2026년 11월 17일** 기준으로 점검합니다. 아직 공개하지 않은 초안입니다.

## 먼저 브라우저에서 실행하기

[아래 실습 화면으로 이동](#research-lab-playground)해서 두 예제를 실행할 수 있습니다.

1. **그래프 탐색**: 질문을 선택하고 실행하면 관계와 결과 표를 확인합니다. 결과는 CSV로 내려받습니다.
2. **CNN 학습**: 학습 횟수와 학습률을 정하고 실행합니다. loss, 검증 정확도, 필터 변화와 예측을 확인하고 기록·가중치를 내려받습니다.
3. **실습 코드 ZIP**: Neo4j 설정, Python 코드, Cypher, Jupyter 노트북과 준비 안내를 한 번에 받습니다.

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

## 2. Neo4j: 연구 협업 그래프

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

## 3. MLP와 CNN: 먼저 알아둘 내용

- **입력과 정답**: 이미지의 픽셀값을 입력하고, 숫자 또는 선의 종류를 정답 라벨로 사용합니다.
- **MLP**: 픽셀을 일렬로 펼쳐 완전연결층에 넣습니다.
- **CNN**: 작은 합성곱 필터를 이미지 위에서 이동시키며 특징을 구합니다. ReLU는 음수를 0으로, pooling은 공간 크기를 줄입니다.
- **loss와 학습률**: 오차를 loss로 계산하고 역전파로 기울기를 구해 가중치를 바꿉니다. 학습률은 한 번에 바꾸는 크기입니다.
- **epoch와 batch**: 학습 데이터를 한 바퀴 보는 횟수와, 한 번의 업데이트에 사용하는 데이터 수입니다.
- **학습·검증·테스트**: 학습에 쓰지 않은 데이터로 확인해야 합니다. 실제 연구에서 조건을 고를 때는 validation set을 따로 두고 최종 test set은 남겨 둡니다.

브라우저 CNN은 12×12 가로·세로선 2종을 사용하며, 학습 80개와 별도 검증 40개를 고정 seed로 만듭니다. 구조는 `Conv 3×3×4 → ReLU → 전역 평균 → Linear 4→2`입니다. 마지막 분류층뿐 아니라 합성곱 필터도 학습합니다.

이후 Python 실습은 **MNIST 28×28 손글씨 숫자 10종**을 사용합니다. 데이터와 모델이 다르므로 두 예제의 정확도를 직접 비교하지 않습니다.

## 4. PyTorch로 MNIST 실행하기

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

최초 실행은 MNIST를 `data/`에 내려받습니다. 원본 학습 60,000개와 테스트 10,000개에서 각각 일부를 선택합니다. 작은 CPU 실습이므로 특정 정확도를 보장하지 않습니다.

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
| `report.html` | 테스트 이미지 12개, 정답과 예측. 브라우저로 열기 |
| `metrics.csv` | epoch별 학습 loss, 테스트 loss와 정확도 |
| `results.json` | 실행 조건, 버전, 지표와 개별 예측 확률 |
| `weights.pt` | 학습한 모델의 `state_dict` |

`--epochs 3` 또는 `--train-limit 10000`으로 바꾸어 비교합니다. 같은 `--out` 경로를 쓰면 기존 결과를 덮어씁니다.

인터넷 없이 동작만 점검하려면 `--dataset synthetic`을 추가합니다. 이 모드는 합성 선 이미지 2종을 사용하므로 MNIST 성능 검증을 대신하지 않습니다.

## 5. Jupyter / Colab과 다음 실험

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

- [Neo4j Docker 실행](https://neo4j.com/docs/operations-manual/current/docker/introduction/)
- [Neo4j Python 쿼리 실행](https://neo4j.com/docs/python-manual/current/query-simple/)
- [PyTorch 설치](https://pytorch.org/get-started/locally/)
- [PyTorch 기초 튜토리얼](https://docs.pytorch.org/tutorials/beginner/basics/intro.html)
- [torchvision MNIST](https://docs.pytorch.org/vision/main/generated/torchvision.datasets.MNIST.html)
- [CrossEntropyLoss](https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html)
