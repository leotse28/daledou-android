"""
无为乐斗 - Python Bridge
对接 Android Java 层的所有调用，支持自定义外部存储路径
"""
import os
import asyncio
import threading
import json
import yaml
from src.utils.config import Config

# ========== 全局变量 ==========
_base_dir = None
_stop_event = threading.Event()

# ========== 任务定义（完整列表，确保 UI 显示所有功能） ==========
NOON_TASKS = [
    "邪神秘宝", "华山论剑", "分享", "好友", "帮友", "侠侣", "武林", "群侠", "结拜",
    "巅峰之战进行中", "矿洞", "掠夺", "踢馆", "竞技场", "十二宫", "许愿", "抢地盘",
    "历练", "镖行天下", "幻境", "群雄逐鹿", "画卷迷踪", "门派", "门派邀请赛",
    "会武", "梦想之旅", "问鼎天下", "帮派商会", "帮派远征军", "帮派黄金联赛",
    "任务派遣中心", "武林盟主", "全民乱斗", "侠士客栈", "江湖长梦", "大侠回归",
    "飞升大作战", "深渊之潮", "侠客岛", "时空遗迹", "世界树", "龙凰之境", "任务",
    "我的帮派", "帮派祭坛", "每日奖励", "领取徒弟经验", "今日活跃度", "仙武修真",
    "乐斗黄历", "器魂附魔", "兵法", "万圣节", "乐斗能量", "大笨钟", "幸运金蛋",
    "客栈同福", "节日福利", "双旦福利", "金秋福利", "春节福利", "多倍福利", "新春拜年"
]

EVENING_TASKS = [
    "邪神秘宝", "星盘", "帮派商会", "任务派遣中心", "侠士客栈", "江湖长梦", "深渊之潮",
    "侠客岛", "龙凰之境", "背包", "镶嵌", "神匠坊", "每日宝箱", "猜单双", "煮元宵",
    "元宵节", "刮刮卡", "娃娃机", "吉利兑", "激运牌", "回忆录", "愚人节", "儿童节",
    "开学季", "大笨钟", "幸运金蛋", "客栈同福", "节日福利", "双旦福利", "金秋福利",
    "春节福利", "多倍福利", "新春拜年", "神魔转盘", "乐斗驿站", "幸运转盘", "冰雪企缘",
    "甜蜜夫妻", "乐斗菜单", "周周礼包", "登录有礼", "活跃礼包", "清明上香", "徽章战令",
    "生肖福卡", "长安盛会", "深渊秘宝", "中秋礼盒", "双节签到", "斗境探秘", "春联大赛",
    "预热礼包", "豪侠出世", "乐斗游记", "喜从天降", "兑换码", "浩劫宝箱", "端午有礼",
    "圣诞有礼", "新春礼包", "登录商店", "周年巡礼", "五一礼包", "五一预订", "好礼提升",
    "周年祝福", "周年预热", "年兽大作战", "新春登录礼", "爱的同心结", "重阳太白诗会"
]

# ========== 初始化 ==========

def init_app(external_path):
    """由 Java 层调用，初始化外部存储路径"""
    global _base_dir
    _base_dir = external_path
    Config.set_base_dir(external_path)
    Config.init_default_config()

def _get_path(filename):
    if filename == "cookie": return str(Config.get_cookie_path())
    if filename == "default": return str(Config._default_config_path())
    if filename == "register": return str(Config._config_dir() / "task_register.json")
    return None

# ========== Cookie 管理 ==========

def load_cookies():
    path = _get_path("cookie")
    if not os.path.exists(path): return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("DALEDOU_COOKIES") or []
    except: return []

def save_cookies(cookies_text):
    path = _get_path("cookie")
    yaml.safe_load(cookies_text)
    with open(path, "w", encoding="utf-8") as f:
        f.write(cookies_text)
    return "ok"

def get_cookie_yaml():
    path = _get_path("cookie")
    if not os.path.exists(path):
        return "# 大乐斗Cookie，每行一个账号\nDALEDOU_COOKIES:\n# - openId=..; accessToken=..; newuin=..\n"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def get_qq_list():
    cookies = load_cookies()
    qq_list = []
    for ck in cookies:
        for part in ck.split(";"):
            part = part.strip()
            if part.startswith("newuin="):
                qq_list.append(part[7:].strip())
                break
    return ",".join(qq_list)

