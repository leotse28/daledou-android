# 大乐斗 Android 助手

基于 [gaoyuanqi/daledou](https://github.com/gaoyuanqi/daledou) 改造的 Kivy Android 版本

## 项目结构

```
daledou_android/
├── main.py              ← Kivy UI 主程序（入口）
├── buildozer.spec       ← Buildozer 打包配置
├── requirements.txt     ← 依赖列表
├── config/
│   └── default.yaml     ← 默认任务配置
└── src/
    ├── run.py           ← 任务执行器（已适配Android）
    ├── timing.py        ← 定时调度（asyncio版，无schedule依赖）
    ├── tasks/
    │   ├── register.py  ← 任务注册系统
    │   ├── common.py    ← 公共任务函数
    │   ├── noon.py      ← 午间任务
    │   └── evening.py   ← 晚间任务
    └── utils/
        ├── client.py    ← HTTP客户端
        ├── config.py    ← 配置管理（已适配Android存储路径）
        ├── daledou.py   ← 核心工具类
        ├── date_time.py ← 日期时间工具
        └── log.py       ← 日志模块（已替换为内存缓冲）
```

## 主要改动说明

| 文件 | 原版 | Android适配 |
|------|------|-------------|
| `src/utils/log.py` | loguru + 文件sink | 内存LogBuffer + 回调通知UI |
| `src/utils/config.py` | `./config/` 路径 | Android存储目录动态适配 |
| `src/run.py` | `sys.exit()` 退出 | 抛出异常，交由UI处理 |
| `src/timing.py` | schedule库 | asyncio纯异步定时循环 |
| `main.py` | CLI入口 | Kivy UI 完整界面 |

## 打包成 APK

### 方法一：使用 Buildozer（推荐，Linux/WSL环境）

```bash
# 安装buildozer
pip install buildozer

# 安装系统依赖（Ubuntu/Debian）
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# 打包（首次需要下载Android SDK/NDK，约1.5GB，耗时较长）
cd daledou_android
buildozer android debug

# APK输出位置
# bin/daledou-1.0.0-arm64-v8a-debug.apk
```

### 方法二：使用 Google Colab（无需本地Linux环境）

在 Google Colab 中运行以下代码：

```python
# 安装依赖
!pip install buildozer cython

# 上传项目zip，解压后执行
!cd daledou_android && buildozer android debug
```

### 方法三：GitHub Actions 自动打包

将项目推送到GitHub，添加 `.github/workflows/build.yml` 即可自动打包。

## PC端测试运行

```bash
pip install kivy httpx pyyaml
python main.py
```

## Cookie 配置

1. 手机安装 **Via浏览器** 并设为默认浏览器
2. 用Via访问大乐斗文字版：`https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index&style=1`
3. 一键登录后等5秒
4. 点击Via左上角 ✓ 图标 → 查看cookies → 复制全部内容
5. 粘贴到App的Cookie管理页面，每个账号一行
