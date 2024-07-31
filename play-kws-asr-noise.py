
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import pyaudio
import wave
import os
import threading

# 读取 Excel 表格函数
def read_audio_paths(excel_path):
    try:
        df = pd.read_excel(excel_path, sheet_name='Sheet1')
        return df
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return pd.DataFrame()

# 播放单个音频的辅助函数
def play_single_audio(pa, audio_path, output_device_index):
    try:
        with wave.open(audio_path, 'rb') as wave_file:
            frames = wave_file.readframes(wave_file.getnframes())
            data = np.frombuffer(frames, dtype=np.int16)
            fs = wave_file.getframerate()
            num_channels = wave_file.getnchannels()

        stream = pa.open(format=pyaudio.paInt16,
                         channels=num_channels,
                         rate=fs,
                         output=True,
                         output_device_index=output_device_index)

        stream.write(data.tobytes())
        stream.stop_stream()
        stream.close()

        print(f"Finished playing audio: {audio_path}")
    except Exception as e:
        print(f"Failed to play audio: {audio_path}. Error: {e}")

# 循环播放固定音频的函数，使用系统默认设备
def play_fixed_audio_loop(pa, fixed_audio_path):
    try:
        with wave.open(fixed_audio_path, 'rb') as wave_file:
            frames = wave_file.readframes(wave_file.getnframes())
            data = np.frombuffer(frames, dtype=np.int16)
            fs = wave_file.getframerate()
            num_channels = wave_file.getnchannels()

        stream = pa.open(format=pyaudio.paInt16,
                         channels=num_channels,
                         rate=fs,
                         output=True)

        while True:  # 循环播放固定音频
            stream.write(data.tobytes())
    except Exception as e:
        print(f"Failed to play fixed audio loop: {fixed_audio_path}. Error: {e}")

# 循环播放 Excel 表格中的每个音频文件，并在每条音频前插入指定的音频
def play_audios_from_excel(pa, df, output_device_id_main, fade_audio_path):
    for index, row in df.iterrows():
        audio_path = row['wavepath']
        
        if not os.path.isfile(audio_path):
            print(f"Audio file not found: {audio_path}. Skipping...")
            continue

        # 播放指定的音频
        play_single_audio(pa, fade_audio_path, output_device_id_main)
        # 播放列表中的音频
        play_single_audio(pa, audio_path, output_device_id_main)

# 主函数
def main():
    excel_path = 'audio_paths.xlsx'  # 替换为你的 Excel 文件路径
    output_device_id_main = 7  # 替换为你的音频硬件编号
    fade_audio_path = r'D:\Audio\kw-pudus.wav'  # 指定要插入的音频文件路径
    fixed_audio_path = r'D:\Audio\background.wav'  # 指定要循环播放的固定音频文件路径

    # 初始化 PyAudio
    pa = pyaudio.PyAudio()

    # 获取当前系统默认的声音设备索引
    default_output_device_index = pa.get_default_output_device_info()['index']

    # 确保输出设备 ID 是有效的
    num_devices = pa.get_device_count()
    if output_device_id_main >= num_devices or default_output_device_index >= num_devices:
        print("One of the output device IDs is invalid. Please check the device IDs.")
        pa.terminate()
        return

    # 在单独的线程播放固定音频循环
    fixed_audio_thread = threading.Thread(target=play_fixed_audio_loop, args=(pa, fixed_audio_path))
    fixed_audio_thread.daemon = True  # 设置为守护线程
    fixed_audio_thread.start()

    # 读取 Excel 表格中的音频路径
    df = read_audio_paths(excel_path)

    # 播放 Excel 表格中的音频文件，并在每条音频前插入指定的音频
    play_audios_from_excel(pa, df, output_device_id_main, fade_audio_path)

    # 等待固定音频循环播放线程结束
    fixed_audio_thread.join()

    # 终止 PyAudio
    pa.terminate()

if __name__ == "__main__":
    main()
