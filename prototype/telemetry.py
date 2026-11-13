from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import platform
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

def _address(value):
    if not value:
        return ""
    ip, port = getattr(value, "ip", None), getattr(value, "port", None)
    if ip is None:
        try:
            ip, port = value
        except Exception:
            return str(value)
    return f"{ip}:{port}" if port is not None else str(ip)

def snapshot_connections():
    try:
        sockets = psutil.net_connections(kind="inet")
    except (psutil.AccessDenied, PermissionError):
        sockets = []
    now = datetime.now(timezone.utc).isoformat()
    records = []
    for conn in sockets:
        kind = getattr(conn, "type", None)
        protocol = "TCP" if kind == 1 or str(kind).endswith("SOCK_STREAM") else "UDP"
        pid = getattr(conn, "pid", None)
        name = None
        if pid:
            try:
                name = psutil.Process(pid).name()
            except (psutil.NoSuchProcess, psutil.AccessDenied, PermissionError):
                pass
        records.append(ConnectionEvent(now, protocol,
            _address(getattr(conn, "laddr", None)),
            _address(getattr(conn, "raddr", None)),
            str(getattr(conn, "status", "")), pid, name))
    return records

def event_to_dict(event):
    return {**asdict(event), "host_os": platform.platform()}