def get_account_summary():
    qq_str = get_qq_list()
    if not qq_str: return "未配置账号"
    qq_list = [q for q in qq_str.split(",") if q]
    return f"共 {len(qq_list)} 个账号: {', '.join(qq_list)}"

# ========== 默认配置管理 ==========

def load_default_config():
    path = _get_path("default")
    if not os.path.exists(path): return "# default.yaml 不存在"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def save_default_config(content):
    yaml.safe_load(content)
    with open(_get_path("default"), "w", encoding="utf-8") as f:
        f.write(content)
    return "ok"

def reset_default_config():
    from src.utils.config import DEFAULT_CONFIG_CONTENT
    with open(_get_path("default"), "w", encoding="utf-8") as f:
        f.write(DEFAULT_CONFIG_CONTENT.strip())
    return "ok"

# ========== 账号配置管理 ==========

def load_account_config(qq):
    path = Config._accounts_dir() / f"{qq}.yaml"
    if not path.exists():
        return f"# 账号 {qq} 暂无独立配置\n# 当前使用默认配置 default.yaml\n# 粘贴/修改后点击保存即可生效\n"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def save_account_config(qq, content):
    yaml.safe_load(content)
    path = Config._accounts_dir() / f"{qq}.yaml"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return "ok"

# ========== 任务注册管理 ==========

def _load_task_register():
    path = _get_path("register")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "noon": {t: True for t in NOON_TASKS},
        "evening": {t: True for t in EVENING_TASKS},
    }

def get_task_list(module):
    register = _load_task_register()
    tasks = NOON_TASKS if module == "noon" else EVENING_TASKS
    module_reg = register.get(module, {})
    parts = []
    for task in tasks:
        enabled = module_reg.get(task, True)
        parts.append(f"{task}:{'1' if enabled else '0'}")
    return ",".join(parts)

def save_task_register(module, data):
    register = _load_task_register()
    module_reg = {}
    for item in data.split(","):
        if not item.strip(): continue
        parts = item.rsplit(":", 1)
        if len(parts) == 2:
            module_reg[parts[0]] = (parts[1] == "1")
    register[module] = module_reg
    with open(_get_path("register"), "w", encoding="utf-8") as f:
        json.dump(register, f, ensure_ascii=False, indent=2)
    return "ok"

def get_enabled_tasks(module):
    register = _load_task_register()
    tasks = NOON_TASKS if module == "noon" else EVENING_TASKS
    module_reg = register.get(module, {})
    return [t for t in tasks if module_reg.get(t, True)]

def save_single_cookie(cookie_str):
    """保存单条或多条 Cookie 并更新列表"""
    import re
    # 匹配 newuin=123456
    qq_matches = re.findall(r"newuin=(\d+)", cookie_str)
    if not qq_matches:
        raise Exception("Cookie 格式错误，未找到 newuin=... 部分")

    # 我们将输入按行分割处理，如果是 YAML 格式，去除前面的 " - "
    lines = cookie_str.splitlines()
    new_cookies_added = []
    for line in lines:
        line = line.strip()
        if not line or "DALEDOU_COOKIES" in line: continue
        # 去除 YAML 符号
        clean_line = line.lstrip("- ").strip()
        if "newuin=" in clean_line:
            new_cookies_added.append(clean_line)

    if not new_cookies_added:
        raise Exception("未解析到有效的 Cookie 条目")

    # 读取旧的
    old_cookies = load_cookies()
    cookie_dict = {}

    # 先放入旧的
    for ck in old_cookies:
        m = re.search(r"newuin=(\d+)", ck)
        if m: cookie_dict[m.group(1)] = ck

    # 放入新的 (覆盖同 QQ 的)
    last_qq = ""
    for ck in new_cookies_added:
        m = re.search(r"newuin=(\d+)", ck)
        if m:
            last_qq = m.group(1)
            cookie_dict[last_qq] = ck

    # 重新序列化
    final_list = list(cookie_dict.values())
    save_cookies(yaml.dump({"DALEDOU_COOKIES": final_list}, allow_unicode=True, sort_keys=False))

    return last_qq

