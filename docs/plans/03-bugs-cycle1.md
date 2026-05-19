# Bugs · Cycle 1

| # | severity | symptom | reproduce | expected | actual |
|---|---|---|---|---|---|
| 1 | P2 (cosmetic) | 빈 toast 가 작은 초록 알약으로 보임 | 초기 진입 (액션 없음). 스크린샷 01-initial.png 의 bar B 영역 우측 하단에 초록 pill 잔존 | toast는 액션이 없으면 완전히 보이지 않아야 함 | `position:fixed; bottom:24px` + 빈 textContent 일 때 translateY(120%)가 거의 작용하지 않아 작은 padding 박스가 보임 |

기능적 P0/P1 버그: **0건**. 모든 단언(16종) 통과.
