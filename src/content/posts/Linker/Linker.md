---
title: "Linker: 비개발자용 서버 및 환경 관리 앱"
published: 2026-03-24
description: 'Linker is an application designed to make it easy for non-developers to access and use personal servers when they have set them up.'
image: './Linker_Start.png'
tags: [Electron, Server, TypeScript]
category: 'TypeScript'
draft: false 
lang: 'TypeScript'
---
::github{repo="Hajiie/Linker"}

# Linker: 비개발자용 서버 및 환경 관리 앱

## 배경

- 2026년 초, 연구실에 있는 서버 컴퓨터에 원격으로 접속하여 사용하던 중 비개발자인 다른 연구원들이 사용을 힘들어하여 제작

## 주요 기술 및 구현
Framework
- **Electron** 을 사용하여 크로스 플랫폼 데스크톱 앱(Vite 기반)을 구성

Frontend Framework
- React 및 Tailwind CSS를 사용하여 Lucide 아이콘 기반의 반응형 UI 제작

Backend Framework
- Node.js 를 사용하여 SSH 세션 및 원격 시스템을 제어 수행

Server Communication
- ssh2 모듈로 SSH 프로토콜 및 포트 포워딩 구현

Database
- lowdb 형태로 서버 접속 정보를 로컬에 저장 및 관리 수행

## 시스템 주요 기능
서버 관리 (Server Management)
- 직관적인 대시보드: 카드형 UI로 등록된 서버 목록을 한눈에 확인.
- 간편한 CRUD: 서버 이름, 호스트, 계정 정보를 안전하게 저장하고 관리.

Conda 가상환경 제어 (Conda Environment)
- 환경 리스트: 서버에 설치된 모든 가상환경 자동 스캔 및 시각화.
- 원클릭 생성/삭제: Python 버전을 선택하여 새 환경을 구축하거나 불필요한 환경 제거.
- 주피터 자동 연결: 가상환경을 선택하면 자동으로 SSH 터널링을 통해 Jupyter Notebook을 기본 브라우저에 실행.

패키지 매니저 (Package Management)
- 설치 목록 확인: 각 환경별 설치된 패키지 명칭, 버전, 설치 채널(Conda/PyPI) 표시.
- 통합 검색 및 설치 
  - Conda Search: Conda 리포지토리에서 패키지 검색 후 즉시 설치. 
  - Pip Direct: 패키지명을 직접 입력하여 PyPI를 통해 설치.
- 안전한 삭제: 휴지통 아이콘 클릭만으로 conda remove 또는 pip uninstall 자동 실행.

SFTP 파일 매니저 (SFTP File Browser)
- 직관적인 탐색: 원격 서버의 디렉토리 구조를 시각적으로 탐색하고 경로 이동 지원.
- 네이티브 드래그 앤 드롭
  - 업로드: 로컬의 파일 및 폴더를 브라우저로 드래그하여 서버에 전송.
  - 다운로드: 서버의 파일 및 폴더를 로컬 폴더로 드래그하여 즉시 다운로드.
- 재귀적 전송: 폴더 구조 전체를 유지하며 재귀적으로 업로드/다운로드 수행.

- 반응형 UI/UX (Responsive Design)
가변 레이아웃: 창 크기에 따라 카드 배열, 모달 여백, 폰트 크기가 최적화되는 반응형 디자인.
실시간 피드백: 작업 진행 상태(로딩 애니메이션) 및 성공/실패 여부를 알림으로 제공.

## 프로젝트 의의
비개발자를 위한 편의성 시스템
- 기존 SSH를 통해 컴퓨터를 원격으로 관리하던 프로그램에 비해 직관적이고 아이콘 기반으로 한 가시성 향상
- 복잡한 명령어 기반이 아닌 검색 후 설치, 가상환경 생성 등을 버튼으로 제어

---

# Linker 트러블슈팅 정리


## 1. Electron Error: Module did not self-register (sshcrypto.node)
문제 및 원인
- `ssh2` 라이브러리의 네이티브 모듈이 번들러에 의해 잘못 처리됨.

해결 방법
- `vite.config.ts`에서 `ssh2` 관련 모듈을 명시적으로 `external` 처리하고, 소스 코드에서 `require` 문법을 사용하여 번들링을 방 지함.