def delete_cookie(qq):
    """根据 QQ 号删除指定的 Cookie"""
    import re
    old_cookies = load_cookies()
    new_list = []
    for ck in old_cookies:
        if f"newuin={qq}" not in ck:
            new_list.append(ck)

    save_cookies(yaml.dump({"DALEDOU_COOKIES": new_list}, allow_unicode=True, sort_keys=False))
    return "ok"

# ========== 任务执行 ==========

def run_module(module, target_qq=None):
    _stop_event.clear()

    import src.utils.log as log_mod
    log_mod._java_log = lambda line: _write_log(line, "system")

    from src.tasks.register import TASKS_REGISTRY, TaskModule
    if module == "noon":
        import src.tasks.noon
        task_module = TaskModule.noon
    else:
        import src.tasks.evening
        task_module = TaskModule.evening

    full_registry = TASKS_REGISTRY.get(task_module, {})
    enabled = get_enabled_tasks(module)
    filtered_registry = {k: v for k, v in full_registry.items() if k in enabled}

    if target_qq:
        cookies = Config.load_cookies(target_qq)
    else:
        cookies = Config.load_cookies()

    if not cookies:
        _write_log("未配置 Cookie，无法执行任务", "system")
        return "no cookies"

    from src.run import TaskRunner
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        runner = TaskRunner(
            cookies=cookies,
            module=task_module,
            registry=filtered_registry,
            max_concurrency=3,
            log_callback=lambda msg, qq="system": _write_log(msg, qq)
        )
        loop.run_until_complete(runner.run())
        loop.close()
    except Exception as e:
        import traceback
        _write_log(f"未知错误: {traceback.format_exc()}", "system")
        return str(e)

    return "done"

def stop_task():
    _stop_event.set()
    return "stopped"

# ========== 日志 ==========

def _write_log(content, qq="system"):
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_path = Config.get_log_path(qq)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {content}\n")

def read_log(qq="system"):
    log_path = Config.get_log_path(qq)
    if not os.path.exists(log_path): return "暂无日志"
    with open(log_path, "r", encoding="utf-8") as f:
        content = f.read()
    return content[-10000:] if len(content) > 10000 else content

def clear_log(qq="system"):
    log_path = Config.get_log_path(qq)
    if os.path.exists(log_path): os.remove(log_path)
    return "ok"

# ========== 连通性测试 ==========

def test_account(qq):
    from src.utils.config import Config
    cookies = Config.load_cookies(qq)
    if not cookies or qq not in cookies:
        return json.dumps({"qq": qq, "status": "fail", "msg": "未找到 Cookie"}, ensure_ascii=False)

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_async_test_account(qq, cookies[qq]))
        loop.close()
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"qq": qq, "status": "error", "msg": str(e)}, ensure_ascii=False)

async def _async_test_account(qq, cookie_dict):
    import re
    from src.utils.client import Client
    try:
        async with Client(qq, cookie_dict) as client:
            html = await client.get("cmd=grdsimple")
            if "请先登录" in html or len(html) < 100:
                return {"qq": qq, "status": "fail", "msg": "Cookie 已失效"}

            # 更加宽松的正则匹配，处理 HTML 标签和多余空格
            def quick_find(pattern, default="-"):
                m = re.search(pattern, html, re.S)
                if m:
                    # 去除匹配结果中的 HTML 标签
                    res = re.sub(r"<[^>]+>", "", m.group(1)).strip()
                    return res if res else default
                return default

            name = quick_find(r"昵称[:：]\s*(.*?)[<|\n|\s]")
            level = quick_find(r"等级[:：]\s*(\d+)")
            hp = quick_find(r"体力[:：]\s*(\d+/\d+)")
            power = quick_find(r"战力[:：]\s*(\d+)")

            return {
                "qq": qq,
                "status": "ok",
                "name": name,
                "level": level,
                "hp": hp,
                "power": power,
                "msg": "连接正常"
            }
    except Exception as e:
        return {"qq": qq, "status": "error", "msg": str(e)}

def test_all_accounts():
    qq_str = get_qq_list()
    if not qq_str: return "[]"
    results = [json.loads(test_account(q.strip())) for q in qq_str.split(",") if q.strip()]
    return json.dumps(results, ensure_ascii=False)
