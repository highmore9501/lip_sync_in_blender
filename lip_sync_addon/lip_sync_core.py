import json
import os
import bpy


# ── Utility functions ──────────────────────────────────────────────────────


def parse_lip_sync_json(json_path):
    """Parse a Rhubarb lip sync JSON file and return the mouthCues list.

    Each cue has the shape: {"start": float, "end": float, "value": str}.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('mouthCues', [])


def parse_lip_sync_tsv(tsv_path):
    """Parse a Cherry Lip Sync TSV file and return the mouthCues list.

    TSV format: timestamp (seconds) \\t phoneme (A-K or X) per line.
    Each cue has the shape: {"start": float, "end": float, "value": str}.
    """
    entries = []
    with open(tsv_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) >= 2:
                try:
                    start = float(parts[0])
                    value = parts[1].strip()
                    entries.append({'start': start, 'value': value})
                except ValueError:
                    continue

    # Convert to mouthCues with end time = next entry's start time
    mouth_cues = []
    for i, entry in enumerate(entries):
        if i + 1 < len(entries):
            end = entries[i + 1]['start']
        else:
            end = entry['start'] + 0.1  # fallback duration for last cue
        mouth_cues.append({
            'start': entry['start'],
            'end': end,
            'value': entry['value'],
        })
    return mouth_cues


def parse_lip_sync_file(file_path):
    """Auto-detect file format (.json or .tsv) and parse accordingly.

    Returns the mouthCues list.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.tsv':
        return parse_lip_sync_tsv(file_path)
    else:
        return parse_lip_sync_json(file_path)


def get_scene_fps(scene):
    """Return the effective FPS from the scene settings."""
    return scene.render.fps / scene.render.fps_base


def _calc_change_duration(start, end):
    """Compute change_duration = (end - start) / 3, capped at 0.5 s."""
    duration = (end - start) / 3.0
    return min(duration, 0.5)


# ── Core apply function ────────────────────────────────────────────────────


def apply_lip_sync_to_mesh(mesh_obj, mouth_cues, mapping, audio_offset=0):
    """Apply mouth-cue data to a mesh's shape keys by inserting keyframes.

    Args:
        mesh_obj:      The Blender mesh object (must have shape keys).
        mouth_cues:    List of dicts [{start, end, value}, ...].
        mapping:       Dict {phoneme: shape_key_name} (A-H → shape key).
        audio_offset:  Optional global frame offset (default 0).
    """
    if not mesh_obj.data.shape_keys:
        return

    scene = bpy.context.scene
    fps = get_scene_fps(scene)
    key_blocks = mesh_obj.data.shape_keys.key_blocks

    # ── Step 1: clear existing animation and reset all shape keys to 0 ─
    clear_shape_key_animation(mesh_obj)
    for kb in key_blocks:
        kb.value = 0.0

    # ── Step 2: pre-compute change_duration for ALL cues (incl. X) ────
    for cue in mouth_cues:
        cue['_change_duration'] = _calc_change_duration(
            cue['start'], cue['end'])

    # ── Step 3: filter out X cues ──────────────────────────────────────
    non_x_cues = [c for c in mouth_cues if c.get('value') != 'X']
    if not non_x_cues:
        return

    # ── Step 4: temporarily disable auto-keyframe ──────────────────────
    use_auto_key = scene.tool_settings.use_keyframe_insert_auto
    scene.tool_settings.use_keyframe_insert_auto = False

    # ── Step 5: iterate cues and insert keyframes ──────────────────────
    for i, cue in enumerate(non_x_cues):
        phoneme = cue['value']
        shape_key_name = mapping.get(phoneme, '')
        if not shape_key_name or shape_key_name not in key_blocks:
            continue

        start = cue['start']
        end = cue['end']
        change_dur = cue['_change_duration']

        # Find the actual preceding cue in the original mouth_cues list
        idx_in_full = next(j for j, c in enumerate(mouth_cues) if c is cue)
        if idx_in_full > 0:
            pre_change_dur = mouth_cues[idx_in_full - 1]['_change_duration']
        else:
            pre_change_dur = change_dur  # first cue, fall back to current

        keyblock = key_blocks[shape_key_name]

        # Frame 1 — fade-in start (value = 0.0)
        t1 = max(0.0, start - pre_change_dur)
        f1 = int(t1 * fps) + audio_offset
        keyblock.value = 0.0
        keyblock.keyframe_insert(data_path='value', frame=f1)

        # Frame 2 — fade-in complete / hold start (value = 1.0)
        f2 = int(start * fps) + audio_offset
        keyblock.value = 1.0
        keyblock.keyframe_insert(data_path='value', frame=f2)

        # Frame 3 — hold end / fade-out start (value = 1.0)
        t3 = end - change_dur
        f3 = int(t3 * fps) + audio_offset
        keyblock.value = 1.0
        keyblock.keyframe_insert(data_path='value', frame=f3)

        # Frame 4 — fade-out complete (value = 0.0)
        f4 = int(end * fps) + audio_offset
        keyblock.value = 0.0
        keyblock.keyframe_insert(data_path='value', frame=f4)

    # ── Step 6: restore auto-keyframe setting ──────────────────────────
    scene.tool_settings.use_keyframe_insert_auto = use_auto_key


# ── Helper functions ───────────────────────────────────────────────────────


def clear_shape_key_animation(mesh_obj):
    """Remove all animation data from the shape keys.

    In Blender 5.0, Action uses a layered system (Action.layers →
    ActionLayer → ActionKeyframeStrip → fcurves), so the old
    action.fcurves access no longer works. Instead we disconnect the
    action entirely — Blender will create a fresh one on next write.
    """
    if not mesh_obj.data.shape_keys:
        return
    sk = mesh_obj.data.shape_keys
    if sk.animation_data:
        sk.animation_data.action = None
