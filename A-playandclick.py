# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import pyaudio
import wave
import time
from datetime import datetime
import subprocess  # 导入 subprocess 模块用于执行 adb 命令

# 读取 Excel 表格函数
def read_audio_paths(excel_path):
    try:
        df = pd.read_excel(excel_path, sheet_name='Sheet1')
        return df
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return pd.DataFrame()

# 插入静音的函数
def insert_silence(data, fs, num_channels, duration=1):
    # 计算静音的样本数
    silence_length = int(fs * duration)
    # 生成静音数据，这里假设音频是16位的，因此每个样本是2字节
    silence = np.zeros(silence_length * num_channels, dtype=np.int16)
    return np.concatenate((silence, data, silence))

# 播放单个音频的函数，并记录时间
def play_audio_and_record_time(df, index, excel_path):
    try:
        # 初始化 PyAudio
        pa = pyaudio.PyAudio()

        # 获取音频文件路径
        audio_path = df.at[index, 'wavepath']

        with wave.open(audio_path, 'rb') as wave_file:
            frames = wave_file.readframes(wave_file.getnframes())
            data = np.frombuffer(frames, dtype=np.int16)
            fs = wave_file.getframerate()
            num_channels = wave_file.getnchannels()
            
        # 记录开始播放的时间
        start = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        df.at[index, 'start'] = start
        

        # 在音频的前后添加静音段
        data_with_silence = insert_silence(data, fs, num_channels)

        stream = pa.open(format=pa.get_format_from_width(wave_file.getsampwidth()),
                         channels=num_channels,
                         rate=fs,
                         output=True)

        stream.write(data_with_silence.tobytes())
        stream.stop_stream()
        stream.close()
        
        time.sleep(1)

        # 记录结束播放的时间
        end = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        df.at[index, 'end'] = end

        print(f"Finish played No.{index + 1} audio from {start} to {end}")
        
        # 写入时间到 Excel
        write_timestamp_to_excel(df, excel_path)

        # 等待8秒的间隔
        time.sleep(8)

        # 执行屏幕点击操作
        click_screen(139, 679)

    except Exception as e:
        print(f"Failed to play audio: {audio_path}. Error: {e}")
    finally:
        pa.terminate()

# 写入时间戳到 Excel 表格
def write_timestamp_to_excel(df, excel_path):
    try:
        df.to_excel(excel_path, sheet_name='Sheet1', index=False)
    except Exception as e:
        print(f"Error writing to Excel file: {e}")

# 屏幕点击操作（针对 Android 设备）
def click_screen(x, y):
    try:
        # 使用 adb 命令模拟屏幕点击
        subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)], check=True)
        print(f"Clicked at coordinates: ({x}, {y})")
    except Exception as e:
        print(f"Failed to click screen. Error: {e}")

# 主函数
def main():
    excel_path = 'audio_paths150.xlsx'  # 替换为你的 Excel 文件路径
    df = read_audio_paths(excel_path)

    if not df.empty:
        # 确保 Excel 表中有记录时间的列
        df['start'] = ''
        df['end'] = ''

        # 播放 Excel 表格中的音频文件，并记录时间
        for index in df.index:
            play_audio_and_record_time(df, index, excel_path)

if __name__ == "__main__":
    main()
