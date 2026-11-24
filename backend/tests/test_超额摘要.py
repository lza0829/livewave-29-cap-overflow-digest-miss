"""超额摘要（甲·摘要入窗额封顶回滚）夹具。

钉死：
- 上限处置成功必须同票写超额摘要：窗键/上限/实际入窗额/截断额或旁路事件号/摘要号；
- 迟到撤回只动入窗额：扣减不得超过被撤回事件摘要的实际入窗额，旁路部分禁止当已入窗回滚；
- 硬约束：① 处置成功摘要空 → 报错回滚；② 扣减超摘要入窗额 → 报错回滚；③ 摘要与窗合计分叉不得提交；
- 夹具「触顶后再撤回」：甲（封顶扣减）——窗合计不低于摘要入窗额；乙（全额回滚）无差额工单须失败；
- 夹具「超额写与撤回抢锁」：扣减与合计不得撕裂；
- 核证只读接口 /api/核证/超额摘要 纯读无副作用。

运行：PYTHONPATH=backend python -m pytest backend/tests -q
"""
import json
import os
import sqlite3
import threading

import pytest


窗键13 = "房A|2026-11-22T13:00:00Z"


def _库行(sql, 参=()):
    conn = sqlite3.connect(os.environ["数据目录"] + "/播浪.db")
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(sql, 参).fetchall()
    finally:
        conn.close()


def _库写(sql, 参=()):
    conn = sqlite3.connect(os.environ["数据目录"] + "/播浪.db")
    try:
        conn.execute(sql, 参)
        conn.commit()
    finally:
        conn.close()


def _窗口(键=窗键13):
    行 = _库行("SELECT * FROM 热度窗 WHERE 窗键=?", (键,))
    return dict(行[0]) if 行 else None


def _摘要(键=窗键13):
    return [dict(r) for r in _库行("SELECT * FROM 超额摘要 WHERE 窗键=? ORDER BY 编号", (键,))]


def _装夹具(客户, 名):
    r = 客户.post("/api/装载/夹具", params={"名": 名})
    assert r.status_code == 200, r.text
    return r.json()


# ---------- ① 上限处置成功摘要不空 ----------

def test_超上限旁路同票写摘要_四件齐摘要号可现算(客户):
    from app.modules import 超额摘要 as 超

    客户.post("/api/装载/夹具", params={"名": "准时热度样例"})
    _装夹具(客户, "超上限旁路样例")

    行 = _摘要()
    assert len(行) == 3, "三个超上限事件须各留一条超额摘要（禁止处置成功摘要空）"
    for r in 行:
        assert r["窗键"] == 窗键13
        assert r["上限"] == 10000
        assert r["实际入窗额"] == 0, "整笔旁路口径：实际入窗额=0"
        assert r["旁路事件号"], "整笔旁路必须记旁路事件号"
        assert r["摘要号"].startswith("摘-")
        望 = 超.算摘要号(
            窗键=r["窗键"], 上限=r["上限"], 实际入窗额=r["实际入窗额"],
            截断额=r["截断额"], 旁路事件号=r["旁路事件号"],
        )
        assert r["摘要号"] == 望, "摘要号须可现算核对"
    事件 = sorted(r["旁路事件号"] for r in 行)
    assert 事件 == ["C2", "C4", "C6"]

    验 = 客户.post("/api/贯验").json()
    assert 验["是否通过"], 验["问题"]
    assert 验["超额摘要数"] == 3


