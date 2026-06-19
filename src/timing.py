"""定时任务模块 - Android适配版（用asyncio替换schedule库）"""
import asyncio
from datetime import datetime, time

from src.run import TaskRunner
from src.tasks.register import (
    TaskModule,
    TASKS_REGISTRY,
    MODULE_METADATA,
    get_all_modules,
)
from src.utils.config import Config
from src.utils.log import LogBuffer


_running = False
_task_handle = None


def _log(msg: str):
    LogBuffer.add(msg)


async def run_module(module: TaskModule, log_callback=None):
    """执行指定模块的所有任务"""
    registry = TASKS_REGISTRY.get(module, {})
    if not registry:
        _log(f"[定时任务] {module.value} 模块没有注册任务，跳过")
        return

    _log(f"[定时任务] 开始执行 {module.value} 模块 ({len(registry)} 个任务)")
    cookies = Config.load_cookies()
    if not cookies:
        _log("[定时任务] 未配置Cookie，跳过")
        return

    runner = TaskRunner(cookies, module, registry, log_callback=log_callback)
    await runner.run()
    _log(f"[定时任务] {module.value} 模块执行完成")


async def _scheduler_loop(log_callback=None):
    """定时调度循环"""
    global _running
    _running = True
    _log("定时任务调度器已启动")

    scheduled = {}
    for module in get_all_modules():
        meta = MODULE_METADATA.get(module, {})
        t_str = meta.get("schedule_time")
        if t_str:
            h, m, s = map(int, t_str.split(":"))
            scheduled[module] = time(h, m, s)
            _log(f"  - {module.value}: 每天 {t_str}")

    executed_today = set()

    while _running:
        now = datetime.now()
        today = now.date()
        current_t = now.time()

        # 每天重置
        for mod in list(executed_today):
            scheduled_t = scheduled.get(mod)
            if scheduled_t and current_t < scheduled_t:
                executed_today.discard(mod)

        for module, t in scheduled.items():
            key = (module, today)
            if key not in executed_today:
                if current_t >= t:
                    executed_today.add(key)
                    _log(f"[定时] 触发 {module.value} 任务")
                    asyncio.create_task(run_module(module, log_callback))

        await asyncio.sleep(30)

    _log("定时调度器已停止")


def start_scheduler(log_callback=None):
    global _task_handle
    loop = asyncio.get_event_loop()
    _task_handle = loop.create_task(_scheduler_loop(log_callback))
    return _task_handle


def stop_scheduler():
    global _running, _task_handle
    _running = False
    if _task_handle:
        _task_handle.cancel()
        _task_handle = None
