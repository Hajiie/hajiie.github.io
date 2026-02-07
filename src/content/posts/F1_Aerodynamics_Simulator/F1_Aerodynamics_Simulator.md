---
title: F1 공기역학 시뮬레이터
published: 2026-02-07
description: 'F1 Aerodynamics Simulator'
image: './F1_Aerodynamics_Simulator_Start.png'
tags: [Simulator, Mechanics, C++, Graphics]
category: 'C++'
draft: true 
lang: 'C++'
---
::github{repo="Hajiie/F1_Aerodynamics_Simulator"}

# F1 공기역학 시뮬레이터

## LBM 엔진의 설계 원리

### 1. 거시적 접근 vs. 미시적 접근 (Navier-Stokes vs. LBM)  
일반적인 유체 역학은 유체를 연속체로 보고 편미분 방정식(Navier-Stokes)을 풀지만, 본 프로젝트에서 채택한 __LBM(Lattice BoltzMann Method)__ 은 유체를 격자 위 입자들의 통계적 집합으로 취급한다. 이는 복잡한 장애물 형상(Boundary)을 처리하고 GPU 병렬 연산을 구현하는 데 유리하다.

### 2. D2Q9 모델의 물리적 구성
격자 하나당 9개의 분포 함수(<span style="font-family:Times new roman">_f<sub>i</sub>_</span>)를 가진다.
- 의미: 각 격자점에서 특정 방향(<span style="font-family:Times new roman">_i_</span>)으로 이동하려는 입자의 밀도이다.
- 상태량 계산: 9개의 <span style="font-family:Times new roman">_f_</span>를 합치면 밀도(_ρ_)가 되고, 방향 벡터를 곱해 합치면 속도(<span style="font-family:Times new roman">_u_</span>)이 산출된다.

### 3. 알고리즘 프로세스
1. 충돌 단계(Collision) - BGK 근사 모델  
   입자들이 부딪혀 물리적 평형 상태(<span style="font-family:Times new roman">_f<sub>eq</sub>_</span>)로 수렴하는 과정
    - 수학적 모델: `(f[i] - f_eq[i]) / TAU` (Single Relaxation Time 모델)
    - 점성 제어: 완화 시간 **TAU(_τ_)**
        - _τ_ 가 0.5에 가까울수록 점성이 낮아져 레이놀즈 수가 높은 공기 흐름(와류)이 발생
        - _τ_ 가 크면 유체가 끈적해져 흐름이 완만해짐
2. 이동 단계(Streaming) & 경계 조건(Bounce-back)  
   계산된 입자 분포를 실제 인접 격자로 전달하는 과정
    - 장애물 처리: 장애물(`is_wall`)을 만나면 입자를 반대 방향 인덱스(`opp[]`)로 튕겨보냄
    - 이점: 복잡한 미분 계산 없이 단순히 인덱스 반전만으로도 고체 표면에서의 유체 거동을 모사 가능
    - 구현 방식: Push 방식(현재 격자에서 이웃으로 전파)을 채택하여 경계 처리를 직관적으로 구현

### 4. 구현 디테일
- **경계 조건 (Boundary Conditions)**:
    - 기본적으로 `(x + cx[i] + nx) % nx`를 이용한 **주기적 경계 조건(Periodic Boundary)** 을 적용하여 상하 경계를 연결함.
    - **Inlet (유입구)**: 왼쪽 벽(x=0)에서는 일정한 유속(<span style="font-family:Times new roman">_u<sub>x</sub>_</span>)을 강제하여 평형 분포 함수(<span style="font-family:Times new roman">_f<sub>eq</sub>_</span>)를 주입함.
    - **Outlet (유출구)**: 오른쪽 벽(x=nx-1)에서는 바로 이전 격자의 분포 함수를 복사하는 **Zero Gradient (Open Boundary)** 조건을 적용하여 유체가 자연스럽게 빠져나가도록 처리함.
- 데이터 최적화: `next_grid`라는 임시 버퍼를 사용하여 이전 프레임의 데이터가 현재 계산에 영향을 주지 않도록 물리적 독립성을 보장 (Double Buffering)
- 업데이트 순서: Collision → Streaming → Boundary Conditions → Macroscopic Update 순으로 정렬하여 데이터 일관성 확보

### 시각화의 깊이
><span style="font-family:Times new roman">Vorticity = ∂u<sub>y</sub>/∂x - ∂u<sub>x</sub>/∂y</span>  

이를 통해 장애물 뒤에서 발생하는 소용돌이를 시각적으로 증명

C++의 메모리 제어를 통해 초당 반복 횟수를 극대화하고, OpenGL 텍스처 매핑을 통해 실시간 유속장을 렌더링함.

# F1 Aerodynamics Simulator 트러블슈팅 정리
## 1. 공기 흐름이 보이지 않았던 원인 분석
### 1. 시각화 코드의 디버깅 설정 잔재
문제 및 원인
- `main.cpp` 내 렌더링 루프에서 `speed` 값을 실제 물리 연산 결과인 `sqrt(vx*vx + vy*vy)`가 아닌, 디버깅용 그라데이션 값(`x / NX`)으로 강제 덮어쓰기 하고 있었음. 이로 인해 내부 물리 연산이 돌고 있어도 화면에는 정지된 그라데이션만 출력.

