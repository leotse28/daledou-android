# 大乐斗助手 (Android 版)

基于 **Android Studio** + **Chaquopy** 实现的移动端大乐斗脚本工具。

## 🌟 核心特性

- **跨语言集成**：利用 Chaquopy (v16.0.0) 在 Android 中无缝运行 Python 3.11 业务逻辑。
- **配置中心**：通过 Gradle 一键同步修改 App 名称和配置文件夹。
- **多架构支持**：全面支持 `arm64-v8a`, `armeabi-v7a`, `x86_64`, `x86`。
- **原生体验**：使用 ViewBinding 和 Material Design 组件构建流畅的 UI。

## 🛠️ 技术栈

- **Android SDK**: API 26+ (Android 8.0+)
- **Build System**: Gradle 8.2.2
- **Python**: v3.11 (via Chaquopy)
- **Dependencies**: `httpx`, `pyyaml` (Python); `AppCompat`, `Material`, `ConstraintLayout` (Android)

## 📁 项目结构

```text
daledou-android/
├── app/
│   ├── build.gradle              ← 统一配置中心 & Chaquopy 配置 (核心)
│   └── src/main/
│       ├── java/com/daledou/
│       │   ├── MainActivity.java     ← 主界面逻辑
│       │   └── ...                   ← 其他 Java 类
│       ├── python/                   ← Python 代码目录
│       │   ├── bridge.py             ← Java <-> Python 桥接层
│       │   └── src/                  ← 原生 Python 业务逻辑
│       └── res/                      ← Android 资源文件 (布局、图标、字符串)
├── build.gradle                  ← 项目级构建配置
└── README.md                     ← 项目说明
```

## ⚙️ 配置与编译

### 1. 修改 App 信息 (可选)
打开 `app/build.gradle`，在 `defaultConfig` 块中找到**统一配置中心**部分：
```gradle
// 修改此处即可同步更新 App 名称和文件夹名
resValue "string", "app_name", "大乐斗助手"
buildConfigField "String", "GLOBAL_APP_NAME", "\"大乐斗助手\""
resValue "string", "config_dir_name", "1A大乐斗配置"
buildConfigField "String", "GLOBAL_CONF_DIR", "\"1A大乐斗配置\""
```
修改后点击 **"Sync Now"**。

### 2. 编译步骤
1. 使用 **Android Studio** (推荐 2023.1.1+) 打开本项目。
2. 等待 Gradle Sync 完成（首次会下载 Chaquopy 和 Python 运行时，约 300MB）。
3. 连接 Android 设备或启动模拟器（API 26+）。
4. 点击工具栏的 **Run (绿色三角形按钮) ▶** 进行安装。

## ⚠️ 注意事项

- **首次运行**：第一次编译需要从远程仓库下载 Python 运行时环境，请确保网络连接良好。
- **ABI 适配**：已默认开启 `armeabi-v7a` 和 `x86` 支持，确保在旧款手机或 32 位模拟器上也能运行。
- **BuildConfig**：项目已开启 `buildConfig` 特性，支持从 Gradle 直接传递常量到 Java 代码。

## 🔗 通信机制

项目采用**异步桥接模式**：
1. **Java** 通过 `Chaquopy` 调用 `bridge.py` 启动任务。
2. **Python** 执行业务逻辑，并通过回调将日志实时推送到 **Java**。
3. **Java** 使用 `Handler` 或 `LiveData` 更新 UI 界面显示日志。

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源。
