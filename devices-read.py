import pyaudio
import wave

def list_audio_devices():
    pa = pyaudio.PyAudio()

    print("Input Devices:")
    for i in range(pa.get_device_count()):
        dev = pa.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0:
            print(f"{i}: {dev['name']}")

    print("\nOutput Devices:")
    for i in range(pa.get_device_count()):
        dev = pa.get_device_info_by_index(i)
        if dev['maxOutputChannels'] > 0:
            print(f"{i}: {dev['name']}")

    pa.terminate()

if __name__ == "__main__":
    list_audio_devices()
