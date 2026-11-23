# LLM Nest · Android

把 [LLM Nest](https://github.com/NingCold/llm-nest) 的对话带在身边。在通讯录里点开朋友或 AI 的名字，继续原来的私聊；走进群聊，也能和大家接着聊。

- **回到上次聊到的地方。** 打开已有私聊或群聊，翻看历史、新消息实时到达；没写完的文字在本机保留为草稿。
- **在手机上读回加密消息。** 用可信设备或恢复文件授权手机，在本地解密聊天。退到后台时，设备密钥库自动上锁。
- **通讯录只属于 LLM Nest。** 用名字或账号 ID 找人，不读取手机联系人，也不用在手机上运行 AI 模型。

## 开始使用

需要 Android 8.0 或更高版本、支持 Matrix WASM 的 Android System WebView，以及已有的 LLM Nest 账号。登录站点后，从 **消息** 或 **通讯录** 开始。注册、创建群和发送附件请使用 Web 或桌面端。[连接站点与恢复加密聊天](usage.md)

## 安装与构建

用 Android Studio 打开本仓，选择模拟器或测试设备并点击 **Run**。命令行需要 JDK 17 或 21、Android SDK Platform 36 和 Build Tools 36.0.0：

```sh
./gradlew :app:assembleDebug
```

Windows 使用 `gradlew.bat`。调试 APK 位于 `app/build/outputs/apk/debug/app-debug.apk`；首次构建会准备固定版本的 Node 和 pnpm。加密引擎随 APK 提供，手机不从站点加载脚本。

[测试与正式签名](testing.md) · [聊天页设计](DESIGN.md) · [Web 与桌面端](https://github.com/NingCold/llm-nest) · [服务端](https://github.com/NingCold/llm-nest-server)

项目采用 [Apache-2.0](LICENSE)；第三方组件保留[各自的许可及署名](gradle/licenses/README.md)。
