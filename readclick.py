import subprocess
import re
import time

def get_click_coordinates():
    print("正在启动监听...")
    print("请在设备上点击屏幕，按 Ctrl+C 停止监听。")
    
    # 启动 getevent 命令
    process = subprocess.Popen(
        ["adb", "shell", "getevent", "-l"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # 定义正则表达式，匹配触摸事件
    x_pattern = re.compile(r"ABS_MT_POSITION_X.*\s+([0-9a-fA-F]+)")
    y_pattern = re.compile(r"ABS_MT_POSITION_Y.*\s+([0-9a-fA-F]+)")
    x = None
    y = None

    try:
        while True:
            line = process.stdout.readline()
            if not line:
                break

            # 匹配 X 坐标
            match_x = x_pattern.search(line)
            if match_x:
                x = int(match_x.group(1), 16)  # 将十六进制转换为十进制

            # 匹配 Y 坐标
            match_y = y_pattern.search(line)
            if match_y:
                y = int(match_y.group(1), 16)  # 将十六进制转换为十进制

            # 如果同时获取到 X 和 Y 坐标，则输出
            if x is not None and y is not None:
                print(f"点击坐标: ({x}, {y})")
                x = None
                y = None
    except KeyboardInterrupt:
        print("\n监听已停止。")
    finally:
        process.kill()  # 确保子进程被终止

if __name__ == "__main__":
    get_click_coordinates()
