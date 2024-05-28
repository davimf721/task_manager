import curses
import psutil
import GPUtil
import time
import signal
import sys
from collections import deque


def get_system_stats():
    cpu_usage = psutil.cpu_percent(interval=0.5)
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
    disk_usage = psutil.disk_usage('/').percent
    
    gpus = GPUtil.getGPUs()
    if gpus:
        gpu = gpus[0]
        gpu_usage = gpu.load * 100
        gpu_memory_usage = gpu.memoryUtil * 100
        gpu_temp = gpu.temperature
    else:
        gpu_usage = gpu_memory_usage = gpu_temp = 0

    return cpu_usage, memory_usage, disk_usage, gpu_usage, gpu_memory_usage, gpu_temp


def signal_handler(signum, frame):
    curses.endwin()
    print("Exiting safely...")
    sys.exit(0)


def draw_bar(stdscr, x, y, width, percent, label):
    bar_width = int(width * (percent / 100.0))
    stdscr.addstr(y, x, f"{label}: [")
    stdscr.addstr(y, x + len(label) + 3, "#" * bar_width)
    stdscr.addstr(y, x + len(label) + 3 + bar_width, " " * (width - bar_width) + "]")
    stdscr.addstr(y, x + len(label) + 5 + width, f"{percent}%")

    
def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(1000)
    
     # Initialize deques for averaging GPU stats
    gpu_usage_deque = deque(maxlen=10)
    gpu_memory_usage_deque = deque(maxlen=10)
    gpu_temp_deque = deque(maxlen=10)
    
    while True:
        stdscr.clear()

        cpu, memory, disk, gpu, gpu_memory, gpu_temp = get_system_stats()

         # Append latest GPU stats to deques
        gpu_usage_deque.append(gpu)
        gpu_memory_usage_deque.append(gpu_memory)
        gpu_temp_deque.append(gpu_temp)

        # Calculate averages
        avg_gpu_usage = sum(gpu_usage_deque) / len(gpu_usage_deque)
        avg_gpu_memory_usage = sum(gpu_memory_usage_deque) / len(gpu_memory_usage_deque)
        avg_gpu_temp = sum(gpu_temp_deque) / len(gpu_temp_deque)

        stdscr.addstr(0, 0, "Task Manager", curses.A_BOLD)
        draw_bar(stdscr, 0, 2, 50, cpu, "CPU Usage")
        draw_bar(stdscr, 0, 3, 50, memory, "Memory Usage")
        draw_bar(stdscr, 0, 4, 50, disk, "Disk Usage")
        draw_bar(stdscr, 0, 5, 50, gpu, "GPU Usage")
        draw_bar(stdscr, 0, 6, 50, gpu_memory, "GPU Memory Usage")
        stdscr.addstr(7, 0, f"GPU Temperature: {gpu_temp:.1f} C")
        stdscr.addstr(8,0, "Press q to exit.", curses.A_BOLD)
        
        stdscr.refresh()
        
        key = stdscr.getch()
        if key == ord('q'):
            break

if __name__ == "__main__":
    curses.wrapper(main)
      # Register signal handler for safe exit
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    curses.wrapper(main)