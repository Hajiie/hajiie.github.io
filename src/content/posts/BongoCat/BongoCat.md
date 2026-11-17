---
title: BongoCat
published: 2025-09-02
updated: 2026-11-17
description: '타이핑 애니메이션과 봉고·키보드 사운드를 제공하는 JetBrains IDE 플러그인. 사운드 설정 저장, 한글 IME 이벤트 병합과 리소스 정리 과정을 정리합니다.'
image: "./BongoCat.png"
tags: [Plugin, Jetbrains, Kotlin]
category: 'Plugin'
draft: false
lang: 'Kotlin'
---
::github{repo="Hajiie/BongoCat"}

# BongoCat IntelliJ 플러그인

## 프로젝트 목표

Visual Studio Marketplace 에 있는 Bongo Cat Buddy Extension과 유사한 기능을 Jetbrains IDE에서 플러그인으로 구현

## 기능

- 사용자의 타이핑에 반응하는 봉고 고양이 애니메이션
- toolWindow 크기에 맞춰 자동으로 크기 조정
- 입력이 멈추면 500ms 후 중앙의 대기 이미지로 복귀
- `Off`, `Bongo`, `Keyboard` 중 사운드 모드 선택
- 선택한 사운드 모드를 저장하고 IDE를 다시 열었을 때 복원
- 봉고 모드는 좌·우 이미지 방향에 맞춰 재생하고, 키보드 모드는 일반 문자·Space·Enter·Backspace를 구분
- 한글 IME 조합 중 짧은 시간에 발생한 문서 변경 이벤트를 병합하여 효과음 중복을 줄임

## 사용 방법

1. IDE의 `View → Tool Windows → Bongo Cat`에서 창을 열기.
2. 창 상단 오른쪽에서 `Off`, `Bongo`, `Keyboard` 중 모드 선택.
3. 편집기에서 입력하면 이미지와 선택한 효과음이 반응.

## 구현 구조

- `BongoCatToolWindow`: Tool Window 콘텐츠 생성.
- `BongoCatToolWindowContent`: 이미지·타이머·문서 리스너·사운드 선택 UI 관리.
- `BongoCatSettings`: 사운드 모드 저장과 복원.
- `BongoCatSoundPlayer`: WAV 파일을 재사용 가능한 `Clip` 풀로 읽어 사운드 재생.

프로젝트 루트에서 `./gradlew build`로 빌드.

# BongoCat IntelliJ 플러그인 트러블슈팅 정리

## 1. DocumentListener 중복 등록 문제

문제 및 원인
- 같은 Document에 DocumentListener를 여러 번 등록하면 이벤트가 중복 실행되고 메모리 누수가 발생
- 파일을 다시 열 때 이전 리스너가 해제되지 않아 문제가 생김.

해결 방법
- 현재 구현에서는 콘텐츠별 `registeredDocuments` 집합으로 이미 등록한 문서를 구분.
- 리스너를 콘텐츠의 `Disposable`에 연결하여 Tool Window 콘텐츠 제거 시 해제.
```kotlin
if (!registeredDocuments.add(document)) {
    return
}

document.addDocumentListener(object : DocumentListener {
    override fun documentChanged(event: DocumentEvent) {
        // 입력 상태와 선택한 사운드 모드 처리
    }
}, disposable)
```
- 프로젝트 메시지 버스 연결도 같은 `Disposable`을 사용하여 콘텐츠의 수명과 함께 정리.

## 2. 키 입력 시 아이콘 전환 불안정

문제 및 원인
- 빠른 타이핑 시 아이콘 토글이 꼬이거나, 입력이 끝난 뒤에도 중립 아이콘으로 복귀하지 않음.
- 이벤트 타이밍만으로는 `idle 상태`를 표현하기 어려움.

해결 방법
- `idleTimer`를 두어 500ms 동안 입력이 없으면 자동으로 중립 아이콘으로 복귀.
- 입력 이벤트가 들어올 때마다 `restart()` 호출.
- 현재 이미지와 반대 방향을 반환하는 `nextBongoIcon()`으로 좌·우 상태를 전환. 기존 입력 시각 큐는 리팩터링 과정에서 제거.
- 봉고 모드에서는 20ms 동안 모은 입력마다 이미지 전환과 사운드를 함께 처리.

## 3. ToolWindow 리사이즈 시 성능 저하

문제 및 원인
- `componentResized` 이벤트가 연속적으로 발생할 때마다 이미지가 계속 리스케일링되어 CPU 부담이 큼.

