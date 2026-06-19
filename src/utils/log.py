"""Android适配版日志模块 - 替换loguru文件sink为内存队列"""
import sys
import logging
from pathlib import Path


class LogBuffer:
    """全局日志缓冲区，供UI层读取"""
    _logs = []
    _callbacks = []

    @classmethod
    def add(cls, msg: str):
        cls._logs.append(msg)
        if len(cls._logs) > 2000:
            cls._logs.pop(0)
        for cb in cls._callbacks:
            try:
                cb(msg)
            except Exception:
                pass

    @classmethod
    def register_callback(cls, cb):
        cls._callbacks.append(cb)

    @classmethod
    def get_all(cls):
        return list(cls._logs)

    @classmethod
    def clear(cls):
        cls._logs.clear()


class FakeLogger:
    """模拟loguru Logger接口"""
    def __init__(self, qq: str = "系统"):
        self._qq = qq

    def _log(self, level: str, msg: str):
        from datetime import datetime
        now = datetime.now().strftime("%H:%M:%S")
        line = f"[{now}][{self._qq}] {msg}"
        LogBuffer.add(line)
        print(line)

    def info(self, msg, *args, **kwargs):
        self._log("INFO", str(msg))

    def warning(self, msg, *args, **kwargs):
        self._log("WARN", str(msg))

    def error(self, msg, *args, **kwargs):
        self._log("ERROR", str(msg))

    def debug(self, msg, *args, **kwargs):
        self._log("DEBUG", str(msg))

    def bind(self, **kwargs):
        qq = kwargs.get("qq", self._qq)
        return FakeLogger(qq)

    def remove(self):
        pass

    def add(self, *args, **kwargs):
        return 0


_loggers = {}
_global_logger = FakeLogger("系统")


def setup_logger() -> None:
    pass


def qq_logger(qq: str) -> FakeLogger:
    if qq not in _loggers:
        _loggers[qq] = FakeLogger(qq)
    return _loggers[qq]
