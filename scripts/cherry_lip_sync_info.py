# 使用 Cherry Lip Sync 将语音转化为嘴唇时间轴
# 模仿 make_lip_sync_info.py (Rhubarb) 的写法

import time
import subprocess
import os

"""
使用本地的 Cherry Lip Sync 工具批量生成嘴唇时间轴。
"""

cherry_exe = r'H:\Cherry-Lip-Sync\cherrylipsync.exe'
wave_dir = 'g:/fretdance介绍视频音源/视频二'
fps = 60

start = time.time()

# 遍历所有wav文件
for root, dirs, files in os.walk(wave_dir):
    for file in files:
        if file.endswith('.wav'):
            wav_file = os.path.join(root, file)
            output = os.path.join(root, f'{file[:-4]}.TSV')
            subprocess.run([
                cherry_exe,
                '-i', wav_file,
                '-o', output,
                '-f', str(fps)
            ], shell=True)

finish = time.time()

print(f'Finished in {finish - start} seconds')
