from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import platform
from typing import Iterable

import psutil


@dataclass(frozen=True)
class ConnectionEvent:
    timestamp_utc: str
    protocol: str
    local_address: str
    remote_address: str
    status: str
    pid: int | None
    process_name: str | None


def _address(value: object) -> str:
    if not value:
        return ""
    ip = getattr(value, "ip", None)
    port = getattr(value, "port", None)
    if ip is None:
        try:
            ip, port = value  # type: ignore[misc]
        except Exception:
            return str(value)
    return f"{ip}:{port}" if port is not None else str(ip)


def snapshot_connections() -> list[ConnectionEvent]:
    events: list[ConnectionEvent] = []
    now = datetime.now(timezone.utc).isoformat()

    try:
        connections: Iterable = psutil.net_connections(kind="inet")
    except (psutil.AccessDenied, PermissionError):
        connections = []

    for conn in connections:
        sock_type = getattr(conn, "type", None)
        protocol = "TCP" if str(sock_type).endswith("SOCK_STREAM") or sock_type == 1 else "UDP"
        pid = getattr(conn, "pid", None)
        process_name = None
        if pid:
            try:
                process_name = psutil.Process(pid).name()
            except (psutil.NoSuchProcess, psutil.AccessDenied, PermissionError):
                process_name = None

        events.append(
            ConnectionEvent(
                timestamp_utc=now,
                protocol=protocol,
                local_address=_address(getattr(conn, "laddr", None)),
                remote_address=_address(getattr(conn, "raddr", None)),
                status=str(getattr(conn, "status", "")),
                pid=pid,
                process_name=process_name,
            )
        )

    return events


def event_to_dict(event: ConnectionEvent) -> dict:
    result = asdict(event)
    result["host_os"] = platform.platform()
    return result
