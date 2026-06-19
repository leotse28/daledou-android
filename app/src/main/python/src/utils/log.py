"""
log.py - Chaquopy版日志模块
支持同时输出到 Java 回调和本地文件（按 QQ 号分文件）
"""
import os
from datetime import datetime
from src.utils.config import Config

_java_log = None  # 由 bridge.py 在 run_module 时注入用于 UI 实时显示

class FakeLogger:
    def __init__(self, qq: str = "system"):
        self._qq = qq

    def _emit(self, msg: str):
        now = datetime.now().strftime("%H:%M:%S")
        line = f"[{now}][{self._qq}] {msg}"

        # 1. 输出到 Java 桥接（主要用于系统状态和 UI 实时查看）
        if _java_log:
            _java_log(line)
        else:
            print(line)

        # 2. 写入本地文件（持久化，按 QQ 分文件）
        try:
            log_path = Config.get_log_path(self._qq)
            # 确保目录存在（Config.set_base_dir 已经创建了 logs 目录）
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
        except Exception as e:
            print(f"写入日志文件失败: {e}")

    def info(self, msg, *a, **kw):    self._emit(str(msg))
    def warning(self, msg, *a, **kw): self._emit(f"WARN: {msg}")
    def error(self, msg, *a, **kw):   self._emit(f"ERROR: {msg}")
    def debug(self, msg, *a, **kw):   self._emit(str(msg))

    def bind(self, **kwargs):
        return FakeLogger(kwargs.get("qq", self._qq))

    def remove(self): pass
    def add(self, *a, **kw): return 0

class LogBuffer:
    """提供给 TaskRunner 使用的日志转发类"""
    @staticmethod
    def add(msg: str):
        qq_logger("system").info(msg)

_loggers: dict = {}

def setup_logger() -> None:
    pass

def qq_logger(qq: str) -> FakeLogger:
    if qq not in _loggers:
        _loggers[qq] = FakeLogger(qq)
    return _loggers[qq]
