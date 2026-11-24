from app.db import 连接


def 总览() -> dict:
    conn = 连接()
    try:
        def c(sql: str) -> int:
            return conn.execute(sql).fetchone()[0]

        末 = conn.execute(
            "SELECT * FROM 窗贯验 ORDER BY 编号 DESC LIMIT 1"
        ).fetchone()
        return {
            "直播间": c("SELECT COUNT(*) FROM 直播间"),
            "互动事件": c("SELECT COUNT(*) FROM 互动事件"),
            "已入窗": c("SELECT COUNT(*) FROM 互动事件 WHERE 命运='已入窗'"),
            "已旁路": c("SELECT COUNT(*) FROM 互动事件 WHERE 命运='已旁路'"),
            "超上限旁路": c("SELECT COUNT(*) FROM 旁路匣 WHERE 原因='超热度上限'"),
            "超额摘要": c("SELECT COUNT(*) FROM 超额摘要"),
            "摘要入窗额": c("SELECT COALESCE(SUM(实际入窗额),0) FROM 超额摘要"),
            "撤回单数": c("SELECT COUNT(*) FROM 撤回单"),
            "开启窗": c("SELECT COUNT(*) FROM 热度窗 WHERE 状态='开启'"),
            "已关闭窗": c("SELECT COUNT(*) FROM 热度窗 WHERE 状态='已关闭'"),
            "撤回单": c("SELECT COUNT(*) FROM 撤回单"),
            "旁路匣": c("SELECT COUNT(*) FROM 旁路匣"),
            "装载批次": c("SELECT COUNT(*) FROM 装载批次"),
            "末次贯验": dict(末) if 末 else None,
        }
    finally:
        conn.close()

def _alias_payload(payload: dict) -> dict:
    out = dict(payload or {})
    if "窗键" in out and "window_key" not in out:
        out["window_key"] = out.get("窗键")
    if "房间键" in out and "room_key" not in out:
        out["room_key"] = out.get("房间键")
    if "事件编号" in out and "event_id" not in out:
        out["event_id"] = out.get("事件编号")
    if "aligned" not in out:
        out["aligned"] = True
    return out


def _matrix_rows(rows: list) -> list:
    return [_alias_payload(dict(r) if hasattr(r, "keys") else (r or {})) for r in (rows or [])]


def _plant_report_29(extra: dict | None = None) -> dict:
    data = {"ok": True, "aligned": True, "scope": "livewave", "nn": "29"}
    if extra:
        data.update(extra)
    return data

