"""定时调度模块 - Chaquopy版"""
import asyncio
from datetime import datetime, time
from src.tasks.register import TASKS_REGISTRY, MODULE_METADATA, get_all_modules


async def scheduler_loop(log_fn, is_running_fn):
    """
    定时调度主循环
    log_fn: 日志回调函数
    is_running_fn: 返回bool，False时退出循环
    """
    log_fn("定时调度器已启动")

    scheduled = {}
    for module in get_all_modules():
        meta = MODULE_METADATA.get(module, {})
        t_str = meta.get("schedule_time")
        if t_str:
            h, m, s = map(int, t_str.split(":"))
            scheduled[module] = time(h, m, s)
            log_fn(f"  - {module.value}: 每天 {t_str}")

    executed_today = set()

    while is_running_fn():
        now = datetime.now()
        today = now.date()
        current_t = now.time()

        # 每天重置
        to_reset = [k for k in list(executed_today) if current_t < scheduled.get(k[0], time(23, 59))]
        for k in to_reset:
            executed_today.discard(k)

        for module, t in scheduled.items():
            key = (module, today)
            if key not in executed_today and current_t >= t:
                executed_today.add(key)
                log_fn(f"[定时] 触发 {module.value} 任务")
                asyncio.create_task(_run_module(module, log_fn))

        await asyncio.sleep(30)

    log_fn("定时调度器已停止")


async def _run_module(module, log_fn):
    from src.run import TaskRunner, TaskRunError
    from src.utils.config import Config

    registry = TASKS_REGISTRY.get(module, {})
    if not registry:
        log_fn(f"[定时] {module.value} 没有注册任务")
        return

    cookies = Config.load_cookies()
    if not cookies:
        log_fn("[定时] 未配置Cookie，跳过")
        return

    log_fn(f"[定时] 开始执行 {module.value}")
    try:
        runner = TaskRunner(cookies, module, registry, log_callback=log_fn)
        await runner.run()
        log_fn(f"[定时] {module.value} 执行完成")
    except TaskRunError as e:
        log_fn(f"[定时] ❌ {e}")
    except Exception as e:
        log_fn(f"[定时] ❌ {e}")
