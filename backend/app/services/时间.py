from datetime import datetime, timedelta, timezone


def 解析(ts: str) -> datetime:
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts).astimezone(timezone.utc)


def 格式(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def 加秒(ts: str, 秒: int) -> str:
    return 格式(解析(ts) + timedelta(seconds=秒))


def 窗键(房间键: str, 窗起: str) -> str:
    return f"{房间键}|{窗起}"


def 对齐窗起(事件时: str, 窗长秒: int) -> str:
    dt = 解析(事件时)
    epoch = int(dt.timestamp())
    base = epoch - (epoch % 窗长秒)
    return 格式(datetime.fromtimestamp(base, tz=timezone.utc))
