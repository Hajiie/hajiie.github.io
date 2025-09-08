---
title: BongoCat
published: 2025-09-02
description: 'The BongoCat plugin is a JetBrains plugin developed in the Kotlin language.'
image: "./BongoCat.png"
tags: [Plugin, Jetbrains, Kotlin]
category: 'Plugin'
draft: false 
lang: 'Kotlin'
---
::github{repo="Hajiie/BongoCat"}

# BongoCat IntelliJ 플러그인 트러블슈팅 정리

## 1. DocumentListener 중복 등록 문제

원인
- 같은 Document에 DocumentListener를 여러 번 등록하면 이벤트가 중복 실행되고 메모리 누수가 발생
- 파일을 다시 열 때 이전 리스너가 해제되지 않아 문제가 생김.

해결 방법
- `documentListenersMap`을 두어 문서별 리스너를 관리.
- 새로 리스너를 등록하기 전에 기존 리스너가 있으면 `removeDocumentListener`로 제거 후 다시 등록.
```kotlin
documentListenersMap[document]?.let {
                document.removeDocumentListener(it)
                documentListenersMap.remove(document)
            }
```
- 파일 닫힘 시에도 맵에서 제거하여 누수 방지.

## 2. 키 입력 시 아이콘 전환 불안정

원인
- 빠른 타이핑 시 아이콘 토글이 꼬이거나, 입력이 끝난 뒤에도 중립 아이콘으로 복귀하지 않음.
- 이벤트 타이밍만으로는 `idle 상태`를 표현하기 어려움.

해결 방법
- `idleTimer`를 두어 500ms 동안 입력이 없으면 자동으로 중립 아이콘으로 복귀.
- 입력 이벤트가 들어올 때마다 `restart()` 호출.
- `keyPressTimes` 큐를 이용해 짧은 시간(100ms) 내 입력을 묶어 좌/우 아이콘을 번갈아 표시.

## 3. ToolWindow 리사이즈 시 성능 저하

원인
- `componentResized` 이벤트가 연속적으로 발생할 때마다 이미지가 계속 리스케일링되어 CPU 부담이 큼.

해결 방법
- `resizeTimer`를 두어 디바운스 적용(500ms).
- 연속 resize 이벤트 중에는 타이머를 멈추고, 마지막 이벤트 이후에만 리스케일 실행.
- 필요 시 현재 크기 캐시를 활용해 불필요한 재스케일 방지.

## 4. 초기 파일 로딩 시 리스너 미등록 문제

원인
- 프로젝트를 열었을 때 이미 열려 있는 파일들은 `fileOpened` 이벤트가 발생하지 않음.
- 문서 변경 이벤트가 처음에는 감지되지 않음.

해결 방법
- 아래 코드와 같이 순회하며 이미 열려있는 모든 파일에도 `registerDocumentListener` 호출
```kotlin
override fun createToolWindowContent(project: Project, toolWindow: ToolWindow) {
    ...
    // 현재 열려 있는 파일 에디터 목록에 대한 이벤트 리스너 등록
    val fileEditorManager = FileEditorManager.getInstance(project)
    for (file in fileEditorManager.openFiles) {
        registerDocumentListener(file)
    }
    ...
}
```
- 프로젝트 시작 시점부터 모든 열린 문서에서 이벤트 감지 가능.