해결 방법
- `resizeTimer`를 두어 디바운스 적용(500ms).
- 연속 resize 이벤트 중에는 타이머를 멈추고, 마지막 이벤트 이후에만 리스케일 실행.
- 창의 너비나 높이가 0 이하이면 크기 변경을 건너뛰고, 계산한 이미지 크기는 최소 1픽셀로 제한.
- 원본 이미지의 비율을 유지하여 조절.

## 4. 초기 파일 로딩 시 리스너 미등록 문제

문제 및 원인
- 프로젝트를 열었을 때 이미 열려 있는 파일들은 `fileOpened` 이벤트가 발생하지 않음.
- 문서 변경 이벤트가 처음에는 감지되지 않음.

해결 방법
- 아래 코드와 같이 순회하며 이미 열려있는 모든 파일에도 `registerDocumentListener` 호출
```kotlin
FileEditorManager.getInstance(project).openFiles.forEach { file ->
    registerDocumentListener(file, disposable, registeredDocuments)
}
```
- 콘텐츠의 `create()`에서 `FileEditorManager.getInstance(project).openFiles`를 순회하여 같은 등록 함수를 호출.
- 이미 열려 있는 문서와 이후에 열리는 문서를 동일한 방식으로 처리.

## 5. MP3 효과음 지연 문제

문제 및 원인
- 처음에는 BongoSoundL.mp3, BongoSoundR.mp3를 JLayer로 재생하도록 구현함.
- MP3는 재생할 때 디코딩 비용이 있고, 키 입력마다 Player를 새로 만들면 시작 지연이 발생함.
- 빠르게 타이핑할 때 여러 입력음이 자연스럽게 겹쳐 재생되기 어렵고, 첫 재생 반응도 느림.

해결 방법
- 효과음 파일을 .wav로 변경.
- 외부 MP3 라이브러리인 `javazoom:jlayer` 의존성을 제거.
- Java 기본 오디오 API인 `javax.sound.sampled.Clip`을 사용.
- 좌/우 사운드마다 여러 개의 Clip을 미리 열어두는 pool 구조로 변경.
```kotlin
private val leftClips = createClipPool("BongoCat_sound/BongoSound/BongoSoundL.wav")
private val rightClips = createClipPool("BongoCat_sound/BongoSound/BongoSoundR.wav")

@Synchronized
private fun play(clips: List<Clip>) {
    val clip = clips.firstOrNull { !it.isRunning } ?: clips.first()

      clip.stop()
      clip.framePosition = 0
      clip.start()
}
```

## 6. 멈췄다가 다시 입력할 때 첫 소리 지연 문제

문제 및 원인
- Clip을 미리 열어도 macOS/Java 오디오 라인이 idle 상태가 되면 첫 start()에서 지연이 생길 수 있음.
- 계속 타이핑할 때는 오디오 라인이 이미 활성화되어 있어 문제가 덜 보임.
- 멈췄다가 다시 타이핑할 때만 첫 소리가 늦게 들리는 현상이 발생.

해결 방법
- 사운드가 켜져 있을 때만 아주 짧은 무음 Clip을 반복 재생.
- 오디오 라인을 계속 활성 상태로 유지해서 첫 입력 지연을 줄임.
- 사용자가 사운드를 끄면 무음 `keep-alive`도 중지.
- Tool Window가 제거될 때 열어둔 모든 Clip을 닫음.
```kotlin
@Synchronized
fun startKeepAlive() {
    if (!keepAliveClip.isRunning) {
        keepAliveClip.loop(Clip.LOOP_CONTINUOUSLY)
    }
}

@Synchronized
fun stopKeepAlive() {
    keepAliveClip.stop()
    keepAliveClip.framePosition = 0
}
```

## 7. 한글 IME 입력 시 DocumentEvent 중복 발생 문제

문제 및 원인
- 한글 입력은 영어 입력처럼 “키 1번 = DocumentEvent 1번”으로 동작하지 않음.
- IME 조합 과정에서 초성/중성/종성 입력, 조합 갱신, 글자 확정이 각각 짧은 간격의 여러 DocumentEvent로 들어올 수 있음.
- 기존 코드는 DocumentEvent가 발생할 때마다 바로 이미지 전환과 사운드 재생을 처리했기 때문에, 사용자는 한 번 입력했다고 느끼는 상황에서도 소리가 두 번 이상 재생될 수 있었음.

