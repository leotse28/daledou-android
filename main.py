"""
大乐斗 Android 版 - Kivy UI 主程序
"""
import asyncio
import os
import sys
import threading
from pathlib import Path

# Kivy imports
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.metrics import sp, dp
from kivy.utils import get_color_from_hex

# 初始化配置
from src.utils.config import Config

Config.init_default_config()

# 导入任务模块（触发注册）
import src.tasks.noon   # noqa
import src.tasks.evening  # noqa

from src.tasks.register import TASKS_REGISTRY, TaskModule, get_all_modules, MODULE_METADATA
from src.utils.log import LogBuffer

# ============ KV 布局定义 ============
KV = """
#:import dp kivy.metrics.dp
#:import sp kivy.metrics.sp

<RoundButton@Button>:
    background_color: 0, 0, 0, 0
    background_normal: ''
    canvas.before:
        Color:
            rgba: (0.13, 0.59, 0.95, 1) if self.state == 'normal' else (0.08, 0.43, 0.75, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(8)]

<DangerButton@Button>:
    background_color: 0, 0, 0, 0
    background_normal: ''
    canvas.before:
        Color:
            rgba: (0.9, 0.26, 0.21, 1) if self.state == 'normal' else (0.72, 0.15, 0.11, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(8)]

<GreenButton@Button>:
    background_color: 0, 0, 0, 0
    background_normal: ''
    canvas.before:
        Color:
            rgba: (0.18, 0.65, 0.31, 1) if self.state == 'normal' else (0.11, 0.47, 0.22, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(8)]

<GreyButton@Button>:
    background_color: 0, 0, 0, 0
    background_normal: ''
    canvas.before:
        Color:
            rgba: (0.45, 0.45, 0.45, 1) if self.state == 'normal' else (0.3, 0.3, 0.3, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(8)]

ScreenManager:
    MainScreen:
    CookieScreen:
    LogScreen:
    ConfigScreen:

<MainScreen>:
    name: 'main'
    canvas.before:
        Color:
            rgba: 0.10, 0.10, 0.13, 1
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(12)

        # Header
        BoxLayout:
            size_hint_y: None
            height: dp(56)
            Label:
                text: '🎮 大乐斗 Android 助手'
                font_size: sp(20)
                bold: True
                color: 0.13, 0.59, 0.95, 1
                halign: 'left'
                valign: 'middle'
                text_size: self.size
            RoundButton:
                text: '⚙️ 设置'
                size_hint_x: None
                width: dp(90)
                font_size: sp(14)
                on_press: app.go_config()

        # Cookie状态卡片
        BoxLayout:
            size_hint_y: None
            height: dp(48)
            canvas.before:
                Color:
                    rgba: 0.15, 0.15, 0.20, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(8)]
            padding: dp(12), dp(4)
            Label:
                id: cookie_status_label
                text: '🔑 Cookie状态: 检查中...'
                font_size: sp(13)
                color: 0.8, 0.8, 0.8, 1
                halign: 'left'
                valign: 'middle'
                text_size: self.size
            RoundButton:
                text: '管理Cookie'
                size_hint_x: None
                width: dp(110)
                font_size: sp(13)
                on_press: app.go_cookie()

        # 模块选择
        Label:
            text: '选择执行模块'
            font_size: sp(15)
            bold: True
            color: 0.9, 0.9, 0.9, 1
            halign: 'left'
            text_size: self.size
            size_hint_y: None
            height: dp(30)

        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(10)
            RoundButton:
                id: btn_noon
                text: '🌞 午间任务 (13:01)'
                font_size: sp(14)
                on_press: app.run_module('noon')
            RoundButton:
                id: btn_evening
                text: '🌙 晚间任务 (20:01)'
                font_size: sp(14)
                on_press: app.run_module('evening')

        # 定时任务控制
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(10)
            GreenButton:
                id: btn_scheduler
                text: '⏰ 启动定时调度'
                font_size: sp(14)
                on_press: app.toggle_scheduler()
            DangerButton:
                text: '🗑️ 清空日志'
                size_hint_x: None
                width: dp(110)
                font_size: sp(14)
                on_press: app.clear_logs()

        # 实时日志
        Label:
            text: '实时日志'
            font_size: sp(15)
            bold: True
            color: 0.9, 0.9, 0.9, 1
            halign: 'left'
            text_size: self.size
            size_hint_y: None
            height: dp(30)

        BoxLayout:
            canvas.before:
                Color:
                    rgba: 0.05, 0.05, 0.08, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(8)]
            ScrollView:
                id: log_scroll
                do_scroll_x: False
                Label:
                    id: log_label
                    text: '等待任务执行...'
                    font_size: sp(12)
                    color: 0.6, 1.0, 0.6, 1
                    halign: 'left'
                    valign: 'top'
                    size_hint_y: None
                    height: self.texture_size[1]
                    text_size: self.width, None
                    padding: dp(8), dp(8)
                    markup: True

        # 底部按钮
        BoxLayout:
            size_hint_y: None
            height: dp(46)
            spacing: dp(10)
            GreyButton:
                text: '📋 完整日志'
                font_size: sp(14)
                on_press: app.go_log()

<CookieScreen>:
    name: 'cookie'
    canvas.before:
        Color:
            rgba: 0.10, 0.10, 0.13, 1
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(12)

        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(10)
            GreyButton:
                text: '← 返回'
                size_hint_x: None
                width: dp(80)
                font_size: sp(14)
                on_press: app.go_back('main')
            Label:
                text: '🔑 Cookie 管理'
                font_size: sp(18)
                bold: True
                color: 0.13, 0.59, 0.95, 1
                halign: 'left'
                valign: 'middle'
                text_size: self.size

        Label:
            text: '每行填写一个账号的Cookie（格式：openId=..; accessToken=..; newuin=..）'
            font_size: sp(12)
            color: 0.7, 0.7, 0.7, 1
            halign: 'left'
            valign: 'top'
            text_size: self.size
            size_hint_y: None
            height: dp(40)

        BoxLayout:
            canvas.before:
                Color:
                    rgba: 0.15, 0.15, 0.20, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(8)]
            TextInput:
                id: cookie_input
                hint_text: 'openId=xxx; accessToken=xxx; newuin=123456789'
                font_size: sp(13)
                background_color: 0, 0, 0, 0
                foreground_color: 0.9, 0.9, 0.9, 1
                cursor_color: 0.13, 0.59, 0.95, 1
                multiline: True
                padding: dp(12)

        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(10)
            RoundButton:
                text: '💾 保存Cookie'
                font_size: sp(15)
                on_press: app.save_cookies()
            GreenButton:
                text: '✅ 验证Cookie'
                font_size: sp(15)
                on_press: app.verify_cookies()

        Label:
            id: cookie_msg
            text: ''
            font_size: sp(13)
            color: 0.6, 1.0, 0.6, 1
            halign: 'left'
            text_size: self.size
            size_hint_y: None
            height: dp(40)

        Label:
            text: '获取Cookie方法：\\n1. 在手机安装Via浏览器并设为默认浏览器\\n2. 用Via访问大乐斗文字版，一键登录\\n3. 成功后点Via左上角✓图标→查看cookies'
            font_size: sp(12)
            color: 0.6, 0.6, 0.6, 1
            halign: 'left'
            valign: 'top'
            text_size: self.size

<LogScreen>:
    name: 'log'
    canvas.before:
        Color:
            rgba: 0.10, 0.10, 0.13, 1
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(12)

        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(10)
            GreyButton:
                text: '← 返回'
                size_hint_x: None
                width: dp(80)
                font_size: sp(14)
                on_press: app.go_back('main')
            Label:
                text: '📋 完整日志'
                font_size: sp(18)
                bold: True
                color: 0.13, 0.59, 0.95, 1
                halign: 'left'
                valign: 'middle'
                text_size: self.size
            DangerButton:
                text: '清空'
                size_hint_x: None
                width: dp(70)
                font_size: sp(14)
                on_press: app.clear_logs()

        BoxLayout:
            canvas.before:
                Color:
                    rgba: 0.05, 0.05, 0.08, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(8)]
            ScrollView:
                id: full_log_scroll
                do_scroll_x: False
                Label:
                    id: full_log_label
                    text: '暂无日志'
                    font_size: sp(11)
                    color: 0.7, 0.9, 0.7, 1
                    halign: 'left'
                    valign: 'top'
                    size_hint_y: None
                    height: self.texture_size[1]
                    text_size: self.width, None
                    padding: dp(8), dp(8)

<ConfigScreen>:
    name: 'config'
    canvas.before:
        Color:
            rgba: 0.10, 0.10, 0.13, 1
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(12)

        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(10)
            GreyButton:
                text: '← 返回'
                size_hint_x: None
                width: dp(80)
                font_size: sp(14)
                on_press: app.go_back('main')
            Label:
                text: '⚙️ 关于'
                font_size: sp(18)
                bold: True
                color: 0.13, 0.59, 0.95, 1
                halign: 'left'
                valign: 'middle'
                text_size: self.size

        ScrollView:
            Label:
                text: app.about_text
                font_size: sp(13)
                color: 0.8, 0.8, 0.8, 1
                halign: 'left'
                valign: 'top'
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None
                padding: dp(8), dp(8)
"""


