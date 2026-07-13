# 下面是如何跑rhubarb将语音转化成为嘴型时间轴

import asyncio
import time
import subprocess
import os

"""
使用本地的Rhubarb Lip Sync工具指批量生成嘴唇时间轴。
"""

start = time.time()
wave_dir = 'g:/fretdance介绍视频音源/视频二'
# 遍历所有wav文件
for root, dirs, files in os.walk(wave_dir):
    for file in files:
        if file.endswith('.wav'):
            wav_file = os.path.join(root, file)
            output = f'g:/fretdance介绍视频音源/视频二/{file[:-4]}.json'
            subprocess.run(['G:\Rhubarb-Lip-Sync-1.13.0-Windows\\rhubarb.exe', '-r', 'phonetic', '-f', 'json', '--datUsePrestonBlair', '-o', output,
                            wav_file], shell=True)


finish = time.time()

print(f'Finished in {finish - start} seconds')
