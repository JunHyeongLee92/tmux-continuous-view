from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

from .core import render_frame
from .tmux_client import TmuxClient

ESC_CLEAR = "\033[2J\033[H"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render continuous view from a tmux source pane")
    parser.add_argument("--source-pane", required=True)
    parser.add_argument("--target-pane", default=os.environ.get("TMUX_PANE", ""))
    parser.add_argument("--position", choices=["above", "below"], default="above")
    parser.add_argument("--depth", type=int, default=1)
    parser.add_argument("--interval", type=float, default=0.15)
    parser.add_argument("--plain", action="store_true", help="Strip ANSI by using tmux joined capture only")
    return parser.parse_args()


def get_target_dimensions(tmux: TmuxClient, target_pane: str) -> tuple[int, int]:
    output = tmux._run("display-message", "-p", "-t", target_pane, "#{pane_width}\t#{pane_height}")
    width, height = output.split("\t")
    return int(width), int(height)


def main() -> int:
    args = parse_args()
    if not args.target_pane:
        print("continuous-view requires a target tmux pane", file=sys.stderr)
        return 2

    tmux = TmuxClient()
    last_frame = None

    try:
        while True:
            width, height = get_target_dimensions(tmux, args.target_pane)
            status, lines = tmux.extract_view_lines(args.source_pane, height, args.position, depth=args.depth)
            frame = render_frame(content_lines=lines, width=width, height=height, status=status)

            if frame != last_frame:
                sys.stdout.write(ESC_CLEAR)
                sys.stdout.write(frame)
                sys.stdout.flush()
                last_frame = frame

            time.sleep(max(args.interval, 0.05))
    except KeyboardInterrupt:
        return 0
    except subprocess.CalledProcessError as error:
        print(f"continuous-view tmux error: {error}", file=sys.stderr)
        return error.returncode or 1


if __name__ == "__main__":
    raise SystemExit(main())
