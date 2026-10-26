# Codex 与 OpenCode 外观、主题、字体完整配置手册（含原生与改后对照）

## 一、字体配置（Google Fonts：`Noto Serif SC` 思源宋体）

- **字体名称**：`Noto Serif SC`（Variable Font，`NotoSerifSC-VariableFont_wght.ttf`）
- **本机安装路径**：`~/Library/Fonts/NotoSerifSC-VariableFont_wght.ttf`
- **字号**：`14px`
- **换新机安装命令**：
  ```bash
  brew install --cask font-noto-serif-sc
  # 或直接将 NotoSerifSC-VariableFont_wght.ttf 放入 ~/Library/Fonts/
  ```

---

## 二、Codex 外观与主题配置（`~/.codex/config.toml`）

Codex 桌面端的外观配置位于 `~/.codex/config.toml` 的 `[desktop]` 节：

```toml
[desktop]
conversationDetailMode = "STEPS_COMMANDS"
ambient-suggestions-enabled = true
followUpQueueMode = "queue"
dock-icon-preference = "codex-system"
show-ultra-in-model-picker-slider = false
enabled-reasoning-efforts = ["low", "medium", "high", "xhigh", "ultra", "max"]
appearanceTheme = "system"
usePointerCursors = false
appearanceLightCodeThemeId = "absolutely"
show-context-window-usage = true
preventSleepWhileRunning = true
sansFontSize = 14
default-workspace-full-view = true
localeOverride = "zh-CN"

[desktop.appearanceLightChromeTheme]
accent = "#cc7d5e"
accentSource = "custom"
contrast = 45
ink = "#2d2d2b"
opaqueWindows = false
surface = "#f9f9f7"

[desktop.appearanceLightChromeTheme.fonts]
ui = "Noto Serif SC"

[desktop.appearanceLightChromeTheme.semanticColors]
diffAdded = "#00c853"
diffRemoved = "#ff5f38"
skill = "#cc7d5e"
```

### Codex 内置 `Absolutely` 代码高亮色板（取自 `ChatGPT.app`）

| 语义项 | 浅色模式（`Absolutely Light`） | 深色模式（`Absolutely Dark`） |
|---|---|---|
| 主背景（`surface` / `bg`） | `#f9f9f7`（侧栏 `#f4f4f2`） | `#2d2d2b`（侧栏 `#373735`） |
| 主文字（`ink` / `fg`） | `#2d2d2b` | `#f9f9f7` |
| 强调色（`accent` / `primary`） | `#cc7d5e`（陶土橙） | `#cc7d5e`（陶土橙） |
| 注释（`comment`） | `#939391` | `#b2b2b0` |
| 字符串 / 新增（`string` / `diffAdded`） | `#00c853` | `#00c853` |
| 关键字 / 数字 / 删除（`keyword` / `diffRemoved`） | `#ff5f38` | `#ff5f38` |
| 类型 / 函数 / 属性（`type` / `function`） | `#bc7559` | `#d28e73` |

---

## 三、OpenCode 原生配置 vs 修改后配置对照

| 维度 | OpenCode 原生配置（`oc-2`） | OpenCode 修改后配置（`Absolutely`） |
|---|---|---|
| **默认主题 ID** | `oc-2`（显示名 `OpenCode`） | `absolutely`（显示名 `Absolutely`） |
| **全局 UI 字体** | `Inter`（`settings.v3 -> appearance.sans: ""`） | `Noto Serif SC`（`settings.v3 -> appearance.sans: "Noto Serif SC"`，14px） |
| **代码等宽字体** | `IBM Plex Mono` | `IBM Plex Mono`（保持不变） |
| **浅色主背景 / 文字** | `#fafafa` / `#161616` | `#f9f9f7`（深层 `#f4f4f2`） / `#2d2d2b` |
| **深色主背景 / 文字** | `#080808` / `#fafafa` | `#2d2d2b`（深层 `#252523`） / `#f9f9f7` |
| **强调色（`--v2-background-bg-accent`）** | `#3b5cf6`（高饱和亮蓝） | `#cc7d5e`（Codex 陶土橙） |
| **用户会话气泡（工作区会话 `[data-workspace-session]`）** | 亮蓝底 `#3b5cf6` + 白字 `#fafafa` | 陶土橙底 `#cc7d5e` + 白字 `#ffffff` |
| **用户会话气泡（本地会话 `[data-local-session]`）** | 浅色：`#f5f8ff` 浅蓝底 + `#0b34f4` 蓝字<br>深色：`#021945` 深蓝底 + `#c3d4fd` 浅蓝字 | 浅色：`#f6ebe6` 暖浅陶土底 + `#9e5336` 深陶土字<br>深色：`#422b22` 深褐底 + `#f2cab9` 浅陶土字 |
| **发送按钮（无字禁用态 `:disabled`）** | `#242424` + `opacity: 0.4`（折合浅灰 `#a8a8a8`） | `--v2-grey-900` + `opacity: 0.4`（安静中性浅灰） |
| **发送按钮（有字可发送态）** | 浅色：深炭黑 `#242424` + 白箭头<br>深色：亮灰白 `#dbdbdb` + 黑箭头 | 浅色/深色统一：**陶土橙 `#cc7d5e` + 纯白箭头 `#ffffff`** |
| **TUI 配置文件（`~/.config/opencode/tui.json`）** | 未指定 `theme` | `"theme": "absolutely"`（读取 `~/.config/opencode/themes/absolutely.json`） |

---

## 四、仓库文件清单与换机一键安装 / 还原

所有配置文件、源码补丁与一键安装脚本均归档在本仓库下：

1. **原生主题与外观备份**：`themes/oc-2-backup.json`（可保存在本机 `~/.config/opencode/themes/oc-2-backup.json`）
2. **改后 TUI 主题**：`themes/absolutely.json`（本机路径 `~/.config/opencode/themes/absolutely.json`）
3. **改后 TUI 配置**：`tui.json`（本机路径 `~/.config/opencode/tui.json`）
4. **改后桌面端主题定义**：`themes/absolutely-desktop.json`（对应源码 `packages/ui/src/theme/themes/absolutely.json`）
5. **换机 / 升级后一键安装脚本（直接注入二进制 `app.asar`）**：`install-opencode-appearance.py`
6. **OpenCode 源码级主题与默认字体补丁**：`patches/opencode-source-theme.patch`

### 换新机或 OpenCode 桌面端版本升级后怎么用

1. 确保新机已安装 `Noto Serif SC` 字体（见第一节）。
2. 在本仓库运行一键安装脚本：
   ```bash
   python3 install-opencode-appearance.py
   ```
3. 重启 OpenCode 桌面端（`Cmd + Q` 后重新打开），即可完整复原 `Absolutely` 主题、陶土橙气泡、陶土橙发送按钮与 `Noto Serif SC` 字体。

> **注意**：当前处于高频优化 OpenCode 源码与插件阶段，该主题仅作为独立归档保存，日常开发、优化、打包 OpenCode 时无需再维护或注入此主题。

### 如何切回原生 `oc-2` 主题

- **桌面端**：打开 OpenCode「设置（Settings） -> 外观（Appearance） -> 主题（Theme）」，在下拉框中选择 `OpenCode`（即原生 `oc-2`），并将「UI 字体」清空即可恢复默认 `Inter`。
- **命令行 TUI**：将 `~/.config/opencode/tui.json` 中的 `"theme": "absolutely"` 删掉或改为 `"theme": "opencode"`。