해결 방법
- 봉고 모드에서는 DocumentEvent마다 즉시 처리하지 않고, 짧은 시간 안에 몰린 이벤트를 하나의 입력 묶음으로 처리.
- Timer를 사용해 20ms 안에 들어온 이벤트를 하나로 합침.
- 합쳐진 이벤트 묶음마다 이미지 전환과 봉고 사운드 재생을 한 번만 수행.
```kotlin
private fun scheduleBongoHit() {
  pendingBongoHit = true
  pendingKeyboardSoundType = null
  soundTimer.restart()
}

private fun playPendingSound() {
  val shouldPlayBongo = pendingBongoHit
  val keyboardSoundType = pendingKeyboardSoundType

  pendingBongoHit = false
  pendingKeyboardSoundType = null

  if (shouldPlayBongo && settings.soundMode == SoundMode.BONGO) {
    val nextIcon = nextBongoIcon()
    label.icon = nextIcon
    playBongoSoundFor(nextIcon)
  } else if (keyboardSoundType != null && settings.soundMode == SoundMode.KEYBOARD) {
    soundPlayer.playKeyboard(keyboardSoundType)
  }
}
```

## 8. Space / Backspace 입력 시 봉고 소리가 두 번 나는 문제

문제 및 원인
- 한글 조합 중 Space나 Backspace를 누르면, 단순 Space/Backspace 이벤트만 발생하지 않을 수 있음.
- IME가 조합 중이던 글자를 확정하거나 제거하면서 추가 DocumentEvent를 발생시킴.
- 기존 즉시 재생 방식에서는 조합 이벤트와 Space/Backspace 이벤트가 각각 사운드를 내서 두 번 들림.

해결 방법
- 봉고 모드에서도 Space/Backspace를 별도로 즉시 처리하지 않고, 모든 봉고 입력을 scheduleBongoHit()으로 통일.
- 짧은 시간 안에 들어온 조합 확정 이벤트와 Space/Backspace 이벤트를 하나의 봉고 타격으로 병합.
- 최종적으로 입력 묶음당 사운드가 한 번만 나도록 처리.
```kotlin
if (settings.soundMode == SoundMode.BONGO) {
  scheduleBongoHit()
  return
}

private const val SOUND_DELAY_MS = 20
```

## 9. 키보드 사운드와 봉고 사운드 처리 방식 차이

문제 및 원인
- 키보드 사운드는 한글 IME 중복 방지를 위해 이벤트 병합이 필요함.
- 봉고 사운드는 이미지 전환과 방향 싱크가 중요해서 단순히 소리만 늦추면 어색해짐.
- 처음에는 키보드 사운드와 봉고 사운드에 같은 방식의 병합/중복 방지를 적용하려 해서 문제가 생김.

해결 방법
- Keyboard 모드와 Bongo 모드를 분리해서 처리.
- Keyboard 모드: 키보드 사운드만 병합 후 재생.
- Bongo 모드: 이미지 전환과 봉고 사운드를 함께 병합 후 처리.
- 이렇게 해서 키보드 사운드의 중복은 줄이고, 봉고 사운드는 이미지 방향과 싱크를 유지함.
현재 `documentChanged()`에서는 봉고 모드의 타격을 예약하고, 키보드 모드에서는 이미지를 먼저 전환한 뒤 해당 입력의 사운드를 예약.
무음 모드에서도 입력에 따른 이미지 전환은 유지.

## 10. Tool Window 콘텐츠 수명과 리소스 정리

문제 및 원인
- 팩토리 객체가 UI 상태까지 보유하면 콘텐츠를 다시 만들 때 리스너와 타이머의 수명이 맞지 않을 수 있음.
- 문서 리스너만 정리해도 리사이즈 리스너·타이머·열어둔 오디오가 남을 수 있음.

해결 방법
- 팩토리와 실제 상태를 관리하는 콘텐츠 클래스를 분리.
- 콘텐츠에 `Disposable`을 설정하고, 제거 시 idle·sound·resize 타이머를 중지.
- Swing 리사이즈 리스너를 제거하고 사운드 플레이어의 `dispose()`를 호출.
- 이미지 리소스 로딩 여부도 확인하여 누락된 파일을 명확하게 식별.

## 관련 구현 기록

- [Tool Window 수명주기 리팩터링](https://github.com/Hajiie/BongoCat/commit/5fe50e998e68c9f07a88bc3770316e728f5aabde)
- [사운드 모드·설정 저장·IME 이벤트 병합](https://github.com/Hajiie/BongoCat/commit/5bd941463f6072257672bc814ac2952c93128721)