def test_上限处置摘要写失败_整票回滚(客户, monkeypatch):
    from app.modules import 超额摘要 as 超

    客户.post("/api/装载/夹具", params={"名": "准时热度样例"})
    前事件数 = _库行("SELECT COUNT(*) c FROM 互动事件")[0]["c"]
    前窗 = _窗口()

    真写 = 超.写摘要

    def 坏写(conn, **kw):
        if kw.get("旁路事件号") == "C2":
            raise 超.摘要违例("模拟摘要写入失败（半截）")
        return 真写(conn, **kw)

    monkeypatch.setattr(超, "写摘要", 坏写)
    r = 客户.post("/api/装载/夹具", params={"名": "超上限旁路样例"})
    assert r.status_code == 409, "摘要写失败须失败闭（409），不得吞错提交"
    assert not _摘要(), "整票回滚：摘要不得落半截"
    assert _库行("SELECT COUNT(*) c FROM 互动事件")[0]["c"] == 前事件数, "事件不得半截落库"
    assert not _库行("SELECT COUNT(*) c FROM 旁路匣 WHERE 原因='超热度上限'")[0]["c"]
    assert _窗口() == 前窗, "窗合计不得半截变化"


# ---------- ② 撤回扣减不得超过摘要入窗额 ----------

def test_触顶后再撤回_甲封顶回滚_合计不低于摘要入窗额(客户):
    """甲夹具：整笔旁路事件触顶后其撤回扣减=0，窗合计保持不低于摘要入窗额（=0→不跌破顶格）。"""
    _装夹具(客户, "超上限旁路样例")
    assert _窗口()["点赞合计"] == 10000, "C1/C3/C5 入窗后顶格"

    报 = _装夹具(客户, "触顶后再撤回")
    assert 报["撤回"] == 1
    明 = 报["明细"][0]
    assert 明["命运"] == "迟到撤回封顶"
    assert 明["整笔旁路"] is True
    assert 明["摘要入窗额"] == 0, "被撤回事件 C2 是整笔旁路，摘要实际入窗额=0"
    assert 明["可扣赞"] == 0, "被旁路部分禁止当已入窗回滚：扣减=0"

    窗 = _窗口()
    assert 窗["点赞合计"] == 10000, "窗合计不得跌破摘要入窗额（=10000 顶格保持）"
    入窗额合计 = sum(r["实际入窗额"] for r in _摘要())
    assert 窗["点赞合计"] >= 入窗额合计

    撤 = _库行("SELECT * FROM 撤回单 ORDER BY 编号 DESC LIMIT 1")[0]
    assert 撤["原因"] == "迟到撤回"
    assert (撤["旧点赞"], 撤["新点赞"]) == (10000, 10000), "撤回按面额扣会跌破摘要，须封顶为 0"

    验 = 客户.post("/api/贯验").json()
    assert 验["是否通过"], 验["问题"]


def test_触顶全额回滚_无差额工单须失败(客户):
    """乙夹具：坚持按面额全额回滚，本库无差额工单→撤回失败，整票回滚。"""
    _装夹具(客户, "超上限旁路样例")
    前窗 = _窗口()
    前撤 = _库行("SELECT COUNT(*) c FROM 撤回单")[0]["c"]
    前事件 = _库行("SELECT COUNT(*) c FROM 互动事件")[0]["c"]

    r = 客户.post("/api/装载/夹具", params={"名": "触顶全额回滚"})
    assert r.status_code == 409, "无差额工单的全额回滚必须失败闭"
    assert "差额工单" in r.json()["detail"] or "全额回滚" in r.json()["detail"]
    assert _窗口() == 前窗, "整票回滚：窗合计不得变"
    assert _库行("SELECT COUNT(*) c FROM 撤回单")[0]["c"] == 前撤
    assert _库行("SELECT COUNT(*) c FROM 互动事件")[0]["c"] == 前事件


def test_摘要被篡改_提交前核证卡住整票回滚(客户):
    """硬约束③：摘要字段被改坏（摘要号对不上）后，撤回票提交前核证失败、整票回滚。"""
    _装夹具(客户, "准时热度样例")
    _装夹具(客户, "超上限旁路样例")
    前窗 = _窗口()

    # 人为把 C2 摘要的实际入窗额改掉却不重算摘要号（模拟证据分叉）
    _库写("UPDATE 超额摘要 SET 实际入窗额=1 WHERE 旁路事件号='C2'")

    r = 客户.post("/api/装载/夹具", params={"名": "触顶全额回滚"})
    assert r.status_code == 409
    assert _窗口() == 前窗, "整票回滚：窗合计不得变"