class DaLeDouApp(App):
    about_text = (
        "大乐斗 Android 助手 v1.0\n\n"
        "基于开源项目 gaoyuanqi/daledou 改造\n"
        "使用 Kivy + Buildozer 打包\n\n"
        "[功能说明]\n"
        "• 午间任务: 每天13:01自动执行\n"
        "• 晚间任务: 每天20:01自动执行\n"
        "• 支持多账号并发\n"
        "• 支持手动触发任务\n\n"
        "[Cookie说明]\n"
        "获取Cookie请用Via浏览器登录大乐斗文字版\n"
        "地址: https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index&style=1\n\n"
        "[数据存储]\n"
        "配置文件存储在App私有目录\n"
        "config/dld_cookie.yaml - Cookie配置\n"
        "config/default.yaml - 任务默认配置"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._scheduler_running = False
        self._loop = None
        self._thread = None

    def build(self):
        self.title = '大乐斗助手'
        Window.clearcolor = (0.10, 0.10, 0.13, 1)
        root = Builder.load_string(KV)
        return root

    def on_start(self):
        # 启动asyncio event loop在后台线程
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

        # 初始化UI状态
        Clock.schedule_once(self._init_ui, 0.5)
        # 每2秒刷新日志
        Clock.schedule_interval(self._refresh_logs, 2.0)
        # 每10秒刷新Cookie状态
        Clock.schedule_interval(self._refresh_cookie_status, 10.0)

        # 注册日志回调
        LogBuffer.register_callback(lambda msg: None)

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def _run_coro(self, coro):
        """在后台asyncio loop中运行协程"""
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(coro, self._loop)

    def _init_ui(self, dt):
        self._refresh_cookie_status(dt)
        self._load_existing_cookies()

    def _load_existing_cookies(self):
        """加载已存在的cookie到输入框"""
        try:
            path = Config.get_cookie_path()
            if path.exists():
                import yaml
                with open(path, encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                cookies = data.get("DALEDOU_COOKIES") or []
                if cookies:
                    sm = self.root
                    cs = sm.get_screen('cookie')
                    cs.ids.cookie_input.text = "\n".join(c for c in cookies if c)
        except Exception:
            pass

    def _refresh_cookie_status(self, dt):
        try:
            sm = self.root
            main = sm.get_screen('main')
            cookies = Config.load_cookies()
            count = len(cookies)
            if count > 0:
                qq_list = ", ".join(list(cookies.keys())[:3])
                if count > 3:
                    qq_list += f" 等{count}个"
                main.ids.cookie_status_label.text = f"🔑 已配置 {count} 个账号: {qq_list}"
                main.ids.cookie_status_label.color = (0.3, 0.9, 0.3, 1)
            else:
                main.ids.cookie_status_label.text = "⚠️ 未配置Cookie，请先添加"
                main.ids.cookie_status_label.color = (1.0, 0.7, 0.2, 1)
        except Exception as e:
            pass

    def _refresh_logs(self, dt):
        try:
            logs = LogBuffer.get_all()
            if not logs:
                return
            text = "\n".join(logs[-100:])  # 主屏只显示最后100条

            sm = self.root
            main = sm.get_screen('main')
            main.ids.log_label.text = text
            # 自动滚动到底部
            main.ids.log_scroll.scroll_y = 0

            # 如果在日志页面也刷新
            if sm.current == 'log':
                log_screen = sm.get_screen('log')
                log_screen.ids.full_log_label.text = "\n".join(logs)
                log_screen.ids.full_log_scroll.scroll_y = 0
        except Exception:
            pass

    def go_cookie(self):
        self.root.current = 'cookie'
        self._load_existing_cookies()

    def go_config(self):
        self.root.current = 'config'

    def go_log(self):
        self.root.current = 'log'
        # 立即刷新日志
        try:
            logs = LogBuffer.get_all()
            log_screen = self.root.get_screen('log')
            log_screen.ids.full_log_label.text = "\n".join(logs) if logs else "暂无日志"
        except Exception:
            pass

    def go_back(self, screen):
        self.root.current = screen

    def save_cookies(self):
        """保存Cookie"""
        try:
            sm = self.root
            cs = sm.get_screen('cookie')
            raw_text = cs.ids.cookie_input.text.strip()
            if not raw_text:
                cs.ids.cookie_msg.text = "⚠️ Cookie内容不能为空"
                cs.ids.cookie_msg.color = (1, 0.5, 0.2, 1)
                return

            lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
            Config.save_cookies(lines)
            cs.ids.cookie_msg.text = f"✅ 已保存 {len(lines)} 个账号Cookie"
            cs.ids.cookie_msg.color = (0.3, 0.9, 0.3, 1)
            self._refresh_cookie_status(None)
            LogBuffer.add(f"[系统] 已保存 {len(lines)} 个Cookie")
        except Exception as e:
            cs = self.root.get_screen('cookie')
            cs.ids.cookie_msg.text = f"❌ 保存失败: {e}"
            cs.ids.cookie_msg.color = (1, 0.3, 0.3, 1)

    def verify_cookies(self):
        """验证Cookie（解析检查）"""
        try:
            cookies = Config.load_cookies()
            cs = self.root.get_screen('cookie')
            if cookies:
                qq_list = "\n".join(f"  • {qq}" for qq in cookies.keys())
                cs.ids.cookie_msg.text = f"✅ 解析成功，共{len(cookies)}个账号:\n{qq_list}"
                cs.ids.cookie_msg.color = (0.3, 0.9, 0.3, 1)
            else:
                cs.ids.cookie_msg.text = "⚠️ 未能解析到有效Cookie（请检查格式）"
                cs.ids.cookie_msg.color = (1, 0.7, 0.2, 1)
        except Exception as e:
            cs = self.root.get_screen('cookie')
            cs.ids.cookie_msg.text = f"❌ 验证失败: {e}"
            cs.ids.cookie_msg.color = (1, 0.3, 0.3, 1)

    def run_module(self, module_name: str):
        """手动触发任务"""
        from src.tasks.register import TASKS_REGISTRY, TaskModule
        from src.run import TaskRunner, TaskRunError

        cookies = Config.load_cookies()
        if not cookies:
            LogBuffer.add("❌ 请先配置Cookie再执行任务")
            self._refresh_logs(None)
            return

        try:
            module = TaskModule(module_name)
        except ValueError:
            LogBuffer.add(f"❌ 未知模块: {module_name}")
            return

        registry = TASKS_REGISTRY.get(module, {})
        if not registry:
            LogBuffer.add(f"❌ 模块 {module_name} 没有注册任务")
            return

        LogBuffer.add(f"[系统] 开始执行 {module_name} 模块，账号数: {len(cookies)}")

        async def _run():
            try:
                runner = TaskRunner(cookies, module, registry)
                await runner.run()
            except Exception as e:
                LogBuffer.add(f"❌ 执行出错: {e}")

        self._run_coro(_run())

    def toggle_scheduler(self):
        """切换定时调度器"""
        from src.timing import start_scheduler, stop_scheduler

        btn = self.root.get_screen('main').ids.btn_scheduler
        if not self._scheduler_running:
            self._scheduler_running = True
            btn.text = '⏹️ 停止定时调度'
            LogBuffer.add("[系统] 定时调度器已启动")

            async def _start():
                from src.timing import _scheduler_loop
                await _scheduler_loop()

            self._run_coro(_start())
        else:
            self._scheduler_running = False
            btn.text = '⏰ 启动定时调度'
            stop_scheduler()
            LogBuffer.add("[系统] 定时调度器已停止")

    def clear_logs(self):
        LogBuffer.clear()
        try:
            main = self.root.get_screen('main')
            main.ids.log_label.text = '日志已清空'
        except Exception:
            pass


if __name__ == '__main__':
    DaLeDouApp().run()
