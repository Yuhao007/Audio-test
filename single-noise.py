
# -*- coding: utf-8 -*-
import pyaudio
import wave
import threading
import numpy as np

# 播放固定音频的函数，使用指定设备循环播放
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
                         frames_per_buffer=1024 * 10,  # 增加缓冲区大小
                         output_device_index=device_index)

        while True:  # 循环播放固定音频
            stream.write(data.tobytes())
    except Exception as e:
        print(f"Failed to play fixed audio loop: {audio_path}. Error: {e}")

# 主函数
def main():
    audio_path = r'D:\Audio\background2.wav'  # 替换为你的音频文件路径
    output_device_id = 5  # 替换为你指定的音频硬件编号

    # 初始化 PyAudio
    pa = pyaudio.PyAudio()

    # 确保输出设备 ID 是有效的
    num_devices = pa.get_device_count()
    if output_device_id >= num_devices:
        print("The output device ID is invalid. Please check the device ID.")
        pa.terminate()
        return

    # 在单独的线程播放固定音频循环
    fixed_audio_thread = threading.Thread(target=play_fixed_audio_loop, args=(pa, audio_path, output_device_id))
    fixed_audio_thread.daemon = True  # 设置为守护线程
    fixed_audio_thread.start()

    # 保持主线程运行，防止程序退出
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        pa.terminate()

if __name__ == "__main__":
    main()
