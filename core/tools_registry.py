from typing import Callable, Dict, Any
from ..tools import fs_ops, os_control, browser, ocr, binary_ops, net


class ToolsRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, Callable[[dict], Any]] = {}

    def register(self, name: str, func: Callable[[dict], Any]) -> None:
        self._tools[name] = func

    def call(self, name: str, args: dict) -> Any:
        if name not in self._tools:
            raise KeyError(f"Tool not found: {name}")
        return self._tools[name](args)

    def list_tools(self) -> Dict[str, str]:
        return {k: getattr(v, "__doc__", "") for k, v in self._tools.items()}


def build_default_registry() -> ToolsRegistry:
    registry = ToolsRegistry()
    registry.register("filesystem.search", fs_ops.filesystem_search)
    registry.register("filesystem.hash", fs_ops.filesystem_hash)
    registry.register("os.input_text", os_control.os_input_text)
    registry.register("os.keypress", os_control.os_keypress)
    registry.register("browser.goto", browser.browser_goto)
    registry.register("browser.fill", browser.browser_fill)
    registry.register("ocr.read", ocr.ocr_read)
    registry.register("binary.filetype", binary_ops.binary_filetype)
    registry.register("binary.pe_info", binary_ops.binary_pe_info)
    registry.register("net.http_get", net.http_get)
    registry.register("net.download", net.download)
    return registry
