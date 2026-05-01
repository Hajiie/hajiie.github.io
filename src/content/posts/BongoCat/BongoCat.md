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

# BongoCat IntelliJ 플러그인

## 프로젝트 목표

Visual Studio Marketplace 에 있는 Bongo Cat Buddy Extension과 유사한 기능을 Jetbrains IDE에서 플러그인으로 구현

## 기능

- 사용자의 타이핑에 반응하는 봉고 고양이 애니메이션
- toolWindow 크기에 맞춰 자동으로 크기 조정
- ~~타이핑 시 키보드 사운드~~

# BongoCat IntelliJ 플러그인 트러블슈팅 정리

## 1. DocumentListener 중복 등록 문제

문제 및 원인
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

문제 및 원인
- 빠른 타이핑 시 아이콘 토글이 꼬이거나, 입력이 끝난 뒤에도 중립 아이콘으로 복귀하지 않음.
- 이벤트 타이밍만으로는 `idle 상태`를 표현하기 어려움.

해결 방법
- `idleTimer`를 두어 500ms 동안 입력이 없으면 자동으로 중립 아이콘으로 복귀.
- 입력 이벤트가 들어올 때마다 `restart()` 호출.
- `keyPressTimes` 큐를 이용해 짧은 시간(100ms) 내 입력을 묶어 좌/우 아이콘을 번갈아 표시.

## 3. ToolWindow 리사이즈 시 성능 저하

문제 및 원인
- `componentResized` 이벤트가 연속적으로 발생할 때마다 이미지가 계속 리스케일링되어 CPU 부담이 큼.

해결 방법
- `resizeTimer`를 두어 디바운스 적용(500ms).
- 연속 resize 이벤트 중에는 타이머를 멈추고, 마지막 이벤트 이후에만 리스케일 실행.
- 필요 시 현재 크기 캐시를 활용해 불필요한 재스케일 방지.

## 4. 초기 파일 로딩 시 리스너 미등록 문제

문제 및 원인
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
    val clip = clips.firstOrNull { !it.isRunning } ? : clips.first()

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
- 오디오 라인을 계속 활성 상태로 유지해서 첫 입력 지연을 줄
  임.
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
```kotlin
private fun handleSound(keyboardSoundType: KeyboardSoundType)
{
  when (settings.soundMode) {
    SoundMode.OFF -> return
    SoundMode.BONGO -> scheduleBongoHit()
    SoundMode.KEYBOARD -> scheduleKeyboardSound(keyboardSoundType)
  }
}
```