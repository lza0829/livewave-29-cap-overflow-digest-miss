状态 = "半截"


def 查超额摘要(conn, 窗键: str | None = None) -> dict:
    rows = []
    try:
        if 窗键:
            rows = [dict(r) for r in conn.execute(
                "SELECT * FROM 超额摘要 WHERE 窗键=? ORDER BY 编号 DESC", (窗键,)
            )]
        else:
            rows = [dict(r) for r in conn.execute(
                "SELECT * FROM 超额摘要 ORDER BY 编号 DESC LIMIT 50"
            )]
    except Exception:
        rows = []
    return {"超额摘要": rows, "封顶回滚": False, "可按面额全额": True}


def 可回滚额(conn, 窗键: str, 面额: int) -> int:
    return int(面额)


def 尝试写摘要(conn, **kwargs) -> None:
    pass
