import asyncio
import traceback
from collections import Counter
from typing import Callable

from src.tasks.register import TaskModule
from src.utils.client import Client, RequestError
from src.utils.config import Config, ConfigResolver
from src.utils.daledou import DaLeDou
from src.utils.date_time import DateTime


class TaskRunError(Exception):
    pass


class TaskRunner:
    """异步任务执行器，支持多账号并发处理"""

    def __init__(
        self,
        cookies: dict,
        module: TaskModule,
        registry: dict,
        max_concurrency: int = 3,
        log_callback=None,
    ):
        self.cookies = cookies
        self.module = module
        self.registry = registry
        self.max_concurrency = max_concurrency
        self.log_callback = log_callback

        if not self.registry:
            raise TaskRunError(f"{self.module}模块没有注册任务")

        if not self.cookies:
            raise TaskRunError(f"未设置大乐斗Cookie")

        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.stats_lock = asyncio.Lock()
        self.queue = asyncio.Queue()
        self.statistics = Counter()

    def _log(self, msg: str):
        from src.utils.log import LogBuffer
        LogBuffer.add(msg)
        if self.log_callback:
            self.log_callback(msg)

    async def run(self) -> None:
        total_start = DateTime.now()

        for qq, cookie_dict in self.cookies.items():
            await self.queue.put((qq, cookie_dict))

        workers = [
            asyncio.create_task(self._worker()) for _ in range(self.max_concurrency)
        ]

        await self.queue.join()
        for _ in range(self.max_concurrency):
            await self.queue.put(None)

        await asyncio.gather(*workers)

        elapsed = DateTime.now() - total_start
        self._log(f"总耗时: {DateTime.format_timedelta(elapsed)}")

        success_count = self.statistics.pop("success", 0)
        failure_total = sum(self.statistics.values())
        self._log(f"所有账号处理完成 | 成功：{success_count} | 失败：{failure_total}")
        if failure_total:
            self._log("失败原因统计：")
            for reason, count in self.statistics.items():
                self._log(f"-- {reason}")

    async def _worker(self) -> None:
        while True:
            account_data = await self.queue.get()
            if account_data is None:
                self.queue.task_done()
                break

            async with self.semaphore:
                qq, cookie_dict = account_data

                if not cookie_dict:
                    failure_reason = f"{qq}: Cookie为空"
                    async with self.stats_lock:
                        self.statistics[failure_reason] += 1
                    self.queue.task_done()
                    continue

                try:
                    account_start = DateTime.now()
                    async with Client(qq, cookie_dict) as client:
                        try:
                            config_resolver = ConfigResolver(qq, self.module)
                        except Exception as e:
                            self._log(f"{qq} 配置加载失败: {e}")
                            async with self.stats_lock:
                                self.statistics[f"{qq}: 配置错误"] += 1
                            self.queue.task_done()
                            continue

                        d = DaLeDou(qq, client, config_resolver)

                        index_html = await d.get("cmd=index&style=1")
                        if "邪神秘宝" not in index_html:
                            raise RequestError("非大乐斗首页（可能繁忙或者维护）")

                        for task_name, task_func in self.registry.items():
                            try:
                                if f">{task_name}<" in index_html:
                                    d.task_name = task_name
                                    await task_func(d)
                            except RequestError:
                                raise
                            except Exception:
                                d.log(traceback.format_exc(), task_name)
                                continue

                        elapsed = DateTime.now() - account_start
                        d.log(f"{DateTime.format_timedelta(elapsed)}", "运行耗时")

                    async with self.stats_lock:
                        self.statistics["success"] += 1

                except RequestError as e:
                    self._log(f"{qq} 请求错误: {e}")
                    async with self.stats_lock:
                        self.statistics[f"{qq}: {e}"] += 1
                except Exception:
                    err = traceback.format_exc()
                    self._log(f"{qq} 未知错误: {err}")
                    async with self.stats_lock:
                        self.statistics[f"{qq}: 未知错误"] += 1
                finally:
                    self.queue.task_done()
