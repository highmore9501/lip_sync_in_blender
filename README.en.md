# Hippo's Lip Sync

[![中文](https://img.shields.io/badge/lang-中文-green)](README.md)

A Blender 5.0 addon that imports [Rhubarb Lip Sync](https://github.com/LipSYNCInc/rhubarb-lip-sync) JSON output and drives mesh shape keys to generate lip-sync animation.

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

1. **Rhubarb Lip Sync** ([download](https://github.com/DanielSWolf/rhubarb-lip-sync/releases))  
   Converts speech audio (WAV) into a phoneme timing JSON file. Example usage:

   ```bash
   rhubarb -r phonetic -f json -o output.json input.wav
   ```

2. **Blender 5.0** or later.

3. **A mesh with shape keys** (e.g. VRM, Ready Player Me, MMD models).

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

### Step 1: Generate a lip-sync JSON file

Use Rhubarb to turn an audio file into a phoneme JSON:

```bash
rhubarb -r phonetic -f json -o my_audio.json my_audio.wav
```

The resulting JSON looks like this:

```json
{
  "metadata": { "soundFile": "...", "duration": 30.0 },
  "mouthCues": [
    { "start": 0.0, "end": 2.62, "value": "X" },
    { "start": 2.62, "end": 3.49, "value": "B" }
  ]
}
```

`value` can be `A` through `H` (different mouth shapes) and `X` (silence/closed mouth).

### Step 2: Initialize the mapping table

1. Select your character mesh (must have shape keys).
2. In the 3D View sidebar → **Hippo's Lip Sync** → click **Init Mapping**.
3. The mapping table appears, with one row per phoneme (A~H).

### Step 3: Configure the mapping

Assign a shape key to each phoneme (A~H):

```
A → [pick a shape key]   ← Click the dropdown to choose from the mesh's shape keys
B → [pick a shape key]
C → [pick a shape key]
...
```

> `X` (silence) is automatically skipped — no mapping needed.

### Step 4: Generate the animation

1. Click the folder icon next to **JSON File** and select your Rhubarb JSON file.
2. (Optional) Check **Use VSE Audio Offset** — if you have an audio strip in the Video Sequence Editor, the addon will automatically read its start frame offset.
3. Click **Apply to Timeline** → the addon parses the JSON and writes shape-key keyframes.

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
│  X (silence) is auto-skipped           │
├────────────────────────────────────────┤
│  Generate Lip Sync:                    │
│  [path/to/file.json         ] [📁]    │
│  ☑ Use VSE Audio Offset                │
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

### Q: How do I change the JSON file?

Edit the path directly in the text field, or click the folder icon to browse.

### Q: The animation doesn't look right?

- Try different Rhubarb parameters (e.g. `-r phonetic`).
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
│   └── make_lip_sync_info.py # Batch Rhubarb invocation demo
├── doc/                     # Documentation
│   ├── 施工计划.md
│   ├── Lip_sync_blender插件开发需求.md
│   └── 7月9日.json          # Example Rhubarb output
├── README.md                # Chinese documentation
├── README.en.md             # English documentation
└── .gitignore
```

---

## License

MIT
