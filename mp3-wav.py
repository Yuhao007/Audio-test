import os
import subprocess

# 设置输入和输出目录
input_dir = r'D:\test\TTS\output_audio'  # 指定输入文件夹路径
output_dir = r'D:\test\TTS\output' # 指定输出文件夹路径

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 遍历指定文件夹下的所有文件
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
