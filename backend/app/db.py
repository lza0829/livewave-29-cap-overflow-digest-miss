import os
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

数据目录 = Path(os.environ.get("数据目录", Path(__file__).resolve().parent.parent / "data"))
夹具目录 = Path(os.environ.get("夹具目录", Path(__file__).resolve().parent.parent.parent / "fixtures"))


def _当前数据目录() -> Path:
    """每次取用现读环境变量：测试逐用例换库时不会被导入期常量钉死。"""
    return Path(os.environ.get("数据目录", 数据目录))


def 库路径() -> Path:
    return _当前数据目录() / "播浪.db"


# 进程内写锁：同一库同时刻只允许一个写事务。
# 上限处置（整笔旁路 + 超额摘要）与迟到撤回必须串行，否则「扣减」与「合计」会撕裂。
_写锁 = threading.RLock()


def 连接() -> sqlite3.Connection:
    数据目录_ = _当前数据目录()
    数据目录_.mkdir(parents=True, exist_ok=True)
    # isolation_level=None：交给显式 BEGIN IMMEDIATE 掌控事务边界，
    # 避免隐式事务与「写事务」嵌套；autocommit 下读连接不持锁。
    c = sqlite3.connect(数据目录_ / "播浪.db", isolation_level=None, timeout=10)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    c.execute("PRAGMA busy_timeout = 5000")
    return c


@contextmanager
def 写事务():
    """写事务：进程内写锁 + BEGIN IMMEDIATE，异常整批回滚。

    上限处置的「判定 → 旁路旁证 → 超额摘要」与迟到撤回的
    「摘要入窗额校验 → 改窗合计 → 撤回单 → 事件落库」都在本上下文内完成；
    任何一步抛错（含摘要写失败）都回滚，杜绝
    「窗已顶格、截断证据空」「撤回单已落、窗行未动」的半截状态。
    """
    with _写锁:
        conn = 连接()
        try:
            conn.execute("BEGIN IMMEDIATE")
            yield conn
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
        finally:
            conn.close()


@contextmanager
def 读事务():
    """读事务：拿一个一致快照，避免多次 SELECT 之间被并发写事务穿插。"""
    conn = 连接()
    try:
        conn.execute("BEGIN")
        yield conn
    finally:
        try:
            conn.commit()
        finally:
            conn.close()
