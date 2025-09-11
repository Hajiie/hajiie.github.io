---
title: GraduationProject_Civil
published: 2025-09-08
description: 'The objective is to develop an application capable of visualising flood situations in augmented reality (AR) within the physical space of urban areas where flood and inundation risks exist.'
image: ""
tags: [Unity, GraduationProject, C#, Visualization]
category: 'Unity'
draft: false 
lang: 'C#'
---
::github{repo="Hajiie/AR_Flooding_Mobile"}

# Unity 침수 시각화 프로젝트

## 문제 인식 및 배경

### 배경

- 2022년 8월, 서울 한강 이남 지역의 기록적 폭우(서초 413mm, 강남 385mm)로 인한 심각한 피해 발생
    - 관악구 반지하 주택 침수로 일가족 사망 비극 발생
    - 도림천이 범람하고 강남 일대 도로, 차량 침수

### 문제점
- 강남 지역의 분지 지형으로 인한 침수 취약성
- 뉴스에서 제공하는 강수량 수치만으로는 일반인의 직관적 위험 인지 한계

## 주요 기술 및 구현
기반 기술
- Unity 기반의 AR 시각화 프로세스 적용

위치 계산
- Unity 내에서 GPS 좌표와 환경부 침수 지도 좌표계 일치
- `레이크로싱(Ray-Crossing)`알고리즘을 활용해 사용자의 침수 구역 내 위치 여부 판별

수위 시뮬레이션
- Unity 스크립트를 통해 시간 경과에 따른 점진적인 수위 상승 연출

수심 시각화
- 침수 깊이에 따른 물 색상 변화로 위험도 시각적 표현
- 0.2m 미만(파랑)부터 0.8m 초과 (빨강)까지 색상으로 위험 수준 표시

## 시스템 주요 기능
AR 시각화
- 사용자 실제 공간에 3D 침수 상황을 오버레이하여 위험 체감 극대화

맨홀 위험 경고
- 맨홀 위치 사전 표시 및 역류 위험 시각화로 접근 방지 유도
  - 해당 기능은 구현되지 못한 기능으로 추후 프로젝트를 더 진행할 수 있다면 추가할 기능이며, 현재 프로젝트에서는 사용자가 인식한 맨홀을 클릭하여 표시하는 방식을 사용

GPS 지도 연동
- 화면 하단 지도를 통해 현재 위치 및 주변 침수 레벨 확인 기능 제공

시각적 경고 강화
- 쉐이더 효과, 파도 애니메이션 등을 적용하여 시각적 경각심 증대

## 프로젝트 의의 및 향후 계획

### 프로젝트 의의
- 복잡한 수치 모델이 아닌 직관적 시각 정보 제공으로 일반 사용자의 상황 인식 능력 향상
- 재난 대응, 대피 훈련 등 실생활에 적용 가능한 실용적 가치 확보

### 향후 활용 계획
- 실시간 재난 대응 훈련 시스템으로 활용
- 관광객 및 방문객을 위한 다국어 안내 콘텐츠 개발
- 실시간 강우 데이터와 연동된 시민 경보 시스템 구축
- 안전 인식 제고를 위한 교육용 콘텐츠로 활용 가능성

---

# Unity 침수 시각화 프로젝트 트러블슈팅 정리

## 1. GeoJSON 좌표 불일치로 인한 물 위치 오류

문제 및 원인
- GeoJSON에서 불러온 침수 영역이 지도 좌표와 맞지 않아, 물이 실제 지형과 엇나가서 나타남.
- GeoJSON 좌표가 WGS84(latitude/longitude)인데, Unity World 좌표로 변환할 때 scale factor와 offset이 잘못 적용됨.
- Y축 높이값을 단순 Flood Depth로 사용하면서 Terrain 높이와 오차 발생.

해결 방법
- GeoJSON 좌표 → Unity World 좌표 변환 시 정확한 min-max 정규화 적용
- Flood Depth를 높이로 바로 적용하지 않고, Terrain 높이 기준 offset 적용

## 2. Flood Depth 값 Nan / Null로 인한 색상/높이 오류

문제 및 원인
- 일부 영역이 검은색으로 표시되거나, 물 높이가 튀는 현상 발생.
- GeoJSON 데이터 중 일부 심도값이 NaN 또는 null로 존재.
- Shader/Material에 전달될 때 계산 오류 발생

해결 방법
- GeoJSON 파싱 단계에서 NaN/Null 체크 후 기본값(0) 적용
- Shader 전달 전 0~1 범위로 정규화하여 안정적으로 색상 및 높이 매핑
