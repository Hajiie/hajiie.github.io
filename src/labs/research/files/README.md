# 머신러닝·Neo4j 2주 실습

## 폴더 구성

- `day01`~`day14`: 해당 일자의 `lab.py`, `README.md`, `requirements.txt`.
- Python 학습 예제의 `lab.ipynb`: 코드가 포함된 Jupyter / Colab 노트북.
- `day12`: Neo4j Docker 설정, 그래프 데이터, Cypher 쿼리.
- `curriculum.md`: 날짜별 개념·명령·결과 해석.
- `experiment-log.md`: 실험 기록 양식.

명령은 압축을 푼 `research-lab` 폴더 기준. `python day01/lab.py` 또는 해당 폴더 안에서 `python lab.py`로 실행 가능. 각 파일은 다른 날짜의 코드 없이 실행하며 결과는 해당 폴더의 `results/`에 저장.

## 공통 준비

Python 3.11과 터미널 사용. Neo4j에는 Docker Compose v2 필요. PyTorch는 CPU 실행.

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

PowerShell 활성화가 차단되면 `python` 대신 `.\.venv\Scripts\python.exe` 사용.

## 1~9일, 13~14일

```sh
python -m pip install -r requirements-ml.txt
python day01/lab.py
python day02/lab.py
```

다음 날짜는 경로의 숫자를 변경. 개별 의존성은 `python -m pip install -r day01/requirements.txt`로도 설치 가능.

내장 Wine 데이터와 합성 데이터를 사용하며 패키지 설치 후 추가 데이터 다운로드 없음.
train/validation/test를 분리하고 표준화·PCA는 train에만 fit. 교차검증에서는 Pipeline 안에서 fold별로 fit.
14일차는 CV로 선택한 모델 하나만 test에서 평가. 8일차는 전체 합성 점군의 군집 탐색.

결과 파일

- `report.html`: 그래프와 지표를 포함한 보고서. 브라우저로 열기.
- `plot.png`, `metrics.csv`, `predictions.csv`: 그래프·지표·샘플별 결과.
- `split.json`, `results.json`: 분할 인덱스·실행 조건·버전·지표.

```sh
python day04/lab.py --neighbors 9 --out day04/results-k9
```

같은 `--out` 경로는 기존 결과를 덮어씀.

## 10~11일: PyTorch

macOS

```sh
python -m pip install -r requirements-cnn.txt
```

Windows / Linux CPU

```sh
python -m pip install -r requirements-cnn.txt --index-url https://download.pytorch.org/whl/cpu
```

```sh
python day10/lab.py --epochs 2
python day11/lab.py --epochs 2
```

- day10은 MLP, day11은 CNN. 각 파일에 해당 모델만 포함.
- 기본값은 train 2,000개·validation 500개·test 후보 500개.
- MNIST는 루트의 `data/`에서 공유. `--data-dir`로 변경 가능.
- 기본 실행은 validation만 평가. 조건 확정 후 선택한 모델을 같은 seed·조건으로 재실행하며 `--evaluate-test`를 추가해 최종 test 평가.
- 결과: `report.html`, `metrics.csv`, `results.json`, `weights.pt`.
- `--dataset synthetic`은 MNIST 대신 합성 선 이미지로 코드 동작을 확인하는 옵션.

## 12일: Neo4j

Docker 실행 후 환경 파일 생성.

- macOS / Linux: `cp day12/.env.example day12/.env`
- PowerShell: `Copy-Item day12/.env.example day12/.env`

```sh
python -m pip install -r day12/requirements.txt
docker compose --project-directory day12 --env-file day12/.env up -d --wait --wait-timeout 180
python day12/lab.py seed
python day12/lab.py queries
```

- Browser: http://127.0.0.1:17474
- URI: `bolt://127.0.0.1:17687`, 사용자·DB: `neo4j`
- 기본 비밀번호: `ResearchLabOnly123` — 로컬 실습용.
- Python은 비밀번호를 입력받거나 `NEO4J_PASSWORD` 환경 변수 사용. Compose는 `day12/.env` 사용.
- 결과는 `day12/results/`에 저장. 기본 그래프는 7노드·9관계.
- `seed.cypher`, `queries.cypher`는 Neo4j Browser에서 직접 실행할 쿼리.

실습 데이터만 초기화

```sh
python day12/lab.py reset --confirm research-lab-v1
```

서버 종료 — 데이터 volume 유지

```sh
docker compose --project-directory day12 --env-file day12/.env down
```

기존 volume의 비밀번호는 `.env`만 바꾸어도 변경되지 않음. 포트 충돌 시 compose의 host 포트와 Python `--uri`를 함께 변경.

## Jupyter / Colab

각 날짜의 `lab.ipynb`를 열어 설치 확인 → 코드 정의 → 실행 → 보고서 순서로 실행.
전체 코드가 포함되어 Colab에는 해당 노트북 하나만 업로드 가능. 결과는 노트북 실행 위치의 `results/`에 저장. Colab 결과는 세션 종료 전 다운로드.
12일은 Docker·터미널·Neo4j Browser를 사용하며 노트북을 포함하지 않음.
