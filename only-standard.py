import os
import subprocess
from pydub import AudioSegment

# 设置输入和输出目录
input_dir = '.'  # 当前文件夹
output_dir = os.path.join('.', 'output')
standard_audio_dir = os.path.join('.', 'standard-audio')

# 确保输出文件夹存在
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
if not os.path.exists(standard_audio_dir):
    os.makedirs(standard_audio_dir)

# 遍历当前文件夹下的所有文件
for filename in os.listdir(input_dir):
    # 检查文件是否为 MP3 格式
    if filename.endswith('.mp3'):
        # 构建输入和输出文件路径
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + '.wav')

        # 使用 FFmpeg 进行转换
        try:
            subprocess.run(['ffmpeg', '-i', input_path, '-c:a', 'pcm_s16le', '-ar', '16000', '-ac', '1', output_path], check=True)
            print(f"Successfully converted {filename} to {os.path.basename(output_path)}")
        except subprocess.CalledProcessError as e:
            print(f"Error converting {filename}: {e}")

# 设置要添加的前缀
prefix = 'CN_guide_'

# 遍历输出文件夹中的所有文件
for filename in os.listdir(output_dir):
    # 检查是否为音频文件
    if filename.endswith('.wav'):
        # 构建输入和输出文件路径
        input_path = os.path.join(output_dir, filename)
        output_filename = prefix + os.path.splitext(filename)[0] + '.wav'
        output_path = os.path.join(standard_audio_dir, output_filename)

        # 使用 pydub 加载音频文件
        audio = AudioSegment.from_file(input_path)

        # 转换为 16kHz 采样率、单声道、16位 PCM 编码的 WAV 格式
        audio = audio.set_frame_rate(16000)
        audio = audio.set_channels(1)
        audio = audio.set_sample_width(2)

        # 音量标准化
        audio = audio.normalize()

        # 输出 WAV 文件
        audio.export(output_path, format='wav')
        print(f'Processed: {filename} -> {output_filename}')
