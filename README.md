# Hippo's Lip Sync

[![English](https://img.shields.io/badge/lang-English-blue)](README.en.md)

一个 Blender 5.0 插件，导入 [Rhubarb Lip Sync](https://github.com/DanielSWolf/rhubarb-lip-sync) 生成的 JSON 口型文件，驱动角色网格的 Shape Key 生成嘴唇动画。

---

## 目录

- [前置准备](#前置准备)
- [安装](#安装)
- [快速入门](#快速入门)
- [界面说明](#界面说明)
- [过渡动画算法](#过渡动画算法)
- [常见问题](#常见问题)
- [项目结构](#项目结构)

---

## 前置准备

1. **Rhubarb Lip Sync**（[官网下载](https://github.com/DanielSWolf/rhubarb-lip-sync/releases)）  
   用于将语音 WAV 文件转化为口型 JSON 文件。命令行使用示例：

   ```bash
   rhubarb.exe -r phonetic -f json -o output.json input.wav
   ```

2. **Blender 5.0** 或更高版本。

3. **一个带 Shape Key 的网格模型**（如 VRM、Ready Player Me、MMD 等）。

---

## 安装

### 方法一：ZIP 拖拽安装（推荐）

1. 将 `lip_sync_addon/` 整个文件夹打包为 ZIP 文件（选中文件夹 → 右键 → 压缩为 ZIP）。
2. 将 ZIP 文件直接拖拽到 Blender 视图窗口上，即可自动完成安装。
3. 在 3D 视图侧边栏（按 `N` 键）可看到 **"Hippo's Lip Sync"** 标签页。

### 方法二：手动复制

1. 将 `lip_sync_addon/` 文件夹复制到 Blender 的 `scripts/addons/` 目录下：
   - Windows: `%APPDATA%\Blender Foundation\Blender\5.0\scripts\addons\`
   - macOS: `~/Library/Application Support/Blender/5.0/scripts/addons/`
   - Linux: `~/.config/blender/5.0/scripts/addons/`

2. 打开 Blender → **Edit** → **Preferences** → **Add-ons**。

3. 搜索 **"Hippo's Lip Sync"**，勾选启用。

4. 在 3D 视图侧边栏（按 `N` 键）可看到 **"Hippo's Lip Sync"** 标签页。

---

## 快速入门

### 第一步：准备口型 JSON 文件

用 Rhubarb 将语音文件转为口型 JSON：

```bash
rhubarb -r phonetic -f json -o my_audio.json my_audio.wav
```

生成的 JSON 格式如下：

```json
{
  "metadata": { "soundFile": "...", "duration": 30.0 },
  "mouthCues": [
    { "start": 0.0, "end": 2.62, "value": "X" },
    { "start": 2.62, "end": 3.49, "value": "B" }
  ]
}
```

其中 `value` 取值 `A~H`（不同口型）和 `X`（闭嘴/静音）。

### 第二步：初始化映射表

1. 在 Blender 中选中你的角色网格（必须含有 Shape Key）。
2. 在 3D 视图侧边栏 → **Hippo's Lip Sync** → 点击 **Init Mapping**。
3. 映射表会出现在面板中，每行对应一个口型（A~H）。

### 第三步：配置映射关系

为每个口型（A~H）选择对应的 Shape Key：

```
A → [选择 Shape Key]   ← 点击右侧下拉框，从网格已有的 Shape Key 中选择
B → [选择 Shape Key]
C → [选择 Shape Key]
...
```

> `X`（闭嘴/静音）会自动跳过，无需映射。

### 第四步：生成口型动画

1. 点击 **JSON File** 右侧的文件夹图标，选择 Rhubarb 生成的 JSON 文件。
2. （可选）勾选 **Use VSE Audio Offset**：如果你在 Video Sequence Editor 中放置了音频轨道，插件会自动检测音频起始帧偏移。
3. 点击 **Apply to Timeline** → 插件解析 JSON 并自动写入 Shape Key 关键帧。

### 第五步：预览效果

- 播放时间轴，查看口型动画效果。
- 如需重做，点击 **Clear Animation** 清除所有 Shape Key 关键帧。

---

## 界面说明

```
┌────────────────────────────────────────┐
│  Hippo's Lip Sync                      │
├────────────────────────────────────────┤
│  Target: Wolf3D_Avatar     ← 目标网格  │
│  [Init Mapping]  [Clear]   ← 映射管理  │
├────────────────────────────────────────┤
│  Phoneme Mapping:                      │
│    A  [shape_key ▼ 下拉选择]           │
│    B  [shape_key ▼ 下拉选择]           │
│    C  [shape_key ▼ 下拉选择]           │
│    D  [shape_key ▼ 下拉选择]           │
│    E  [shape_key ▼ 下拉选择]           │
│    F  [shape_key ▼ 下拉选择]           │
│    G  [shape_key ▼ 下拉选择]           │
│    H  [shape_key ▼ 下拉选择]           │
│  X (silence) is auto-skipped           │
├────────────────────────────────────────┤
│  Generate Lip Sync:                    │
│  [选择 JSON 文件路径...] [📁]         │
│  [▶ Apply to Timeline]  [🗑 Clear]     │
└────────────────────────────────────────┘
```

---

## 常见问题

### Q: 面板不显示？

确保：

- 已选中一个 **Mesh 类型** 的物体
- 在 3D 视图按 `N` 键打开了侧边栏
- 插件已在 Preferences 中启用

### Q: 点击 "Apply to Timeline" 没有反应？

检查：

- 是否已 **Init Mapping**？
- 映射表中每个口型是否已选择对应的 Shape Key？
- JSON 文件路径是否有效？

### Q: 如何更换 JSON 文件？

直接在 JSON 文件路径输入框中修改路径，或点击文件夹图标重新选择。

### Q: 动画效果不理想？

- 调整 Rhubarb 的参数重新生成 JSON（如 `-r phonetic` 切换识别方法）
- 检查映射表是否正确

---

## 项目结构

```
lip_sync_in_blender/
├── lip_sync_addon/          # 插件代码
│   ├── __init__.py          # 插件入口 ── bl_info + 注册
│   ├── properties.py        # 映射表存储 + 场景属性
│   ├── lip_sync_core.py     # 核心算法 ── JSON 解析、关键帧写入
│   ├── operators.py         # 操作符 ── 按钮动作
│   └── panels.py            # UI 面板 ── 3D 视图侧边栏
├── scripts/                 # 参考脚本
│   ├── lip_sync.py          # 手动应用口型动画的示范
│   └── make_lip_sync_info.py # 批量调用 Rhubarb 生成 JSON 的示范
├── doc/                     # 文档
│   ├── 施工计划.md
│   ├── Lip_sync_blender插件开发需求.md
│   └── 7月9日.json          # Rhubarb 输出示例
└── README.md
```

---

## License

MIT
