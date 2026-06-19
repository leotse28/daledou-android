"""
主页屏幕 - 功能导航
"""

from kivy.uix.screen import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.metrics import dp


class HomeScreen(Screen):
    """主页 - 显示功能入口和任务概览"""

    def __init__(self, app=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.build_ui()

    def build_ui(self):
        """构建UI"""
        main_layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))

        # 顶部标题栏（仿QQ风格）
        title_layout = BoxLayout(size_hint_y=0.08)
        with title_layout.canvas.before:
            Color(0.0, 0.47, 0.8, 1.0)  # QQ蓝
            Rectangle(size=title_layout.size, pos=title_layout.pos)

        title_label = Label(
            text="Q宠大乐斗助手",
            font_size="20sp",
            bold=True,
            color=(1, 1, 1, 1),
        )
        title_layout.add_widget(title_label)
        main_layout.add_widget(title_layout)

        # 账号状态卡片
        status_card = self._create_card("account_status")
        main_layout.add_widget(status_card)

        # 功能按钮网格
        button_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=0.6)

        buttons = [
            ("📋 账号管理", "accounts", self.on_btn_accounts),
            ("🎮 执行任务", "task_runner", self.on_btn_run_tasks),
            ("📊 运行日志", "logs", self.on_btn_logs),
            ("⚙️ 关于", "settings", self.on_btn_settings),
        ]

        for text, screen_name, callback in buttons:
            btn = Button(
                text=text,
                size_hint=(0.5, 1),
                font_size="16sp",
                background_normal="",
                background_color=(0.9, 0.9, 0.9, 1),
            )
            with btn.canvas.before:
                Color(0.2, 0.6, 1.0, 1.0)  # QQ蓝
                RoundedRectangle(size=btn.size, pos=btn.pos, radius=[dp(8)])

            btn.bind(on_press=callback)
            button_layout.add_widget(btn)

        main_layout.add_widget(button_layout)

        # 底部信息
        footer_layout = BoxLayout(size_hint_y=0.15, padding=dp(10))
        footer_label = Label(
            text="v1.0.0\n已加载 2 个模块 (noon, evening)\n状态：就绪",
            font_size="12sp",
            color=(0.5, 0.5, 0.5, 1),
        )
        footer_layout.add_widget(footer_label)
        main_layout.add_widget(footer_layout)

        self.add_widget(main_layout)

    def _create_card(self, card_type):
        """创建卡片"""
        card = BoxLayout(orientation="vertical", size_hint_y=0.15, padding=dp(10))
        with card.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            Rectangle(size=card.size, pos=card.pos)

        if card_type == "account_status":
            account_count = len(self.app.config_handler.get_accounts())
            label1 = Label(
                text="已配置账号",
                font_size="14sp",
                size_hint_y=0.4,
                halign="left",
            )
            label2 = Label(
                text=f"共 {account_count} 个账号",
                font_size="18sp",
                bold=True,
                size_hint_y=0.6,
                halign="left",
                color=(0.0, 0.47, 0.8, 1.0),
            )
            card.add_widget(label1)
            card.add_widget(label2)

        return card

    def on_btn_accounts(self, instance):
        """切换到账号管理页面"""
        self.manager.current = "accounts"

    def on_btn_run_tasks(self, instance):
        """切换到任务执行页面"""
        self.manager.current = "task_runner"

    def on_btn_logs(self, instance):
        """切换到日志页面"""
        self.manager.current = "logs"

    def on_btn_settings(self, instance):
        """打开设置弹窗"""
        popup_content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        popup_content.add_widget(
            Label(text="关于本应用", font_size="16sp", size_hint_y=0.2)
        )
        popup_content.add_widget(
            Label(
                text="版本: 1.0.0\n作者: daledou-android贡献者\n大乐斗自动化助手Android版本",
                font_size="12sp",
            )
        )
        close_btn = Button(text="关闭", size_hint_y=0.2)
        popup_content.add_widget(close_btn)

        popup = Popup(
            title="关于", content=popup_content, size_hint=(0.9, 0.6)
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
