import os
from pydub import AudioSegment
from pydub.silence import detect_nonsilent

def trim_silence(input_dir, output_dir, silence_thresh=-60, min_silence_len=100):
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 遍历输入目录中的所有文件
    for filename in os.listdir(input_dir):
        if filename.endswith(".wav"):
            file_path = os.path.join(input_dir, filename)
            audio = AudioSegment.from_wav(file_path)

            # 检测非静音部分
            nonsilent_ranges = detect_nonsilent(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)

            # 如果存在非静音部分，则裁剪音频
            if nonsilent_ranges:
                start_trim = nonsilent_ranges[0][0]
                end_trim = nonsilent_ranges[-1][1]
                trimmed_audio = audio[start_trim:end_trim]

                # 保存文件到输出目录
                output_file_path = os.path.join(output_dir, filename)
                trimmed_audio.export(output_file_path, format="wav")
                print(f"Processed and saved: {output_file_path}")
            else:
                print(f"No non-silent parts found in: {file_path}")

# 使用示例
input_directory = "input"
output_directory = "output"
trim_silence(input_directory, output_directory)
