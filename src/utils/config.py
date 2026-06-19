"""
配置加载模块 - Android适配版
"""
import os
from http.cookies import SimpleCookie
from pathlib import Path
from typing import Optional, Any, Final

import yaml

from src.tasks.register import TaskModule


def get_config_dir() -> Path:
    """获取配置目录：Android用app存储目录，PC用./config"""
    try:
        from android.storage import app_storage_path  # type: ignore
        base = Path(app_storage_path())
    except ImportError:
        base = Path(".")
    return base / "config"


class ConfigError(Exception):
    pass

class ConfigFileNotFoundError(ConfigError):
    pass

class ConfigKeyError(ConfigError):
    pass

class ConfigYAMLError(ConfigError):
    pass


class ConfigResolver:
    NOT_FOUND: Final = object()

    def __init__(self, qq: str, module: TaskModule):
        self._qq = qq
        self._module = module
        self._full_account: dict = Config.load_account(qq)
        self._full_default: dict = Config.load_default()

        if (
            self._module not in self._full_account
            and self._module not in self._full_default
        ):
            raise ConfigKeyError(
                f"配置键 {self._module} 不存在"
            )

        self._account = self._full_account.get(self._module)
        self._default = self._full_default.get(self._module)

    def get(self, key: str) -> Any:
        keys = key.split(".")

        if isinstance(self._account, dict):
            account_value = self._deep_get(self._account, keys)
            if account_value is not self.NOT_FOUND:
                return account_value

        if isinstance(self._default, dict):
            default_value = self._deep_get(self._default, keys)
            if default_value is not self.NOT_FOUND:
                return default_value

        raise ConfigKeyError(f"配置键 '{self._module}.{key}' 未找到")

    def _deep_get(self, data: dict, keys: list) -> Any:
        current = data
        for k in keys:
            if not isinstance(current, dict) or k not in current:
                return self.NOT_FOUND
            current = current[k]
        return current


class Config:
    @classmethod
    def _config_dir(cls) -> Path:
        return get_config_dir()

    @classmethod
    def _accounts_dir(cls) -> Path:
        return cls._config_dir() / "accounts"

    @classmethod
    def _default_config_path(cls) -> Path:
        return cls._config_dir() / "default.yaml"

    @classmethod
    def _cookie_config_path(cls) -> Path:
        return cls._config_dir() / "dld_cookie.yaml"

    # Keep DLD_COOKIE_CONFIG_PATH as a class property for compatibility
    DLD_COOKIE_CONFIG_PATH = property(lambda self: self._cookie_config_path())

    @classmethod
    def _parse_cookie(cls, cookie: str) -> dict:
        jar = SimpleCookie()
        jar.load(cookie)
        return {k: v.value for k, v in jar.items()}

    @classmethod
    def _load_yaml_file(cls, file_path: Path) -> dict:
        if not file_path.exists():
            raise ConfigFileNotFoundError(f"{file_path} 不存在")
        try:
            with file_path.open("r", encoding="utf-8") as fp:
                return yaml.safe_load(fp) or {}
        except yaml.YAMLError as e:
            raise ConfigYAMLError(f"{file_path} 解析错误: {e}")

    @classmethod
    def load_account(cls, qq: str) -> dict:
        file_path = cls._accounts_dir() / f"{qq}.yaml"
        if not file_path.exists():
            if not cls._default_config_path().exists():
                return {}
            cls._accounts_dir().mkdir(parents=True, exist_ok=True)
            yaml_data = {task.value: None for task in TaskModule}
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(yaml_data, f, sort_keys=False, allow_unicode=True)
        return cls._load_yaml_file(file_path)

    @classmethod
    def load_default(cls) -> dict:
        path = cls._default_config_path()
        if not path.exists():
            return {}
        return cls._load_yaml_file(path)

    @classmethod
    def get_cookie_path(cls) -> Path:
        return cls._cookie_config_path()

    @classmethod
    def load_cookies(cls, qq: Optional[str] = None) -> dict:
        result = {}
        cookie_path = cls._cookie_config_path()
        if not cookie_path.exists():
            return result
        try:
            cookie_dict = cls._load_yaml_file(cookie_path)
        except Exception:
            return result
        cookies_list = cookie_dict.get("DALEDOU_COOKIES") or []
        if not cookies_list:
            return result

        for cookie_str in cookies_list:
            if not cookie_str:
                continue
            parsed = cls._parse_cookie(cookie_str)
            if newuin := parsed.get("newuin"):
                if qq is not None and qq == newuin:
                    return {qq: parsed}
                result[newuin] = parsed

        return {} if qq is not None else result

    @classmethod
    def save_cookies(cls, cookies_list: list) -> None:
        """保存cookie列表到文件"""
        cookie_path = cls._cookie_config_path()
        cookie_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"DALEDOU_COOKIES": cookies_list}
        with open(cookie_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True)

    @classmethod
    def init_default_config(cls) -> None:
        """首次运行时初始化default.yaml到存储目录"""
        dest = cls._default_config_path()
        if dest.exists():
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        # 内置的default.yaml内容（精简版）
        default_content = """
noon:
  华山论剑:
    战阵调整:
      - count: 8
        knights: [林朝英, 王处一, 王重阳]
    exchange:
      6857:
        material_name: 钻石
        quantity: 100
  好友:
    贡献药水:
      count: 4
  侠侣:
    情师徒拜:
      enabled: true
  群侠:
    设置战队: [林朝英, 王处一, 王重阳, 木岛主, 龙岛主]
  巅峰之战进行中:
    id: 2
  矿洞:
    floor: 1
    mode: 1
  竞技场:
    河图洛书:
      enabled: true
  十二宫:
    id: 1011
  历练:
    6114: 3
    6134: 2
  幻境:
    id: 8
  帮派商会:
    交易会所: []
    兑换商店: []
  侠士客栈:
    黑市商人: []
  深渊之潮:
    深渊秘境:
      count: 3
      id: 1
  龙凰之境:
    龙凰论武:
      count: 5
  客栈同福:
    献酒: []
  大笨钟:
    enabled: true
evening:
  华山论剑:
    战阵调整:
      - count: 8
        knights: [林朝英, 王处一, 王重阳]
    exchange:
      6857:
        material_name: 钻石
        quantity: 100
  好友:
    贡献药水:
      count: 4
  侠侣:
    情师徒拜:
      enabled: true
  群侠:
    设置战队: [林朝英, 王处一, 王重阳, 木岛主, 龙岛主]
  巅峰之战进行中:
    id: 2
  矿洞:
    floor: 1
    mode: 1
  竞技场:
    河图洛书:
      enabled: true
  十二宫:
    id: 1011
  历练:
    6114: 3
    6134: 2
  幻境:
    id: 8
  帮派商会:
    交易会所: []
    兑换商店: []
  侠士客栈:
    黑市商人: []
  深渊之潮:
    深渊秘境:
      count: 3
      id: 1
  龙凰之境:
    龙凰论武:
      count: 5
  客栈同福:
    献酒: []
  大笨钟:
    enabled: true
  登录商店:
    id: null
  爱的同心结:
    QQ: null
"""
        with open(dest, "w", encoding="utf-8") as f:
            f.write(default_content)
