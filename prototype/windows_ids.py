"""Passive connection monitoring, compatible CSV replay, and append-only CSV scoring."""
from __future__ import annotations
import argparse
import json
import time
from pathlib import Path
from prototype.telemetry import snapshot_connections, event_to_dict
from prototype.replay import score_csv
from prototype.flow_watch import monitor_compatible_flows

def build_parser():
    parser = argparse.ArgumentParser(description="Defensive EvoNIDS Windows prototype")
    sub = parser.add_subparsers(dest="command", required=True)
    monitor = sub.add_parser("monitor", help="Passive socket snapshot (not ML classification)")
    monitor.add_argument("--interval", type=float, default=2.)
    monitor.add_argument("--iterations", type=int)
    replay = sub.add_parser("replay", help="Score a compatible flow CSV with named-column trained pipeline")
    replay.add_argument("--csv", required=True)
    replay.add_argument("--model", required=True)
    replay.add_argument("--output")
    watch = sub.add_parser("watch-flows", help="Score completed appended flow CSV records")
    watch.add_argument("--csv", required=True)
    watch.add_argument("--model", required=True)
    watch.add_argument("--interval", type=float, default=1.)
    watch.add_argument("--iterations", type=int)
    watch.add_argument("--threshold", type=float, default=.5)
    watch.add_argument("--output", help="Append JSONL decisions")
    return parser

def main():
    a = build_parser().parse_args()
    if a.command == "monitor":
        if a.interval <= 0 or (a.iterations is not None and a.iterations < 1):
            raise SystemExit("interval and iterations must be positive")
        print("Passive connections only; no blocking or ML prediction on socket metadata.")
        i = 0
        while a.iterations is None or i < a.iterations:
            print(json.dumps([event_to_dict(x) for x in snapshot_connections()], indent=2))
            i += 1
            if a.iterations is None or i < a.iterations:
                time.sleep(a.interval)
    elif a.command == "replay":
        data = score_csv(a.csv, a.model)
        if a.output:
            out = Path(a.output); out.parent.mkdir(parents=True, exist_ok=True)
            data.to_csv(out, index=False)
            print(f"Wrote {len(data)} predictions: {out}")
        else:
            print(data.head(20).to_string(index=False))
    elif a.command == "watch-flows":
        total = monitor_compatible_flows(a.csv, a.model, interval=a.interval,
                                         iterations=a.iterations, threshold=a.threshold,
                                         output=a.output)
        print(f"Scored {total} compatible flow(s)")

if __name__ == "__main__":
    main()
