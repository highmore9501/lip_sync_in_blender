# Hippo's Lip Sync

[![English](https://img.shields.io/badge/lang-English-blue)](README.en.md)

一个 Blender 5.0 插件，导入口型文件并驱动角色网格的 Shape Key 生成嘴唇动画。

支持两种口型生成工具：

- [Rhubarb Lip Sync](https://github.com/DanielSWolf/rhubarb-lip-sync) — 生成 JSON 格式（8 口型：A~H + X）
- [Cherry Lip Sync](https://github.com/amberwhitehead/cherry-lip-sync) — 生成 TSV 格式（12 口型：A~K + X）

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

本插件支持以下两种口型生成工具（任选其一即可）：

### 方案 A：Rhubarb Lip Sync（8 口型）

[官网下载](https://github.com/DanielSWolf/rhubarb-lip-sync/releases)  
将语音 WAV 文件转化为 JSON 格式的口型文件：

```bash
rhubarb.exe -r phonetic -f json -o output.json input.wav
```

口型符号：`A, B, C, D, E, F, G, H, X`

### 方案 B：Cherry Lip Sync（12 口型）

[GitHub 下载](https://github.com/amberwhitehead/cherry-lip-sync/releases)  
将语音文件（WAV/MP3/OGG/FLAC）转化为 TSV 格式的口型文件：

```bash
cherrylipsync.exe -i input.wav -o output.tsv -f 30
```

口型符号：`A, B, C, D, E, F, G, H, I, J, K, X`

| 新增口型 | 发音    | 说明                     |
| :------- | :------ | :----------------------- |
| **I**    | EE      | 咧嘴，类似"一"音         |
| **J**    | CH/J/SH | 噘嘴齿音，类似"吃/知/湿" |
| **K**    | R       | 圆唇闭齿 R 音            |

> 如果角色的 Shape Key 没有 I/J/K 对应的口型，可以从邻近口型复制：I→B, J→B, K→E。

### 共同要求

- **Blender 5.0** 或更高版本。
- **一个带 Shape Key 的网格模型**（如 VRM、Ready Player Me、MMD 等）。

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

### 第一步：准备口型文件

#### 方式 1：Rhubarb JSON

```bash
rhubarb -r phonetic -f json -o my_audio.json my_audio.wav
```

生成的 JSON 格式：

```json
{
  "metadata": { "soundFile": "...", "duration": 30.0 },
  "mouthCues": [
    { "start": 0.0, "end": 2.62, "value": "X" },
    { "start": 2.62, "end": 3.49, "value": "B" }
  ]
}
```

`value` 取值 `A~H`（不同口型）和 `X`（闭嘴/静音）。

#### 方式 2：Cherry Lip Sync TSV

```bash
cherrylipsync -i my_audio.wav -o my_audio.tsv -f 30
```

生成的 TSV 格式（制表符分隔）：

```text
0.000	X
0.133	C
0.200	G
0.300	I
0.500	C
0.633	X
```

`value` 取值 `A~K`（不同口型）和 `X`（闭嘴/静音）。

### 第二步：初始化映射表

1. 在 Blender 中选中你的角色网格（必须含有 Shape Key）。
2. 在 3D 视图侧边栏 → **Hippo's Lip Sync** → 点击 **Init Mapping**。
3. 映射表会出现在面板中，每行对应一个口型（A~K）。

### 第三步：配置映射关系

为每个口型（A~K）选择对应的 Shape Key：

```
A  → [选择 Shape Key]   ← 点击右侧下拉框，从网格已有的 Shape Key 中选择
B  → [选择 Shape Key]
C  → [选择 Shape Key]
...  （共 A~K 十一个口型）
```

> `X`（闭嘴/静音）会自动跳过，无需映射。

### 第四步：生成口型动画

1. 点击文件路径右侧的文件夹图标，选择 Rhubarb 生成的 `.json` 文件或 Cherry Lip Sync 生成的 `.tsv` 文件。
2. （可选）勾选 **Use VSE Audio Offset**：如果你在 Video Sequence Editor 中放置了音频轨道，插件会自动检测音频起始帧偏移。
3. 点击 **Apply to Timeline** → 插件自动识别文件格式（JSON 或 TSV）并写入 Shape Key 关键帧。

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
│    I  [shape_key ▼ 下拉选择]           │  ← Cherry 新增（EE 咧嘴）
│    J  [shape_key ▼ 下拉选择]           │  ← Cherry 新增（CH/J/SH）
│    K  [shape_key ▼ 下拉选择]           │  ← Cherry 新增（R 音）
│  X (silence) is auto-skipped           │
├────────────────────────────────────────┤
│  Generate Lip Sync:                    │
│  [选择 JSON/TSV 文件路径...]   [📁]   │
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

### Q: 如何更换口型文件？

直接在文件路径输入框中修改路径，或点击文件夹图标重新选择。支持 `.json`（Rhubarb）和 `.tsv`（Cherry Lip Sync）格式。

### Q: 我的角色没有 I/J/K 对应的 Shape Key 怎么办？

可以在映射表中将 I/J/K 映射到邻近口型：**I→B**（咧嘴）、**J→B**（齿音）、**K→E**（圆唇）。缺失映射时插件会自动跳过，不影响其他口型。

### Q: 动画效果不理想？

- Rhubarb：调整参数重新生成（如 `-r phonetic` 切换识别方法）
- Cherry Lip Sync：尝试 `--filter` 参数过滤单帧抖动
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
│   ├── make_lip_sync_info.py # 批量调用 Rhubarb 生成 JSON 的示范
│   └── cherry_lip_sync_info.py # 批量调用 Cherry Lip Sync 生成 TSV 的示范
├── doc/                     # 文档
│   ├── 施工计划.md
│   ├── Lip_sync_blender插件开发需求.md
│   ├── 7月9日.json          # Rhubarb 输出示例
│   └── 米良三油屋四月 - 爱的代价钢琴弹唱版Cover 李宗盛_vocals.TSV  # Cherry Lip Sync 输出示例
└── README.md
```

---

## License

MIT
