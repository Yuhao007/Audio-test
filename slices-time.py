# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from datetime import datetime

# 假设已知参数
SAMPLE_RATE = 16000  # 采样率

# 将日期时间字符串转换为时间戳
def parse_timestamp(timestamp_str):
    return datetime.strptime(timestamp_str, '%Y-%m-%d_%H-%M-%S')

# 将帧索引转换为秒
def frames_to_seconds(frames, sample_rate):
    return frames / float(sample_rate)

# 读取PCM原始音频数据
def read_pcm_file(filename, sample_rate):
    with open(filename, 'rb') as f:
        audio_data = np.fromfile(f, dtype=np.int16)
    return audio_data

# 音频切片
def slice_audio(audio_data, sample_rate, start_times, end_times):
    slices = []
    for start, end in zip(start_times, end_times):
        start_frame = int(start * sample_rate)
        end_frame = int(end * sample_rate)
        start_sec = frames_to_seconds(start_frame, sample_rate)
        end_sec = frames_to_seconds(end_frame, sample_rate)
        print(f"Slicing from {start_sec:.2f}s to {end_sec:.2f}s")  # 打印时间范围
        if start_frame < len(audio_data) and end_frame <= len(audio_data):
            slices.append(audio_data[start_frame:end_frame])
        else:
            print(f"Error: Slice range from {start_sec:.2f}s to {end_sec:.2f}s is out of bounds.", end='\n')
    return slices

# 保存切片后的音频
def save_pcm_slices(slices, filenames, output_dir):
    for i, audio_slice in enumerate(slices):
        if audio_slice.size > 0:  # 确保切片不为空
            filename = f"{output_dir}/audio_slice_{filenames[i]}.pcm"
            audio_slice.tofile(filename)
            print(f"Saved audio slice as {filename}")
        else:
            print(f"No audio data for slice {filenames[i]}")

# 主函数
def main(audio_file, excel_file, output_dir, base_timestamp):
    # 读取音频数据
    audio_data = read_pcm_file(audio_file, SAMPLE_RATE)
    
    # 读取Excel表格中的切片规则
    df = pd.read_excel(excel_file)
    
    # 将base_timestamp转换为时间戳
    base_timestamp_dt = parse_timestamp(base_timestamp)
    
    # 将Excel中的日期时间字符串转换为时间戳，并与base_timestamp计算时间差
    df['start_seconds'] = (df['start'].apply(parse_timestamp) - base_timestamp_dt).dt.total_seconds()
    df['end_seconds'] = (df['end'].apply(parse_timestamp) - base_timestamp_dt).dt.total_seconds()
    
    # 音频切片
    audio_slices = slice_audio(audio_data, SAMPLE_RATE, df['start_seconds'], df['end_seconds'])
    
    # 保存切片后的音频
    save_pcm_slices(audio_slices, df['wavepath'].tolist(), output_dir)

if __name__ == "__main__":
    audio_file = r'D:\log\test\test.pcm'  # PCM原始音频文件路径
    excel_file = r'D:\log\test\test.xlsx'  # Excel文件路径
    output_dir = r'D:\log\test\output'  # 输出目录
    base_timestamp = '2024-07-31_10-03-24'  # 音频的起始点
    main(audio_file, excel_file, output_dir, base_timestamp)
