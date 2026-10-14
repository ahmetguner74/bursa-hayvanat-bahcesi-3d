"""Read candidate zoo sheets from original M5 DGN without modifying them."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_DGN = HERE / "source-dgn"
GM = Path("C:/Program Files/GlobalMapper27.0_64bit/global_mapper.exe")
SHEETS = ("H22D01C2A", "H22D01C2B", "H22D01C2C", "H22D01C2D")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    if not GM.is_file():
        raise FileNotFoundError(GM)
    sources = [SOURCE_DGN / f"{sheet}.dgn" for sheet in SHEETS]
    before = {path.name: sha256(path) for path in sources}
    output = HERE / "source-ascii"
    output.mkdir(exist_ok=True)
    script = output / "export.gms"
    lines = [
        "GLOBAL_MAPPER_SCRIPT VERSION=1.00 ENABLE_PROGRESS=NO SHOW_WARNINGS=NO LOG_ERRLOG_MESSAGES=YES",
        f'SET_LOG_FILE FILENAME="{output / "export.log"}" APPEND_TO_FILE=NO',
    ]
    for source in sources:
        lines.extend(
            [
                f'IMPORT FILENAME="{source}" TYPE=AUTO PROMPT_IF_PROJ_UNKNOWN=NO',
                f'EXPORT_VECTOR FILENAME="{output / (source.stem + ".txt")}" TYPE=SIMPLE_ASCII EXPORT_ATTRS=YES EXPORT_ELEV=YES COORD_PRECISION=6',
                "UNLOAD_ALL",
            ]
        )
    lines.append("FORCE_EXIT")
    script.write_text("\n".join(lines) + "\n", encoding="ascii")
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    subprocess.run(
        [str(GM), str(script)], cwd=output, check=True, timeout=300,
        creationflags=subprocess.CREATE_NO_WINDOW, startupinfo=startup,
    )
    log = (output / "export.log").read_text(encoding="utf-8", errors="replace")
    if "Script processing COMPLETED" not in log:
        raise RuntimeError(log[-2000:])
    after = {path.name: sha256(path) for path in sources}
    if after != before:
        raise RuntimeError("A source DGN changed during export")
    result = {
        "purpose": "independent intermediate read of candidate zoo DGN sheets",
        "sourceDgnSha256": before,
        "sourceDgnUnchanged": True,
        "globalMapper": str(GM),
        "exports": {
            sheet: {"sha256": sha256(output / f"{sheet}.txt"), "bytes": (output / f"{sheet}.txt").stat().st_size}
            for sheet in SHEETS
        },
        "identityLimit": "SIMPLE_ASCII does not preserve native DGN element IDs",
    }
    (output / "manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
