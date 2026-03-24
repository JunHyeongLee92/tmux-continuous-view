# Changelog

## 2026-03-23

### 수정
- `capture-pane -J` 사용으로 화면 줄이 합쳐지던 문제를 제거해, 줄바꿈으로 넘어간 텍스트가 viewer1→source 경계에서도 실제 화면 줄 기준으로 자연스럽게 이어지도록 수정
- 3분할에서 wrapped line 경계가 depth 1/depth 2 사이를 가를 때 일부 내용이 크게 건너뛰어 보이던 문제를 줄이기 위해 depth 2 경계에 wrapped row overlap 보정 추가

### 테스트
- wrapped screen row 보존 및 depth 1 연속성 검증용 `tests/test_tmux_client.py` 추가
- depth 2 wrapped boundary overlap 회귀 테스트 추가

## 2026-03-20

### 추가
- tmux 연속 읽기용 `tmux-continuous-view` 초기 구현 추가
- `prefix + \`로 viewer 시작, `prefix + |`로 viewer 종료 기능 추가
- source pane 기준 read-only viewer 동기화 기능 추가
- ANSI 색상 보존 렌더링 추가
- 상태줄 compact 포맷(`CV dN · %pane · cmd · ↑scroll`) 추가
- 2분할에서 같은 시작 키를 다시 누르면 3분할로 확장되는 동작 추가
- viewer depth(`viewer1`, `viewer2`) 및 tmux pane metadata 추가

### 변경
- 2분할 시작 시 가능한 경우 50:50에 가깝게 배치되도록 조정
- `prefix + \` 실행 후 포커스가 자동으로 가장 오른쪽 source pane으로 복귀하도록 변경
- 시작/확장 시 source pane 최소 폭을 보장하도록 레이아웃 정책 변경
- 3분할 확장 시 pane 폭이 다시 거의 1/3씩 되도록 균등 분배 정책으로 조정
- 2번째 viewer 확장 시 기존 viewer 최소 폭도 유지하도록 조정
- viewer 종료 시 균등 재배치 대신 기존 source 우선 폭을 유지하도록 변경
- viewer pane에 은은한 배경 스타일을 적용해 source pane과 시각적으로 구분되도록 변경
- README 사용법을 2분할/3분할 동작 기준으로 갱신

### 제한 사항
- `vim`, `nvim`, `htop`, `top`, `nano` 등 full-screen TUI는 아직 비지원
- 입력은 source pane에서만 수행되고 viewer pane은 읽기 전용

### 검증
- `python3 -m unittest discover -s tests -q`
- `python3 -m compileall continuous_view`
- `bash -n scripts/start.sh`
- `bash -n scripts/stop.sh`
- tmux detached smoke test로 2→3 확장, 단계적 종료, 폭 재정렬 확인
