from pathlib import Path

from app.tools.base import Tool


class ReadFileTool(Tool):
    name = "readFile"

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir.resolve()

    def run(self, **kwargs) -> str:
        filename = kwargs.get("fname") or kwargs.get("filename")
        if not filename or not isinstance(filename, str):
            raise ValueError("readFile requires fname")
        if "/" in filename or "\\" in filename or "*" in filename:
            raise ValueError("readFile only accepts a plain file name")
        path = (self.data_dir / filename).resolve()
        if not str(path).startswith(str(self.data_dir)):
            raise ValueError("readFile cannot read outside data directory")
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(filename)
        return path.read_text(encoding="utf-8")
