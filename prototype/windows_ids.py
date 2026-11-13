from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from prototype.replay import score_csv
from prototype.flow_watch import monitor_compatible_flows
from prototype.telemetry import event_to_dict, snapshot_connections


def run_monitor(interval: float, iterations: int | None) -> None:
    print("Passive connection monitor. No traffic is blocked or modified.")
    count = 0
    while iterations is None or count < iterations:
        events = snapshot_connections()
        print(json.dumps([event_to_dict(e) for e in events], indent=2))
        count += 1
        if iterations is None or count < iterations:
            time.sleep(interval)


def run_replay(csv_path: str, model_path: str, output_path: str | None) -> None:
    scored = score_csv(csv_path, model_path)
    if output_path:
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        scored.to_csv(target, index=False)
        print(f"Saved scored rows to {target}")
    else:
        print(scored.head(20).to_string(index=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Passive Windows IDS prototype for COMP1818 EvoNIDS."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    monitor = subparsers.add_parser("monitor", help="Show passive local socket telemetry.")
    monitor.add_argument("--interval", type=float, default=2.0)
    monitor.add_argument("--iterations", type=int, default=None)

    replay = subparsers.add_parser(
        "replay", help="Score UNSW-NB15-compatible CSV rows with a trained pipeline."
    )
    replay.add_argument("--csv", required=True)
    replay.add_argument("--model", required=True)
    replay.add_argument("--output", default=None)

    flow = subparsers.add_parser("watch-flows", help="Score complete new rows from externally exported compatible flow CSV.")
    flow.add_argument("--csv", required=True)
    flow.add_argument("--model", required=True)
    flow.add_argument("--interval", type=float, default=1.0)
    flow.add_argument("--iterations", type=int, default=None)
    flow.add_argument("--threshold", type=float, default=0.5)
    flow.add_argument("--output", default=None, help="Append JSONL predictions to this file")

    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "monitor":
        run_monitor(args.interval, args.iterations)
    elif args.command == "replay":
        run_replay(args.csv, args.model, args.output)
    elif args.command == "watch-flows":
        total = monitor_compatible_flows(args.csv, args.model, interval=args.interval,
                                         iterations=args.iterations, threshold=args.threshold,
                                         output=args.output)
        print(f"Scored {total} compatible flow(s)")


if __name__ == "__main__":
    main()
