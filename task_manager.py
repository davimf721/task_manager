import curses
import sys
import psutil
import time
import signal

def get_system_stats():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
    disk_usage = psutil.disk_usage('/').percent
    return cpu_usage, memory_usage, disk_usage

def signal_handler(signum, frame):
    curses.endwin()
    print("Exiting safely...")
    sys.exit(0)

    
def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(1000)
    
    while True:
        stdscr.clear()

        cpu, memory, disk = get_system_stats()

        stdscr.addstr(0, 0, "Task Manager", curses.A_BOLD)
        stdscr.addstr(2, 0, f"CPU Usage:    {cpu}%")
        stdscr.addstr(3, 0, f"Memory Usage: {memory}%")
        stdscr.addstr(4, 0, f"Disk Usage:   {disk}%")
        stdscr.addstr(5,0, "Press q to exit.", curses.A_BOLD)
        
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