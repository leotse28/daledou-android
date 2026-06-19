#!/usr/bin/env python3
"""
Android Kivy APP Entry Point
Q宠大乐斗自动化助手 - Android版
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window

from screens.home import HomeScreen
from screens.accounts import AccountManagerScreen
from screens.task_runner import TaskRunnerScreen
from screens.logs import LogsScreen

from utils.storage import StorageManager
from utils.config_handler import ConfigHandler

# 设置窗口大小
Window.size = (540, 1080)  # 仿QQ手机界面


class DaLeDouApp(App):
    """主应用类"""

    title = "Q宠大乐斗助手"

    def build(self):
        # 初始化存储和配置
        self.storage = StorageManager()
        self.config_handler = ConfigHandler(self.storage)

        # 初始化屏幕管理器
        self.screen_manager = ScreenManager()

        # 添加所有屏幕
        self.screen_manager.add_widget(HomeScreen(name="home", app=self))
        self.screen_manager.add_widget(
            AccountManagerScreen(name="accounts", app=self)
        )
        self.screen_manager.add_widget(
            TaskRunnerScreen(name="task_runner", app=self)
        )
        self.screen_manager.add_widget(LogsScreen(name="logs", app=self))

        return self.screen_manager

    def on_pause(self):
        """应用暂停时处理"""
        return True

    def on_resume(self):
        """应用恢复时处理"""
        pass


if __name__ == "__main__":
    app = DaLeDouApp()
    app.run()
