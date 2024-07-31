# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import pyaudio
import wave
import os
import threading
import time
from datetime import datetime

# 读取 Excel 表格函数
def read_audio_paths(excel_path):
    try:
        df = pd.read_excel(excel_path, sheet_name='Sheet1')  # 确保工作表名称正确
        return df
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return pd.DataFrame()  # 返回空DataFrame

# 播放单个音频的函数
def play_audio(pa, audio_path, output_device_index):
    try:
        with wave.open(audio_path, 'rb') as wave_file:
            frames = wave_file.readframes(wave_file.getnframes())
            data = np.frombuffer(frames, dtype=np.int16)
            fs = wave_file.getframerate()
            num_channels = wave_file.getnchannels()

        stream = pa.open(format=pa.get_format_from_width(wave_file.getsampwidth()),
                         channels=num_channels,
                         rate=fs,
                         output=True,
                         output_device_index=output_device_index)

        stream.write(data.tobytes())
        stream.stop_stream()  # 停止流
        stream.close()  # 关闭流

        print(f"Finished playing audio: {audio_path}")
    except Exception as e:
        print(f"Failed to play audio: {audio_path}. Error: {e}")

# 插入静音的函数
def insert_silence(data, fs, num_channels, duration=1):
    silence = np.zeros(int(fs * duration * num_channels), dtype=np.int16)
    return np.concatenate((data, silence))

# 写入时间戳到 Excel 表格
def write_timestamp_to_excel(excel_path, index, start_time, end_time):
    try:
        df = pd.read_excel(excel_path, sheet_name='Sheet1')
        df.at[index, 'start'] = start_time
        df.at[index, 'end'] = end_time
        df.to_excel(excel_path, sheet_name='Sheet1', index=False)
    except Exception as e:
        print(f"Error writing to Excel file: {e}")

# 循环播放 Excel 表格中的每个音频文件
def play_audios_from_excel(pa, df, output_device_id_main, excel_path):
    for index, row in df.iterrows():
        audio_path = row['wavepath']
        
        if not os.path.isfile(audio_path):
            print(f"Audio file not found: {audio_path}. Skipping...")
            continue

        # 记录开始时间
        start_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        write_timestamp_to_excel(excel_path, index, start_time, None)

        # 插入前静音
        time.sleep(1)

        with wave.open(audio_path, 'rb') as wave_file:
            frames = wave_file.readframes(wave_file.getnframes())
            data = np.frombuffer(frames, dtype=np.int16)
            fs = wave_file.getframerate()
            num_channels = wave_file.getnchannels()

        # 插入后静音
        data_with_silence = insert_silence(data, fs, num_channels)
        data_with_silence = insert_silence(data_with_silence, fs, num_channels, duration=1)

        stream = pa.open(format=pa.get_format_from_width(wave_file.getsampwidth()),
                         channels=num_channels,
                         rate=fs,
                         output=True,
                         output_device_index=output_device_id_main)

        stream.write(data_with_silence.tobytes())
        stream.stop_stream()  # 停止流
        stream.close()  # 关闭流

        # 记录结束时间
        end_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        write_timestamp_to_excel(excel_path, index, start_time, end_time)
        
        print(f"Finished playing audio: {audio_path}")

        # 休息10秒
        time.sleep(10)

# 播放固定音频的函数，使用系统默认设备循环播放
def play_fixed_audio_loop(pa, audio_path, device_index):
    try:
        with wave.open(audio_path, 'rb') as wave_file:
            frames = wave_file.readframes(wave_file.getnframes())
            data = np.frombuffer(frames, dtype=np.int16)
            fs = wave_file.getframerate()
            num_channels = wave_file.getnchannels()

        stream = pa.open(format=pa.get_format_from_width(wave_file.getsampwidth()),
                         channels=num_channels,
                         rate=fs,
                         output=True,
                         output_device_index=device_index)

        while True:  # 循环播放固定音频
            stream.write(data.tobytes())
    except Exception as e:
        print(f"Failed to play fixed audio loop: {audio_path}. Error: {e}")

# 主函数
def main():
    excel_path = 'audio_paths.xlsx'  # 替换为你的 Excel 文件路径
    output_device_id_main = 10  # 替换为你的音频硬件编号

    # 初始化 PyAudio
    pa = pyaudio.PyAudio()

    # 获取当前系统默认的声音设备索引
    default_output_device_index = pa.get_default_output_device_info()['index']

    # 确保输出设备 ID 是有效的
    num_devices = pa.get_device_count()
    if output_device_id_main >= num_devices:
        print("The output device ID for main audio is invalid. Please check the device ID.")
        pa.terminate()
        return

    # 读取 Excel 表格中的音频路径
    df = read_audio_paths(excel_path)

    # 硬编码要循环播放的音频文件路径
    fixed_audio_path = r'D:\Audio\background.wav'

    # 在单独的线程播放固定音频循环
    fixed_audio_thread = threading.Thread(target=play_fixed_audio_loop, args=(pa, fixed_audio_path, default_output_device_index))
    fixed_audio_thread.daemon = True  # 设置为守护线程
    fixed_audio_thread.start()

    # 播放 Excel 表格中的音频文件
    play_audios_from_excel(pa, df, output_device_id_main, excel_path)
   
    # 等待固定音频循环播放线程结束
    fixed_audio_thread.join()

    # 终止 PyAudio
    pa.terminate()

if __name__ == "__main__":
    main()
