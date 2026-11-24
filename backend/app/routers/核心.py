import json
import sqlite3

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import 夹具目录, 连接
from app.modules import 超额摘要
from app.services import 上限闸, 装载, 贯验, 目录

路由 = APIRouter(prefix="/api")


class 装载请求(BaseModel):
    批次编号: str = ""
    事件: list = Field(default_factory=list)


@路由.get("/健康")
def 健康():
    return {
        "正常": True,
        "项目": "播浪",
        "骨架": "互动事件入流→事件时间水位线推进→热度窗关闭发射→迟到修正撤回→窗输出与撤回互证",
    }


@路由.get("/总览")
def 取总览():
    return 目录.总览()


@路由.get("/站规")
def 站规():
    conn = 连接()
    try:
        return {r["键"]: r["值"] for r in conn.execute("SELECT 键, 值 FROM 站规")}
    finally:
        conn.close()


@路由.get("/直播间")
def 列直播间():
    conn = 连接()
    try:
        rooms = [dict(r) for r in conn.execute("SELECT * FROM 直播间 ORDER BY 房间键")]
        for r in rooms:
            wm = conn.execute("SELECT * FROM 水位线 WHERE 房间键=?", (r["房间键"],)).fetchone()
            r["水位线"] = dict(wm) if wm else None
        return rooms
    finally:
        conn.close()


@路由.get("/事件")
def 列事件(命运: str = ""):
    conn = 连接()
    try:
        if 命运:
            rows = conn.execute(
                "SELECT * FROM 互动事件 WHERE 命运=? ORDER BY 事件时 DESC LIMIT 200", (命运,)
            )
        else:
            rows = conn.execute("SELECT * FROM 互动事件 ORDER BY 事件时 DESC LIMIT 200")
        return [dict(r) for r in rows]
    finally:
        conn.close()


@路由.get("/水位线")
def 列水位线():
    conn = 连接()
    try:
        return [dict(r) for r in conn.execute("SELECT * FROM 水位线 ORDER BY 房间键")]
    finally:
        conn.close()


@路由.get("/热度窗")
def 列热度窗(状态: str = ""):
    conn = 连接()
    try:
        if 状态:
            rows = conn.execute(
                "SELECT * FROM 热度窗 WHERE 状态=? ORDER BY 窗起事件时 DESC", (状态,)
            )
        else:
            rows = conn.execute("SELECT * FROM 热度窗 ORDER BY 窗起事件时 DESC")
        return [dict(r) for r in rows]
    finally:
        conn.close()


@路由.get("/撤回单")
def 列撤回():
    conn = 连接()
    try:
        return [dict(r) for r in conn.execute("SELECT * FROM 撤回单 ORDER BY 编号 DESC LIMIT 100")]
    finally:
        conn.close()


@路由.get("/旁路匣")
def 列旁路():
    conn = 连接()
    try:
        return [dict(r) for r in conn.execute("SELECT * FROM 旁路匣 ORDER BY 编号 DESC LIMIT 100")]
    finally:
        conn.close()


@路由.get("/上限闸")
def 列上限闸():
    """上限闸只读接口：上限、各窗合计、超上限旁路证据、valid。"""
    conn = 连接()
    try:
        return 上限闸.全闸况(conn)
    finally:
        conn.close()


@路由.get("/上限闸/窗")
def 取上限闸(窗键: str = ""):
    """单窗闸况（查询参数传窗键；Starlette 路径参数不支持中文名）。"""
    conn = 连接()
    try:
        况 = 上限闸.闸况(conn, 窗键)
        if 况 is None:
            raise HTTPException(404, f"热度窗不存在:{窗键}")
        return 况
    finally:
        conn.close()


@路由.get("/批次")
def 列批次():
    conn = 连接()
    try:
        out = []
        for r in conn.execute("SELECT * FROM 装载批次 ORDER BY 时刻 DESC LIMIT 30"):
            d = dict(r)
            try:
                d["报告"] = json.loads(d["报告"])
            except Exception:
                pass
            out.append(d)
        return out
    finally:
        conn.close()


@路由.post("/装载")
def 做装载(体: 装载请求):
    try:
        return 装载.装一批(体.model_dump())
    except (装载.撤回违例, 超额摘要.摘要违例) as e:
        raise HTTPException(409, f"失败闭（整票回滚）：{e}") from e
    except sqlite3.OperationalError as e:
        if "locked" in str(e).lower():
            raise HTTPException(409, f"入流并发冲突（写锁竞争），失败闭拒绝：{e}") from e
        raise HTTPException(500, str(e)) from e


@路由.post("/装载/夹具")
def 装夹具(名: str = "准时热度样例"):
    路径 = 夹具目录 / f"{名}.json"
    if not 路径.exists():
        raise HTTPException(404, f"夹具不存在:{名}")
    try:
        return 装载.装一批(json.loads(路径.read_text(encoding="utf-8")))
    except (装载.撤回违例, 超额摘要.摘要违例) as e:
        raise HTTPException(409, f"失败闭（整票回滚）：{e}") from e
    except sqlite3.OperationalError as e:
        if "locked" in str(e).lower():
            raise HTTPException(409, f"入流并发冲突（写锁竞争），失败闭拒绝：{e}") from e
        raise HTTPException(500, str(e)) from e


@路由.post("/贯验")
def 做贯验():
    return 贯验.跑贯验()


@路由.get("/贯验")
def 列贯验():
    conn = 连接()
    try:
        return [dict(r) for r in conn.execute("SELECT * FROM 窗贯验 ORDER BY 编号 DESC LIMIT 20")]
    finally:
        conn.close()


@路由.get("/空桩")
def 空桩():
    from app import modules

    return modules.列表()

from app.modules import 超额摘要 as 超


@路由.get("/核证/超额摘要")
def 取超额摘要(窗键: str | None = None):
    """超额摘要核证只读接口：与上限写闸/旁路匣/撤回簿/热度页/对齐核验协同。纯读不写。"""
    conn = 连接()
    try:
        return 超.查超额摘要(conn, 窗键)
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