def test_可回滚额_受摘要实际入窗额封顶_截断部分不回滚(库):
    """硬约束②直测：被撤回事件摘要实际入窗额 k < 面额 → 可回滚额=k，截断部分不得回滚。"""
    from app.db import 连接
    from app.modules import 超额摘要 as 超

    conn = 连接()
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            """INSERT INTO 热度窗(窗键,房间键,窗起事件时,窗止事件时,状态,点赞合计,送礼合计,事件笔数,版本)
               VALUES ('房A|2026-11-22T15:00:00Z','房A','2026-11-22T15:00:00Z','2026-11-22T15:01:00Z','已关闭',7000,0,2,1)"""
        )
        conn.execute(
            """INSERT INTO 互动事件(事件编号,房间键,事件类型,事件时,处理时,观众键,点赞增量,送礼额,命运,窗键,批次编号)
               VALUES ('P1','房A','点赞','2026-11-22T15:00:10Z','2026-11-22T15:00:11Z','观','5000',0,'已入窗','房A|2026-11-22T15:00:00Z','b')"""
        )
        # 部分入窗事件：实际入窗额 3000，截断 2000
        超.写摘要(conn, 窗键='房A|2026-11-22T15:00:00Z', 上限=10000,
                  实际入窗额=3000, 截断额=2000, 旁路事件号='P1', 时刻='2026-11-22T15:01:10Z')
        conn.commit()
    finally:
        conn.close()

    conn = 连接()
    try:
        assert 超.可回滚额(conn, '房A|2026-11-22T15:00:00Z', 5000, 'P1') == 3000, (
            "扣减不得超过摘要实际入窗额 3000；截断的 2000 禁止当已入窗回滚"
        )
        assert 超.应拒超摘要(conn, '房A|2026-11-22T15:00:00Z', 5000) is True
        # 整笔旁路（实际入窗额=0）→ 可回滚 0
        超.写摘要(conn, 窗键='房A|2026-11-22T15:00:00Z', 上限=10000,
                  实际入窗额=0, 截断额=0, 旁路事件号='P2', 时刻='2026-11-22T15:01:11Z')
        assert 超.可回滚额(conn, '房A|2026-11-22T15:00:00Z', 9999, 'P2') == 0
    finally:
        conn.close()


# ---------- ③ 摘要与窗合计分叉不得提交 ----------

def test_摘要与窗合计分叉_提交前核证卡住(客户):
    """硬约束③：摘要入窗额合计 > 窗合计时，任何后续装载票都不得提交。"""
    _装夹具(客户, "准时热度样例")
    _装夹具(客户, "超上限旁路样例")
    # 人为把某条摘要实际入窗额抬到超过窗合计（伪造证据分叉）
    _库写("UPDATE 超额摘要 SET 实际入窗额=20000, 截断额=0 WHERE 旁路事件号='C2'")

    新票 = {
        "批次编号": "分叉后新票",
        "事件": [{
            "事件编号": "Z9", "房间键": "房A", "事件类型": "点赞",
            "事件时": "2026-11-22T14:00:10Z", "处理时": "2026-11-22T14:00:11Z",
            "观众键": "观Z", "点赞增量": 1, "送礼额": 0,
        }],
    }
    r = 客户.post("/api/装载", json=新票)
    assert r.status_code == 409, "摘要与窗合计分叉时后续票必须失败闭"
    assert not _库行("SELECT * FROM 互动事件 WHERE 事件编号='Z9'")
    assert not _库行("SELECT * FROM 装载批次 WHERE 编号='分叉后新票'")

    核 = 客户.get("/api/核证/超额摘要").json()
    assert 核["valid"] is False
    assert any("跌破摘要入窗额" in p or "越上限" in p for p in 核["问题"]), 核["问题"]


# ---------- 核证只读接口 ----------

