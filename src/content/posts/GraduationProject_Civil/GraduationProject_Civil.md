---
title: GraduationProject_Civil
published: 2025-09-08
description: 'The objective is to develop an application capable of visualising flood situations in augmented reality (AR) within the physical space of urban areas where flood and inundation risks exist.'
image: "./Civil_Img.jpeg"
tags: [Unity, GraduationProject, C#, Visualization]
category: 'Unity'
draft: false 
lang: 'C#'
---
::github{repo="Hajiie/AR_Flooding_Mobile"}

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
