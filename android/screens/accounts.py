"""
账号管理屏幕
"""

from kivy.uix.screen import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.core.metrics import dp


class AccountManagerScreen(Screen):
    """账号管理页面"""

    def __init__(self, app=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.accounts = {}  # 加载的账号列表
        self.build_ui()

    def build_ui(self):
        """构建UI"""
        main_layout = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))

        # 顶部标题栏
        header_layout = BoxLayout(size_hint_y=0.08, spacing=dp(10))
        with header_layout.canvas.before:
            Color(0.0, 0.47, 0.8, 1.0)  # QQ蓝
            Rectangle(size=header_layout.size, pos=header_layout.pos)

        back_btn = Button(
            text="← 返回",
            size_hint_x=0.2,
            background_color=(0.0, 0.35, 0.6, 1),
            font_size="14sp",
        )
        back_btn.bind(on_press=self.on_back)
        header_layout.add_widget(back_btn)

        title_label = Label(
            text="账号管理",
            font_size="18sp",
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_x=0.6,
        )
        header_layout.add_widget(title_label)

        add_btn = Button(
            text="+ 添加",
            size_hint_x=0.2,
            background_color=(0.2, 0.8, 0.3, 1),
            font_size="14sp",
        )
        add_btn.bind(on_press=self.on_add_account)
        header_layout.add_widget(add_btn)

        main_layout.add_widget(header_layout)

        # 账号列表
        scroll = ScrollView(size_hint=(1, 0.92))
        self.accounts_layout = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.accounts_layout.bind(minimum_height=self.accounts_layout.setter("height"))
        scroll.add_widget(self.accounts_layout)
        main_layout.add_widget(scroll)

        self.add_widget(main_layout)
        self._refresh_accounts_list()

    def _refresh_accounts_list(self):
        """刷新账号列表显示"""
        self.accounts_layout.clear_widgets()
        accounts = self.app.config_handler.get_accounts()

        if not accounts:
            empty_label = Label(
                text="暂无账号配置\n点击+添加按钮添加账号",
                size_hint_y=None,
                height=dp(100),
                font_size="14sp",
                color=(0.7, 0.7, 0.7, 1),
            )
            self.accounts_layout.add_widget(empty_label)
        else:
            for qq, cookie_dict in accounts.items():
                account_card = self._create_account_card(qq, cookie_dict)
                self.accounts_layout.add_widget(account_card)

    def _create_account_card(self, qq, cookie_dict):
        """创建账号卡片"""
        card = BoxLayout(
            orientation="vertical", size_hint_y=None, height=dp(80), spacing=dp(5)
        )
        with card.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            Rectangle(size=card.size, pos=card.pos)

        qq_label = Label(
            text=f"QQ: {qq}",
            size_hint_y=0.4,
            font_size="14sp",
            halign="left",
        )
        card.add_widget(qq_label)

        cookie_preview = str(cookie_dict)[:30] if cookie_dict else "无Cookie"
        cookie_label = Label(
            text=f"Cookie: {cookie_preview}...",
            size_hint_y=0.3,
            font_size="11sp",
            halign="left",
            color=(0.6, 0.6, 0.6, 1),
        )
        card.add_widget(cookie_label)

        btn_layout = BoxLayout(size_hint_y=0.3, spacing=dp(5))
        edit_btn = Button(
            text="编辑", size_hint_x=0.5, background_color=(0.0, 0.47, 0.8, 1)
        )
        delete_btn = Button(
            text="删除", size_hint_x=0.5, background_color=(0.8, 0.2, 0.2, 1)
        )
        edit_btn.bind(on_press=lambda x: self.on_edit_account(qq))
        delete_btn.bind(on_press=lambda x: self.on_delete_account(qq))
        btn_layout.add_widget(edit_btn)
        btn_layout.add_widget(delete_btn)
        card.add_widget(btn_layout)

        return card

    def on_back(self, instance):
        """返回主页"""
        self.manager.current = "home"

    def on_add_account(self, instance):
        """添加新账号"""
        self._show_account_dialog()

    def on_edit_account(self, qq):
        """编辑账号"""
        self._show_account_dialog(qq)

    def on_delete_account(self, qq):
        """删除账号"""
        if self.app.config_handler.remove_account(qq):
            self._refresh_accounts_list()

    def _show_account_dialog(self, qq=None):
        """显示账号编辑对话框"""
        popup_content = BoxLayout(
            orientation="vertical", spacing=dp(10), padding=dp(15)
        )

        qq_input = TextInput(
            hint_text="请输入QQ号",
            multiline=False,
            size_hint_y=0.2,
            input_filter="int",
            text=qq or "",
        )
        popup_content.add_widget(Label(text="QQ号:", size_hint_y=0.1))
        popup_content.add_widget(qq_input)

        cookie_input = TextInput(
            hint_text="请粘贴大乐斗Cookie",
            multiline=True,
            size_hint_y=0.5,
        )
        popup_content.add_widget(Label(text="Cookie:", size_hint_y=0.1))
        popup_content.add_widget(cookie_input)

        btn_layout = BoxLayout(size_hint_y=0.1, spacing=dp(10))
        save_btn = Button(text="保存", background_color=(0.2, 0.8, 0.3, 1))
        cancel_btn = Button(text="取消", background_color=(0.8, 0.8, 0.8, 1))
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        popup_content.add_widget(btn_layout)

        popup = Popup(
            title="添加账号" if not qq else f"编辑账号 {qq}",
            content=popup_content,
            size_hint=(0.95, 0.9),
        )
        save_btn.bind(
            on_press=lambda x: self._save_account(
                qq_input.text, cookie_input.text, popup
            )
        )
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def _save_account(self, qq, cookie, popup):
        """保存账号"""
        if not qq or not cookie:
            pass
        else:
            if self.app.config_handler.add_account(qq, cookie):
                self._refresh_accounts_list()
                popup.dismiss()
