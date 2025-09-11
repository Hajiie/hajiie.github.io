---
title: OpenGL
published: 2025-09-09
description: 'Summary of OpenGL Study Using C++'
image: 'https://learnopengl.com/img/index_image2.png'
tags: [OpenGL, Study, C++]
category: 'Study'
draft: False 
lang: 'C++'
---
[LearnOpenGL](https://learnopengl.com/) 강의 요약   
2025-09-09 ~ Ing

# Getting Started
## OpenGL
- ~~그래픽, 이미지를 다루는데 사용할 수 있는 함수 집합을 제공하는 API~~
- Khronos Group이 개발, 유지 관리하는 기술 명세 혹은 규격

### OpenGL Specification
- 각 함수의 결과/출력이 무엇이고, 어떻게 동작하는지 명시
- OpenGL은 Specification(결과/출력/규격)을 준수하는 한 구현 방식 상이
- [OpenGL 3.3 명세서](https://www.opengl.org/registry/doc/glspec33.core.20100311.withchanges.pdf)

### Immediate Mode(Fixed Function Pipeline)
- 그래픽 처리 과정(파이프라인)의 각 단계가 정의돼있는 상태
- 실제 함수의 작동 방식(연산 방식) 습득엔 한계

### Core-profile
- Immediate Mode 의 기능을 뺀 순수한 OpenGL
- 정해진 기능이 아닌 사용자가 원하는 기능을 구현
- 3D 그래픽스 렌더링의 원리·컴퓨터 그래픽스에 대한 이해

### Extensions
- OpenGL은 하드웨어가 지원하는 한 새로운 최적화 방식, 기술 등을 적용 가능
- 하드웨어가 지원하지 않는다고 하여도 기존의 방식을 사용
- 확장된 기능이 유용한 경우 OpenGL 코어 기능으로 통합
```Pseudo-code
if(GL_ARB_extension_name){
    // 하드웨어가 지원하는 새 방식
}
else{
    // 기존의 방식
}
```

### State Machine
오토마타 이론에 나오는 DFA 와 같은 기계는 `(상태, 입력) → 다음 상태`로의 전이가 정의된 모델
```Automata
(A state, 'a' input) → B state
```
OpenGL에서의 `State Machine`은 Design Pattern, OpenGL의 `상태`는 여러 설정 변수들의 집합
```OpenGL
glColor3f() → 일부만 변경
```

오토마타에서 State는 Machine이 있을 수 있는 State를 말하며,
`OpenGL Context` 는 OpenGL 이라는 Machine의 State를 말한다.   
`glUseProgram(shaderProgramID) 함수 호출로 사용할 셰이더 프로그램 Context를 변경`

오토마타처럼 Input이 들어가면 새로운 State를 출력한다는 개념이 아닌,
Input이 들어오면 현재 Context(State)를 변경하거나, 현재 Context(State)를 이용해서 다른 동작을 하는 개념
- Input → Change Context → `state-changing`
- Input → Use Context → `state-using`

### Objects
- OpenGL에서의 객체는 OpenGL Context의 하위 집합을 나타내는 상태 변수/설정의 집합
- C언어의 구조체처럼 객체는 데이터(설정값)의 컨테이너 역할
```Pseudo-code
// create object
unsigned int objectId = 0;
glGenObject(1, &objectId); // objectId 를 새로 부여
// bind/assign object to context
glBindObject(GL_WINDOW_TARGET, objectId); // objectId 가 가리키는 객체에 bind
// set options of object currently bound to GL_WINDOW_TARGET
glSetObjectOption(GL_WINDOW_TARGET, GL_OPTION_WINDOW_WIDTH,  800); // objectId 가 가리키는 객체의 너비
glSetObjectOption(GL_WINDOW_TARGET, GL_OPTION_WINDOW_HEIGHT, 600); // 높이를 조정
// set context target back to default
glBindObject(GL_WINDOW_TARGET, 0); // unbind
```
- 원하는 설정값이 담긴 객체의 ID를 타겟에 바인딩하여 해당 타겟에 대한 후속 작업이 바인딩된 객체의 상태를 즉시 사용
  - A 라는 객체와 B 라는 객체에 서로 다른 설정이 있을 때, A 를 bind 하거나 B 를 bind 하는 식으로 다른 설정의 객체를 불러와 사용 가능

## Create Window

### GLFW 초기화 및 설정, winodw 객체 생성
GLFW 초기화 및 설정

`glfwWindowHint(구성하려는 옵션(GLFW_ 접두사가 붙은 열거형 옵션 중 택), 선택한 옵션의 값을 설정);`

```C++
glfwInit(); // GLFW 초기화
glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3); // GLFW 버전 설정 major
glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3); // GLFW 버전 설정 minor
glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE); // GLFW 프로파일을 Core-profile 로 설정
glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
```

window 객체 생성
```C++
// GLFW 윈도우 생성
GLFWwindow *window = glfwCreateWindow(800, 600, "LearnOpenGL", NULL, NULL);
if (window == NULL) { // 윈도우 생성 실패시
    std::cout<<"Failed to create GLFW window" << std::endl;
    glfwTerminate();
    return -1;
}
glfwMakeContextCurrent(window);
```

### GLAD
```C++
// GLAD 초기화
if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
    std::cout<<"Failed to initialize GLAD"<<std::endl;
    return -1;
}
```

### Viewport
`glViewport` 함수는 -1~1 사이의 값을 좌표계로 변환
(-0.5, 0.5) 는 우리가 설정한 좌표계에서 (200, 450) 으로 매핑
```C++
glViewport(0, 0, 800, 600);
```

사용자가 창 크기를 변경하는 순간 Viewport도 함께 변경
창 크기가 변경될 때마다 호출되는 콜백 함수를 등록
```C++
void framebuffer_size_callback(GLFWwindow *window, int width, int height); // prototype
```
`GLFWwindow`를 받고 새로운 창 크기의 너비, 높이를 인자로 받는 콜백 함수

생성한 콜백 함수를 GLFW에 등록
```C++
glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);
```
사용자 정의 함수를 등록하기 위해 설정할 수 있는 콜백 함수는 window 생성 후 render 루프 시작 전에 등록

### Render Loop
GLFW에 종료가 입력되기 전까지 계속 실행되는 렌더링 루프
```C++
while (!glfwWindowShouldClose(window)) {
    glfwSwapBuffers(window);
    glfwPollEvents();
}
```
`glfwWindowShouldClose` 함수는 각 루프 반복 시작 시 GLFW에 종료가 입력됐는지 확인   
`glfwPollEvents` 함수는 이벤트(키보드 입력, 마우스 움직임 등)가 발생했는지 확인, 
window 상태를 업데이트 후 해당 이벤트 함수(콜백 메서드를 통해 등록 가능)를 호출   
`glfwSwapBuffers` 함수는 이번 렌더링 루프에서 렌더링에 사용된 버퍼를 교체   
:::note[Double Buffer]   
문제점
- 단일 버퍼에 어플리케이션이 렌더링 할 경우 이미지에 깜빡임이 발생

원인
- 출력 이미지가 순간적으로 그려지는 것이 아니라 순차적으로 픽셀 단위만큼 그려지기 때문

해결방안
- 프론트 버퍼는 현재 화면에 표시되는 최종 이미지를 출력   
- 백 버퍼는 다음에 표시될 이미지 렌더링을 수행   
- 백 버퍼의 렌더링이 모두 완료되면, 프론트 버퍼와 백 버퍼를 교체
:::

### Terminate & Result
```C++
glfwTerminate();
return 0;
```
리소스를 정리하고 어플리케이션을 종료

실행 결과
![OpenGL](OpenGL_Start.png)

### Input
GLFW 입력 제어 기능   
키를 입력으로 받는 `glfwGetKey` 함수 사용
```C++
void processInput(GLFWwindow *window){
  if(glfwGetKey(window, GLFW_KET_ESCAPE) == GLFW_PRESS){
    glfwSetWindowShouldClose(window,true);
  }
}
```
ESCAPE 키가 입력 됐는지 확인, 입력되지 않았다면 `GLFW_RELEASE` 값을 반환   
ESCAPE 키를 누른 경우, `glfwSetwindowShouldClose` 함수를 사용하여 `WindowShouldClose` 속성을 true 로 설정   

### Rendering
모든 렌더링 커맨드를 렌더링 루프 내에 배치
```C++
// render loop
while (!glfwWindowShouldClose(window)) {
    // input
    processInput(window);

    // rendering commands here
    ...

    // check and call events and swap the buffers
    glfwPollEvents();
    glfwSwapBuffers(window);
}
```
화면 내 색상 변경   
프레임 시작 시 이전 프레임의 결과가 나올 수 있기 때문에 `glClear` 함수를 사용해 화면의 색상 버퍼를 제거   
`glClear(지울 버퍼를 지정하기 위한 버퍼 비트 선택);`   

:::tip[설정 가능한 버퍼 비트]
- `GL_COLOR_BUFFER_BIT`
- `GL_GL_DEPTH_BUFFER_BIT`
- `GL_STENCIL_BUFFER_BIT`
:::

`glClearColor` 함수를 사용해 버퍼 색상 변경   
`glClearColor(R,G,B,A);`

:::note
`glClearColor` 함수는 state-changing(Change Context), 상태 설정 함수   
`glClear` 함수는 state-using(Use Context), 상태 사용 함수
:::