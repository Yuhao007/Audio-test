#!/usr/bin/env python3
"""最简ADB坐标获取工具 - 直接读触摸事件文件"""

import subprocess
import re
import sys
import time

def get_coordinates():
    # 检查ADB连接
    result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    devices = [line for line in lines[1:] if line.strip() and 'device' in line]
    if not devices:
        print("未找到设备，请检查ADB连接")
        sys.exit(1)
    
    print(f"已连接设备: {devices[0].split()[0]}")
    
    # 查找所有触摸相关的事件设备
    result = subprocess.run(
        ['adb', 'shell', 'ls', '/dev/input/'],
        capture_output=True, text=True
    )
    print(f"可用输入设备:\n{result.stdout}")
    
    # 尝试直接从dumpsys获取
    print("\n开始监听 (点击屏幕测试)...")
    print("如果没有输出，请手动执行: adb shell getevent -l")
    print("然后点击屏幕，把输出发给我看看\n")
    
    # 最后一招：直接用input tap的反向思路，持续监控
    process = subprocess.Popen(
        ['adb', 'shell', 'cat', '/proc/bus/input/devices'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    output = process.communicate()[0]
    
    # 找触摸屏设备
    touch_handler = None
    for section in output.split('\n\n'):
        if 'Touch' in section or 'touch' in section or 'ts' in section.lower():
            handler_match = re.search(r'Handlers=.*?(event\d+)', section)
            if handler_match:
                touch_handler = handler_match.group(1)
                print(f"找到触摸设备: /dev/input/{touch_handler}")
    
    if not touch_handler:
        print("没找到触摸设备，帮你测试一下getevent...")
        result = subprocess.run(
            ['adb', 'shell', 'getevent', '-l', '-c', '10'],
            capture_output=True, 
            text=True,
            timeout=5
        )
        print(f"getevent输出:\n{result.stdout[:500]}")
        return
    
    # 直接监听找到的设备
    print("开始监听屏幕点击 (Ctrl+C 停止)\n")
    
    process = subprocess.Popen(
        ['adb', 'shell', 'getevent', '-l', '/dev/input/' + touch_handler],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    touch = {}
    
    try:
        for line in process.stdout:
            if 'ABS_MT_POSITION_X' in line:
                hex_val = line.split()[-1]
                touch['x'] = int(hex_val, 16)
            elif 'ABS_MT_POSITION_Y' in line:
                hex_val = line.split()[-1]
                touch['y'] = int(hex_val, 16)
            elif 'BTN_TOUCH' in line and 'UP' in line:
                if touch.get('x') and touch.get('y'):
                    print(f"({touch['x']}, {touch['y']})")
                    
    except KeyboardInterrupt:
        print("\n已停止")
        process.terminate()

if __name__ == '__main__':
    get_coordinates()