해결 방법
- 물리 연산 결과를 반영하여 해결

### 2. Double Buffering 미적용으로 인한 데이터 오염
문제 및 원인
- LBM은 모든 격자가 동시에 업데이트되어야 하는 병렬적 특성을 가짐.
- 수정 전 코드에서는 `grid` 값을 읽으면서 동시에 같은 `grid`에 값을 썼기 때문에, 업데이트된 값이 즉시 이웃 격자의 계산에 영향을 주어 비물리적인 전파가 발생.

해결 방법
- `next_grid` 버퍼를 도입하여 '읽기'와 '쓰기'를 분리함으로써 해결.

### 3. 물리 파라미터(TAU) 설정
문제 및 원인
- 완화 시간 `TAU`가 0.6으로 설정되어 점성이 다소 높았음. 

해결 방법
- 0.53으로 낮추어 레이놀즈 수(Re)를 높임으로써, 장애물 뒤쪽의 불안정한 흐름(Karman Vortex Street)이 더 잘 생성되도록 유도.

## 2. 렌더링 및 쉐이더 이슈 분석


### 1. 텍스처 보간(Interpolation) 문제 (GL_LINEAR vs GL_NEAREST)
문제 및 원인
- 장애물(-10.0)과 유체(0.0)의 경계면이 흐릿하게 보이거나 회색조로 렌더링됨.
- `GL_LINEAR` 필터링은 인접한 픽셀 값을 부드럽게 섞어서(Interpolation) 표현. 이 과정에서 -10.0과 0.0 사이의 중간값(예: -5.0)이 생성되어, 쉐이더의 조건문(`v < -5.0`) 경계에서 의도치 않은 색상이 출력. 

해결 방법
-`GL_NEAREST`로 변경하여 픽셀 값을 섞지 않고 있는 그대로(Nearest Neighbor) 가져오도록 설정, 경계를 명확하게 만듦.

### 2. 쉐이더 파일 로딩 및 캐싱 문제
문제 및 원인
- 쉐이더 파일(`simulation.frag`)을 수정했음에도 불구하고 화면에 변화가 없었음.
- 실행 파일이 실행되는 위치(Working Directory)와 소스 파일의 위치가 달라 수정된 쉐이더 파일을 읽지 못하고 기존 파일을 읽었거나, 빌드 시스템이 리소스를 최신화하지 않았을 가능성이 큼.

해결 방법
- 쉐이더 소스 코드를 `main.cpp` 내부에 문자열(String Literal)로 직접 포함(Inline)시켜, 외부 파일 의존성을 제거하고 컴파일 시 무조건 최신 코드가 반영되도록 강제함.

## 3. ImGui 통합 및 빌드 이슈
ImGui를 프로젝트에 통합하는 과정에서 발생한 문제와 해결책은 다음과 같다.

### 1. ImGui 백엔드 소스 누락 (Undefined Reference Error)
문제 및 원인
- `ImGui::CreateContext`, `ImGui_ImplGlfw_InitForOpenGL` 등의 함수를 찾을 수 없다는 링킹 에러 발생.
- vcpkg로 설치한 ImGui 패키지는 헤더 파일만 제공하며, 실제 구현체인 `imgui_impl_glfw.cpp`, `imgui_impl_opengl3.cpp` 등은 포함되어 있지 않음.

해결 방법
- ImGui GitHub 저장소에서 해당 백엔드 소스 파일과 코어 소스 파일(`imgui.cpp` 등)을 직접 다운로드하여 프로젝트의 `external` 폴더에 추가하고, `CMakeLists.txt`에 소스 파일로 등록하여 직접 빌드하도록 설정함.

### 2. 시뮬레이션 성능 저하 (Lagging)
문제 및 원인
- ImGui 추가 후 시뮬레이션이 눈에 띄게 느려짐.
- Debug 모드로 빌드 시 컴파일러 최적화가 적용되지 않아, 매 프레임 수십만 개의 격자를 계산하는 LBM 연산 속도가 현저히 떨어짐.

해결 방법
- `CMakeLists.txt`에 최적화 플래그(`/O2`, `-O3`, `-march=native`)를 추가하고, Release 모드로 빌드하여 성능을 복구함.

## 4. 알파 채널(투명도) 처리 및 인덱싱 오류
문제 및 원인
- 배경을 제거한 PNG를 사용했음에도 차체 형상이 격자에 나타나지 않거나 프로세스가 비정상 종료됨.
- 일반적인 1채널(Grayscale) 방식이나 3채널(RGB) 방식으로 접근할 경우, 배경이 날아간 PNG의 알파 채널 데이터를 읽지 못함.
- 픽셀 접근 시 채널 수(img_ch)를 고려하지 않은 잘못된 인덱스 계산으로 인해 잘못된 메모리 주소를 참조(Access Violation)함.

해결 방법
- `stbi_load` 호출 시 강제로 4채널(RGBA)로 로드하도록 설정하고, 픽셀당 4바이트 간격으로 접근하여 4번째 바이트인 알파(A) 값을 기준으로 장애물 여부를 판단하도록 로직을 수정함.