## 2. SSH Command Error: conda: command not found
문제 및 원인
- SSH `exec`을 통해 명령어를 실행할 때, 로그인 셸이 아니므로 `.bashrc`나 `.profile`에 정의된 `conda` 경로가 로드되지 않음. 이로 인해 `conda` 명령어를 인식하지 못하는 현상이 발생함.

해결 방법
- 명령어를 실행할 때 `bash -l -c` (로그인 셸) 옵션을 사용하여 사용자 환경 설정을 강제로 로드한 뒤 실행하거나, 환경 설정 파일을 직접 `source` 하도록 명령어를 수정함.

## 3. UI Layout Breakdown on Small Window Sizes
문제 및 원인
- 고정된 패딩과 최소 높이(`min-h`) 설정으로 인해 창 크기가 작아질 때 모달 콘텐츠가 겹치거나 화면 밖으로 나가는 현상이 발생함. 

해결 방법
- Tailwind CSS의 반응형 접두사(`md:`, `lg:`)를 사용하여 화면 크기에 따라 여백과 폰트 크기를 동적으로 조절하고, 모달 내부의 고정 높이 제한을 제거하여 콘텐츠가 유연하게 배치되도록 수정함.

## 4. "Create New Environment" Button Accessibility
문제 및 원인
- 가상환경 리스트가 길어지거나 창 높이가 낮아질 때, 리스트 하단에 고정된 "새 환경 만들기" 버튼이 화면 하단에 가려져 클릭할 수 없는 문제가 발생함.

해결 방법
- 버튼을 스크롤 가능한 컨테이너 내부 하단으로 이동시키고 영역의 `min-h`를 제거하여, 항목이 많아지더라도 스크롤을 통해 항상 버튼에 접근할 수 있도록 구조를 개선함.

## 5. SFTP Drag-Out: Local File Requirement for startDrag
문제 및 원인
- Electron의 `startDrag` API는 로컬에 존재하는 파일 경로를 필수로 요구함. 하지만 SFTP 브라우저에서 드래그를 시작할 때 파일은 원격 서버에만 존재하므로 즉시 드래그를 시작할 수 없음.

해결 방법
- `ipcMain.on`에서 드래그 요청을 받으면, 먼저 서버에서 파일을 로컬 임시 디렉토리(`os.tmpdir()`)로 다운로드함. 다운로드가 완료된 시점에 `event.sender.startDrag`를 호출하여 로컬 경로와 아이콘을 전달함으로써 원격 파일의 드래그 앤 드롭을 구현함.

## 6. SFTP Folder Upload: Recognition Issue
문제 및 원인
- SFTP 브라우저에 폴더를 드롭했을 때, 기존 `sftp.put()` 메서드는 단일 파일만 처리할 수 있어 폴더 구조가 정상적으로 업로드되지 않거나 에러가 발생함.

해결 방법메인 프로세스의 `uploadFile` 로직에서 `fs.statSync`를 사용하여 로컬 경로가 폴더인지 확인하도록 수정함. 폴더일 경우 `sftp.uploadDir()` 메서드를 호출하여 재귀적으로 폴더 구조 전체를 업로드하도록 기능을 개선함.

## 7. SFTP Folder Download: Recursive Support
문제 및 원인
- 원격 서버의 폴더를 로컬로 드래그하여 다운로드할 때, 단일 파일 전용인 `sftp.get()`을 사용하여 폴더 구조가 누락되거나 에러가 발생함.

해결 방법
- `downloadFile` 로직에 `sftp.stat()`을 추가하여 원격 경로가 폴더인지 확인하고, 폴더일 경우 `sftp.downloadDir()`을 사용하여 하위 디렉토리와 파일을 모두 재귀적으로 다운로드하도록 수정함.

## 8. SFTP Drag-Out: macOS Icon Path Crash
문제 및 원인
- macOS(darwin) 환경에서 Electron의 `startDrag` API 호출 시 전달된 `icon` 경로에 실제 이미지 파일이 존재하지 않으면 앱이 즉시 크래시되거나 드래그가 시작되지 않는 현상이 발생함.

해결 방법
- 프로젝트 내에 기본 아이콘이 없는 경우를 대비해, 드래그 시작 시점에 1x1 크기의 투명 PNG 데이터를 Buffer로 생성하여 임시 폴더에 저장함. 해당 임시 파일 경로를 아이콘으로 사용함으로써 아이콘 부재로 인한 크래시를 방지함.
