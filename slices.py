# -*- coding: gbk -*-

import numpy as np
import pandas as pd

# 假设已知参数
SAMPLE_RATE = 16000  # 采样率
CHANNELS = 1         # 通道数，这里是单通道

# 读取PCM原始音频数据
def read_pcm_file(filename, sample_rate, channels):
    with open(filename, 'rb') as f:
        audio_data = np.fromfile(f, dtype=np.int16)
    return audio_data

# 音频切片
def slice_audio(audio_data, sample_rate, start_times, end_times):
    slices = []
    for start, end in zip(start_times, end_times):
        start_frame = int(start * sample_rate)
        end_frame = int(end * sample_rate)
        slices.append(audio_data[start_frame:end_frame])
    return slices

# 保存切片后的音频
def save_pcm_slices(slices, sample_rate, output_dir):
    for i, audio_slice in enumerate(slices):
        filename = f"{output_dir}/audio_slice_{i+1}.pcm"
        audio_slice.tofile(filename)

# 主函数
def main(audio_file, excel_file, output_dir):
    # 读取音频数据
    audio_data = read_pcm_file(audio_file, SAMPLE_RATE, CHANNELS)
    
    # 读取Excel表格中的切片规则
    df = pd.read_excel(excel_file)
    '''
    start_times = df['start'] / 1000  # 假定Excel中的时间为毫秒，转换为秒
    end_times = df['end'] / 1000
    '''
    start_times = df['start'] 
    end_times = df['end'] 
    
    # 音频切片
    audio_slices = slice_audio(audio_data, SAMPLE_RATE, start_times, end_times)
    
    # 保存切片后的音频
    save_pcm_slices(audio_slices, SAMPLE_RATE, output_dir)

if __name__ == "__main__":
    audio_file = r'D:\log\testshort\test1.pcm'  # PCM原始音频文件路径
    excel_file = r'D:\log\testshort\in.xlsx'  # Excel文件路径
    output_dir = r'D:\log\testshort\output'  # 输出目录
    main(audio_file, excel_file, output_dir)
