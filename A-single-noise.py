# -*- coding: utf-8 -*-
import pyaudio
import wave
import threading
import numpy as np

# 列出所有音频设备
def list_audio_devices(pa):
    device_count = pa.get_device_count()
    print("Input Devices:")
    for i in range(device_count):
        dev = pa.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0:
            print(f"{i}: {dev['name']}")
    
    print("\nOutput Devices:")
    for i in range(device_count):
        dev = pa.get_device_info_by_index(i)
        if dev['maxOutputChannels'] > 0:
            print(f"{i}: {dev['name']}")

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
                         frames_per_buffer=1024 * 10,
                         output_device_index=device_index)

        while True:
            stream.write(data.tobytes())
    except Exception as e:
        print(f"Failed to play fixed audio loop: {audio_path}. Error: {e}")

# 主函数
def main():
    audio_path = r'D:\Audio\background2.wav'  # 替换为你的音频文件路径

    # 初始化 PyAudio
    pa = pyaudio.PyAudio()

    # 列出音频设备
    list_audio_devices(pa)

    # 获取用户输入的设备号
    output_device_id = int(input("Enter the output device ID to play audio: "))

    # 确保输出设备 ID 是有效的
    if output_device_id >= pa.get_device_count():
        print("The output device ID is invalid. Please check the device ID.")
        pa.terminate()
        return

    # 在单独的线程播放固定音频循环
    fixed_audio_thread = threading.Thread(target=play_fixed_audio_loop, args=(pa, audio_path, output_device_id))
    fixed_audio_thread.daemon = True
    fixed_audio_thread.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        pa.terminate()

if __name__ == "__main__":
    main()
