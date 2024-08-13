# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from datetime import datetime
import wave

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

# 音频切片，添加start_offset和end_offset参数
def slice_audio(audio_data, sample_rate, start_times, end_times, start_offset=0, end_offset=0):
    slices = []
    for start, end in zip(start_times, end_times):
        start_frame = int((start + start_offset) * sample_rate)
        end_frame = int((end + end_offset) * sample_rate)
        start_sec = frames_to_seconds(start_frame, sample_rate)
        end_sec = frames_to_seconds(end_frame, sample_rate)
        print(f"Slicing from {start_sec:.2f}s to {end_sec:.2f}s")  # 打印时间范围
        if start_frame >= 0 and end_frame <= len(audio_data):
            slices.append(audio_data[start_frame:end_frame])
        else:
            print(f"Error: Slice range from {start_sec:.2f}s to {end_sec:.2f}s is out of bounds.", end='\n')
    return slices

# 保存切片后的音频为WAV格式
def save_wav_slices(slices, filenames, output_dir):
    for i, audio_slice in enumerate(slices):
        if audio_slice.size > 0:  # 确保切片不为空
            filename = f"{output_dir}/audio_slice_{filenames[i]}.wav"
            with wave.open(filename, 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(SAMPLE_RATE)
                wav.writeframes(audio_slice.tobytes())
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
    
    # 定义start_offset和end_offset
    start_offset = -3  # 开始时间往前1秒
    end_offset = 3     # 结束时间往后1秒
    
    # 音频切片，使用新的start_offset和end_offset
    audio_slices = slice_audio(audio_data, SAMPLE_RATE, df['start_seconds'], df['end_seconds'], start_offset, end_offset)
    
    # 保存切片后的音频为WAV格式
    save_wav_slices(audio_slices, df['wavepath'].tolist(), output_dir)

if __name__ == "__main__":
    audio_file = r'D:\Audio\test_tool\test result\speech_quiet.pcm'  # PCM原始音频文件路径
    excel_file = r'D:\Audio\test_tool\test result\speech-quiet.xlsx'  # Excel文件路径
    output_dir = r'D:\Audio\test_tool\test result\speech-quiet'    # 输出目录，确保使用英文字符和空格

    base_timestamp = '2024-08-12_18-02-06'  # 音频的起始点
    main(audio_file, excel_file, output_dir, base_timestamp)
