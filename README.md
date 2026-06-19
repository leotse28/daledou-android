# 无为乐斗 Android 助手 - Android Studio 版

## 技术栈
- **Android Studio** + Java
- **Chaquopy** v15.0.1 - 在Android内嵌Python 3.11
- Python 业务逻辑完全保留原版

## 项目结构

```
daledou_as/
├── app/
│   ├── build.gradle              ← Chaquopy插件配置（核心）
│   └── src/main/
│       ├── AndroidManifest.xml
│       ├── java/com/daledou/
│       │   ├── MainActivity.java     ← 主界面
│       │   ├── CookieActivity.java   ← Cookie管理界面
│       │   ├── LogActivity.java      ← 完整日志界面
│       │   └── DaLeDouBridge.java    ← Java日志缓冲区
│       ├── python/                   ← Python代码目录（Chaquopy自动识别）
│       │   ├── bridge.py             ← Java<->Python桥接（最关键）
│       │   ├── src/
│       │   │   ├── run.py
│       │   │   ├── timing.py
│       │   │   ├── tasks/ (register/common/noon/evening)
│       │   │   └── utils/ (client/config/daledou/log/date_time)
│       │   └── config/default.yaml
│       └── res/layout/ values/ drawable/
├── build.gradle
└── settings.gradle
```

## 编译步骤

1. 用 Android Studio（推荐 Hedgehog 2023.1.1+）打开本目录
2. 等待 Gradle Sync 完成（首次会下载 Chaquopy + Python 3.11，约 300MB）
3. 连接手机或启动模拟器（API 24+，推荐 API 33）
4. 点击 **Run ▶** 即可安装到设备

## 注意事项

- 首次Sync时间较长（需下载Python运行时）
- 需要网络访问 mavenCentral 下载 Chaquopy
- 支持架构：arm64-v8a、armeabi-v7a (32位真机)、x86_64、x86 (模拟器)
- Python依赖：httpx、pyyaml（已在build.gradle中声明，自动安装）

## Java <-> Python 通信机制

```
Java (MainActivity)
    ↓ 调用
bridge.py (Python)
    ↓ 导入
src/tasks/noon.py, evening.py ...
    ↓ 日志回调
DaLeDouBridge.java (日志缓冲)
    ↓ UI读取
MainActivity → TextView显示
```
