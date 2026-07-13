# Hippo's Lip Sync

[![中文](https://img.shields.io/badge/lang-中文-green)](README.md)

A Blender 5.0 addon that imports lip sync files and drives mesh shape keys to generate lip-sync animation.

Supports two lip sync tools:

- [Rhubarb Lip Sync](https://github.com/DanielSWolf/rhubarb-lip-sync) — JSON format (8 phonemes: A~H + X)
- [Cherry Lip Sync](https://github.com/amberwhitehead/cherry-lip-sync) — TSV format (12 phonemes: A~K + X)

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [UI Overview](#ui-overview)
- [Transition Algorithm](#transition-algorithm)
- [FAQ](#faq)
- [Project Structure](#project-structure)

---

## Prerequisites

This addon supports either of the following lip sync tools:

### Option A: Rhubarb Lip Sync (8 phonemes)

[Download](https://github.com/DanielSWolf/rhubarb-lip-sync/releases)  
Converts speech audio (WAV) into a phoneme timing JSON file:

```bash
rhubarb -r phonetic -f json -o output.json input.wav
```

Phoneme set: `A, B, C, D, E, F, G, H, X`

### Option B: Cherry Lip Sync (12 phonemes)

[Download](https://github.com/amberwhitehead/cherry-lip-sync/releases)  
Converts audio (WAV/MP3/OGG/FLAC) into a TSV format lip sync file:

```bash
cherrylipsync -i input.wav -o output.tsv -f 30
```

Phoneme set: `A, B, C, D, E, F, G, H, I, J, K, X`

| New phoneme | Sound   | Description                             |
| :---------- | ------- | :-------------------------------------- |
| **I**       | EE      | Wide mouth showing teeth                |
| **J**       | CH/J/SH | Shape for "CH", "J", "SH"               |
| **K**       | R       | Rounded mouth with teeth closed for "R" |

> If your character doesn't have dedicated shape keys for I/J/K, you can map them to similar shapes: **I→B**, **J→B**, **K→E**.

### Common requirements

- **Blender 5.0** or later.
- **A mesh with shape keys** (e.g. VRM, Ready Player Me, MMD models).

---

## Installation

### Method 1: ZIP drag-and-drop (recommended)

1. Zip the entire `lip_sync_addon/` folder into a `.zip` file.
2. Drag the ZIP file directly onto the Blender viewport — it will be installed automatically.
3. Press `N` in the 3D Viewport to open the sidebar — the **"Hippo's Lip Sync"** tab will appear.

### Method 2: Manual copy

1. Copy the `lip_sync_addon/` folder to Blender's `scripts/addons/` directory:
   - Windows: `%APPDATA%\Blender Foundation\Blender\5.0\scripts\addons\`
   - macOS: `~/Library/Application Support/Blender/5.0/scripts/addons/`
   - Linux: `~/.config/blender/5.0/scripts/addons/`

2. Open Blender → **Edit** → **Preferences** → **Add-ons**.

3. Search for **"Hippo's Lip Sync"** and enable it.

4. Press `N` in the 3D Viewport to open the sidebar — the **"Hippo's Lip Sync"** tab will be there.

---

## Quick Start

### Step 1: Generate a lip-sync file

#### Method 1: Rhubarb JSON

```bash
rhubarb -r phonetic -f json -o my_audio.json my_audio.wav
```

The resulting JSON:

```json
{
  "metadata": { "soundFile": "...", "duration": 30.0 },
  "mouthCues": [
    { "start": 0.0, "end": 2.62, "value": "X" },
    { "start": 2.62, "end": 3.49, "value": "B" }
  ]
}
```

`value` ranges from `A` to `H` plus `X` (silence).

#### Method 2: Cherry Lip Sync TSV

```bash
cherrylipsync -i my_audio.wav -o my_audio.tsv -f 30
```

The resulting TSV format (tab-separated):

```text
0.000	X
0.133	C
0.200	G
0.300	I
0.500	C
0.633	X
```

`value` ranges from `A` to `K` plus `X` (silence).

### Step 2: Initialize the mapping table

1. Select your character mesh (must have shape keys).
2. In the 3D View sidebar → **Hippo's Lip Sync** → click **Init Mapping**.
3. The mapping table appears, with one row per phoneme (A~K).

### Step 3: Configure the mapping

Assign a shape key to each phoneme (A~K):

```
A → [pick a shape key]   ← Click the dropdown to choose from the mesh's shape keys
B → [pick a shape key]
C → [pick a shape key]
...
```

> `X` (silence) is automatically skipped — no mapping needed.

### Step 4: Generate the animation

1. Click the folder icon next to the file path and select your `.json` (Rhubarb) or `.tsv` (Cherry Lip Sync) file.
2. (Optional) Check **Use VSE Audio Offset** — if you have an audio strip in the Video Sequence Editor, the addon will automatically read its start frame offset.
3. Click **Apply to Timeline** → the addon auto-detects the file format (JSON or TSV) and writes shape-key keyframes.

### Step 5: Preview

- Scrub the timeline or play the animation to see the result.
- To redo, click **Clear Animation** to remove all shape-key keyframes.

---

## UI Overview

```
┌────────────────────────────────────────┐
│  Hippo's Lip Sync                      │
├────────────────────────────────────────┤
│  Target: Wolf3D_Avatar     ← mesh name │
│  [Init Mapping]  [Clear]   ← mgmt btns │
├────────────────────────────────────────┤
│  Phoneme Mapping:                      │
│    A  [shape_key ▼ dropdown]           │
│    B  [shape_key ▼ dropdown]           │
│    C  [shape_key ▼ dropdown]           │
│    D  [shape_key ▼ dropdown]           │
│    E  [shape_key ▼ dropdown]           │
│    F  [shape_key ▼ dropdown]           │
│    G  [shape_key ▼ dropdown]           │
│    H  [shape_key ▼ dropdown]           │
│    I  [shape_key ▼ dropdown]           │  ← Cherry (wide EE)
│    J  [shape_key ▼ dropdown]           │  ← Cherry (CH/J/SH)
│    K  [shape_key ▼ dropdown]           │  ← Cherry (R sound)
│  X (silence) is auto-skipped           │
├────────────────────────────────────────┤
│  Generate Lip Sync:                    │
│  [path/to/file.json/.tsv      ] [📁]   │
│  [▶ Apply to Timeline]  [🗑 Clear]     │
└────────────────────────────────────────┘
```

---

## Transition Algorithm

For each **non-X** mouth cue, the addon inserts 4 keyframes to create a smooth ease-in/out curve:

```
 1.0 ──────────────
     /               \
0.0 ─                 ────
    ↑        ↑        ↑        ↑
    t1       t2       t3       t4
   fade-in  start    end     fade-out
   (0.0)    (1.0)    (1.0)    (0.0)
```

- **t1** = `start - change_duration` where `change_duration = min((end - start) / 3, 0.5 s)`.
- **t2** = `start`
- **t3** = `end`
- **t4** = `end + next_change_duration` (the next non-X cue's change_duration).

`X` cues are completely skipped — no keyframes are generated for them.

---

## FAQ

### Q: The panel doesn't show up?

Make sure:

- You have a **Mesh** object selected.
- The sidebar is visible (press `N` in the 3D Viewport).
- The addon is enabled in **Preferences** → **Add-ons**.

### Q: "Apply to Timeline" does nothing?

Check:

- Did you click **Init Mapping** first?
- Does each phoneme have a shape key assigned?
- Is the JSON file path valid?

### Q: How do I change the lip sync file?

Edit the path directly in the text field, or click the folder icon to browse. Both `.json` (Rhubarb) and `.tsv` (Cherry Lip Sync) are supported.

### Q: My character doesn't have I/J/K shape keys?

Map the new phonemes to similar existing shapes: **I→B** (wide mouth), **J→B** (teeth together), **K→E** (rounded lips). Missing mappings are automatically skipped.

### Q: The animation doesn't look right?

- Rhubarb: Try different parameters (e.g. `-r phonetic`).
- Cherry Lip Sync: Try the `--filter` flag to remove single-frame jitter.
- Double-check your phoneme-to-shape-key mapping.

---

## Project Structure

```
lip_sync_in_blender/
├── lip_sync_addon/          # Addon source code
│   ├── __init__.py          # Entry point — bl_info + registration
│   ├── properties.py        # Mapping storage + scene properties
│   ├── lip_sync_core.py     # Core logic — JSON parsing, keyframe writing
│   ├── operators.py         # Operators — button actions
│   └── panels.py            # UI panel — 3D View sidebar
├── scripts/                 # Reference scripts
│   ├── lip_sync.py          # Manual lip-sync application demo
│   ├── make_lip_sync_info.py # Batch Rhubarb invocation demo
│   └── cherry_lip_sync_info.py # Batch Cherry Lip Sync invocation demo
├── doc/                     # Documentation
│   ├── 施工计划.md
│   ├── Lip_sync_blender插件开发需求.md
│   ├── 7月9日.json          # Example Rhubarb output
│   └── 米良三油屋四月 - 爱的代价钢琴弹唱版Cover 李宗盛_vocals.TSV  # Example Cherry Lip Sync output
├── README.md                # Chinese documentation
├── README.en.md             # English documentation
└── .gitignore
```

---

## License

MIT
