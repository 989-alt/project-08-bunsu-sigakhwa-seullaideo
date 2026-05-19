# Fixes · Cycle 1

| bug# | 변경 파일 | 변경 내용 | 이유 |
|---|---|---|---|
| 1 | `index.html` (toast CSS) | `.toast` 에 `opacity:0; visibility:hidden; min-height:0;` 추가, transform offset 120% → 140%, transition에 opacity/visibility 포함 | `position:fixed`+빈 textContent 박스가 padding 만으로 작은 알약을 만들어 화면에 잔존. opacity/visibility 로 확실히 숨기는 게 안전. |

Cycle 2 검증: 동일 16개 단언 모두 PASS, 스크린샷 1번에서 잔존 알약 사라짐 → P0/P1/P2 버그 0건. **Loop 종료**.
