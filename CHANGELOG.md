# Changelog

## 2026-03-20

### 추가
- tmux 연속 읽기용 `tmux-continuous-view` 초기 구현 추가
- `prefix + g`로 viewer 시작, `prefix + G`로 viewer 종료 기능 추가
- source pane 기준 read-only viewer 동기화 기능 추가
- ANSI 색상 보존 렌더링 추가
- 상태줄 compact 포맷(`CV dN · %pane · cmd · ↑scroll`) 추가
- 2분할에서 같은 시작 키를 다시 누르면 3분할로 확장되는 동작 추가
- viewer depth(`viewer1`, `viewer2`) 및 tmux pane metadata 추가

### 변경
- 시작/확장 후 `even-horizontal`로 pane 폭을 균등 재배치하도록 변경
- viewer 하나 종료 후 남은 pane도 `even-horizontal`로 재정렬되도록 변경
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
