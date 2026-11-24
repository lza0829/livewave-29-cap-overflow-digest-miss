import os
import sys
from pathlib import Path

import pytest

后端根 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(后端根))
os.environ.setdefault("夹具目录", str(后端根.parent / "fixtures"))


@pytest.fixture()
def 客户(tmp_path, monkeypatch):
    """每用例一座新库；startup 时建表播种。"""
    monkeypatch.setenv("数据目录", str(tmp_path / "data"))
    from app.main import app
    from fastapi.testclient import TestClient

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def 库(tmp_path, monkeypatch):
    """裸库路径，供服务级/并发用例。"""
    monkeypatch.setenv("数据目录", str(tmp_path / "data"))
    from app import seed

    seed.初始化库()
    return tmp_path / "data" / "播浪.db"