def test_核证只读接口_纯读无副作用(客户):
    _装夹具(客户, "超上限旁路样例")
    前 = _库行("SELECT COUNT(*) c FROM 超额摘要")[0]["c"]

    体 = 客户.get("/api/核证/超额摘要").json()
    assert 体["口径"] == "摘要入窗额封顶回滚"
    assert 体["封顶回滚"] is True
    assert 体["可按面额全额"] is False
    assert 体["需差额工单"] is False
    assert 体["valid"] is True, 体["问题"]
    assert 体["摘要数"] == 3
    for s in 体["超额摘要"]:
        assert s["核证"]["通过"], s["核证"]["问题"]
    for k in ("上限写闸", "旁路匣", "撤回簿", "热度页", "对齐核验"):
        assert k in 体["协同"]

    单 = 客户.get("/api/核证/超额摘要", params={"窗键": 窗键13}).json()
    assert 单["摘要数"] == 3
    assert 单["本窗"]["摘要入窗额"] == 0

    assert _库行("SELECT COUNT(*) c FROM 超额摘要")[0]["c"] == 前, "核证接口只读不写"


def test_抗撕裂_建窗与摘要与窗行一致(客户):
    """摘要挂的窗必须真实存在，且窗合计不低于摘要入窗额、不越上限。"""
    _装夹具(客户, "准时热度样例")
    _装夹具(客户, "超上限旁路样例")
    _装夹具(客户, "触顶后再撤回")
    for r in _摘要():
        窗 = _窗口(r["窗键"])
        assert 窗 is not None
        入窗合计 = sum(x["实际入窗额"] for x in _摘要(r["窗键"]))
        assert 窗["点赞合计"] >= 入窗合计
        assert 窗["点赞合计"] <= r["上限"]


# ---------- 抢锁夹具：超额写与撤回不得撕裂 ----------

def test_并发_超额写与撤回抢锁_不撕裂(库):
    """再夹：上限处置（超上限旁路+摘要）与迟到撤回并发抢锁——合计与扣减不得撕裂。

    多线程交替推「超上限旁路样例」与「触顶后再撤回」，每票一个写事务；
    结束后：摘要与旁路证据逐条对应、窗合计=上限、不跌破摘要入窗额、贯验通过。
    """
    from app.services import 装载, 贯验

    夹具目录 = os.environ["夹具目录"]

    def 读(名):
        return json.loads((__import__("pathlib").Path(夹具目录) / f"{名}.json").read_text(encoding="utf-8"))

    装载.装一批({"批次编号": "setup-准时", "事件": 读("准时热度样例")["事件"]})

    错 = []
    屏障 = threading.Barrier(4)

    def 工(i):
        try:
            屏障.wait()
            if i % 2 == 0:
                装载.装一批(读("超上限旁路样例") | {"批次编号": f"并发-超额-{i}"})
            else:
                装载.装一批(读("触顶后再撤回") | {"批次编号": f"并发-撤回-{i}"})
        except Exception as e:  # HTTPException(409) 或 sqlite locked 都算失败闭，不是撕裂
            错.append(repr(e))

    线程 = [threading.Thread(target=工, args=(i,)) for i in range(4)]
    for t in 线程:
        t.start()
    for t in 线程:
        t.join()

    窗 = _窗口()
    assert 窗 is not None
    assert 窗["点赞合计"] <= 10000, "合计不得越上限"
    入窗合计 = sum(r["实际入窗额"] for r in _摘要())
    assert 窗["点赞合计"] >= 入窗合计, "合计不得跌破摘要入窗额（扣减与合计不撕裂）"

    # 每条超上限证据必须有同窗同事件摘要
    for r in _库行("SELECT 载荷 FROM 旁路匣 WHERE 原因='超热度上限'"):
        载荷 = json.loads(r["载荷"])
        摘要 = _库行(
            "SELECT * FROM 超额摘要 WHERE 窗键=? AND 旁路事件号=?",
            (载荷["窗键本应"], 载荷["事件编号"]),
        )
        assert 摘要, f"证据{载荷['事件编号']}缺摘要"

    验 = 贯验.跑贯验()
    assert 验["是否通过"], 验["问题"]
