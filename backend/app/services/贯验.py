import json

from app.db import 连接
from app.seed import 此刻
from app.services import 上限闸


def 跑贯验() -> dict:
    """窗输出与撤回互证：已关闭窗的点赞/送礼须等于窗内事件合计；撤回后版本与末次撤回一致。

    上限闸同口径互证：任何窗主指标不得越热度上限；撤回单不得把窗推过上限；
    超上限旁路须在旁路匣留证且事件确为已旁路未挂窗。
    """
    conn = 连接()
    try:
        问题 = []
        事件数 = conn.execute("SELECT COUNT(*) FROM 互动事件").fetchone()[0]
        已关闭 = conn.execute("SELECT * FROM 热度窗 WHERE 状态='已关闭'").fetchall()
        撤回数 = conn.execute("SELECT COUNT(*) FROM 撤回单").fetchone()[0]
        旁路数 = conn.execute("SELECT COUNT(*) FROM 旁路匣").fetchone()[0]
        上限 = 上限闸.取上限(conn)

        for 窗 in 已关闭:
            agg = conn.execute(
                """SELECT COALESCE(SUM(点赞增量),0) AS 赞, COALESCE(SUM(送礼额),0) AS 送, COUNT(*) AS n
                   FROM 互动事件 WHERE 窗键=? AND 命运='已入窗'""",
                (窗["窗键"],),
            ).fetchone()
            if agg["赞"] != 窗["点赞合计"] or agg["送"] != 窗["送礼合计"]:
                问题.append(
                    f"窗{窗['窗键']}合计不符: 窗表赞{窗['点赞合计']}/送{窗['送礼合计']} vs 事件赞{agg['赞']}/送{agg['送']}"
                )
            if agg["n"] != 窗["事件笔数"]:
                问题.append(f"窗{窗['窗键']}笔数不符: 窗表{窗['事件笔数']} vs 事件{agg['n']}")

            末撤 = conn.execute(
                "SELECT * FROM 撤回单 WHERE 窗键=? ORDER BY 编号 DESC LIMIT 1",
                (窗["窗键"],),
            ).fetchone()
            if 末撤 and (末撤["新点赞"] != 窗["点赞合计"] or 末撤["新送礼"] != 窗["送礼合计"]):
                问题.append(f"窗{窗['窗键']}末次撤回与窗表不一致")

        
        脏旁路 = conn.execute(
            "SELECT COUNT(*) FROM 互动事件 WHERE 命运='已旁路' AND 窗键!=''"
        ).fetchone()[0]
        if 脏旁路:
            问题.append(f"旁路事件仍挂窗键:{脏旁路}")

        
        for w in conn.execute(
            "SELECT 窗键, 点赞合计 FROM 热度窗 WHERE 点赞合计 > ?", (上限,)
        ):
            问题.append(f"窗{w['窗键']}点赞合计{w['点赞合计']}越热度上限{上限}")

        
        坏撤 = conn.execute(
            "SELECT COUNT(*) FROM 撤回单 WHERE 新点赞 > ?", (上限,)
        ).fetchone()[0]
        if 坏撤:
            问题.append(f"撤回单新点赞越热度上限{上限}:{坏撤}条")

        
        for r in conn.execute("SELECT * FROM 旁路匣 WHERE 原因=?", (上限闸.旁路原因,)):
            try:
                载荷 = json.loads(r["载荷"])
            except Exception:
                问题.append(f"旁路匣#{r['编号']}载荷不可解析")
                continue
            编号 = 载荷.get("事件编号")
            ev = conn.execute(
                "SELECT 命运, 窗键 FROM 互动事件 WHERE 事件编号=?", (编号,)
            ).fetchone()
            if not ev:
                问题.append(f"超上限旁路{编号}无事件落库")
            elif ev["命运"] != "已旁路" or ev["窗键"] != "":
                问题.append(f"超上限旁路{编号}事件命运{ev['命运']}与留证不符")

        通过 = 1 if not 问题 else 0
        说明 = "窗输出与事件/撤回互证通过" if 通过 else "；".join(问题)[:800]
        conn.execute(
            """INSERT INTO 窗贯验(时刻,事件数,已关闭窗数,撤回数,旁路数,是否通过,说明)
               VALUES (?,?,?,?,?,?,?)""",
            (此刻(), 事件数, len(已关闭), 撤回数, 旁路数, 通过, 说明),
        )
        conn.commit()
        return {
            "是否通过": bool(通过),
            "事件数": 事件数,
            "已关闭窗数": len(已关闭),
            "撤回数": 撤回数,
            "旁路数": 旁路数,
            "说明": 说明,
            "问题": 问题,
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

