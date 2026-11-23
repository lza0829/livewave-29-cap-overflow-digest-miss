from pathlib import Path

根 = Path(__file__).resolve().parent


def 列表() -> list:
    out = []
    for p in sorted(根.iterdir()):
        if p.is_dir() and not p.name.startswith("_"):
            init = p / "__init__.py"
            状态 = "未实现"
            说明 = ""
            if init.exists():
                text = init.read_text(encoding="utf-8")
                for line in text.splitlines():
                    if line.startswith("状态"):
                        状态 = line.split("=", 1)[-1].strip().strip("\"'")
                    if line.startswith('"""') and "空桩" in text:
                        说明 = text.split('"""')[1].strip().splitlines()[0]
            out.append({"名": p.name, "状态": 状态, "说明": 说明})
    return out
