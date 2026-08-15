"""
ASCII Productivity Timer - Main Application
Features:
- Pomodoro (25min work / 5min break)
- Custom timer
- Visual progress bars
- Zen-style text displays
- Road-trip progress visualization
"""

import sys
import time
from datetime import datetime
from art import (
    render_progress_bar,
    render_time_bubble,
    render_heart_beat,
    render_wave_animation,
    render_zen_text,
    render_clock_ascii,
    render_progress_dots,
    render_vertical_bar,
    render_road_trip,
    WORKS_ASCII,
    BREAK_ASCII,
    COMPLETE_ASCII
)


class AsyncTimer:
    """Main timer controller with ASCII visualizations"""
    
    def __init__(self, work_minutes=25, break_minutes=5):
        self.work_minutes = work_minutes
        self.break_minutes = break_minutes
        self.current_mode = "work"
        self.work_count = 0
        self.break_count = 0
        self.start_time = None
        self.end_time = None
    
    def start(self, mode="work"):
        """Start the timer in specified mode"""
        self.current_mode = mode
        self.start_time = datetime.now()
        print(f"\n🕒 {mode.capitalize()} Timer Started!")
        print(WORKS_ASCII)
        print("Press Ctrl+C to cancel\n")
        self.run()
    
    def stop(self):
        """Stop the timer and show summary"""
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds() / 60
            print(f"\n✅ Timer stopped! Total time: {elapsed:.1f} minutes")
            self.show_summary()
    
    def run(self):
        """Main timer loop"""
        try:
            while True:
                if self.current_mode == "work":
                    self.do_work_phase()
                else:
                    self.do_break_phase()
                
                # Check for interrupt
                if self.is_interrupted:
                    break
                
                # Small delay to prevent CPU spinning
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n⏹️ Timer interrupted by user")
            self.stop()
    
    def do_work_phase(self):
        """Work phase - 25 minutes"""
        print(f"\n🔥 WORK PHASE ({self.work_minutes} min)\n")
        print(render_zen_text("Focus on your task!", width=50))
        print(render_progress_bar(0, width=40))
        print(render_time_bubble(int(self.work_minutes * 60), label="WORK"))
        
        # Simulate work period
        for i in range(self.work_minutes * 60):
            time.sleep(1)
            # Update progress bar every minute
            if i % 60 == 0:
                rendered = render_progress_bar(i // 60, width=40)
                print(f"  Progress: {rendered}")
        
        self.work_count += 1
        print(f"\n🏁 Work session completed! Count: {self.work_count}\n")
        self.work_count = 0
    
    def do_break_phase(self):
        """Break phase - 5 minutes"""
        print(f"\n☕ BREAK PHASE ({self.break_minutes} min)\n")
        print(BREAK_ASCII)
        print(render_zen_text("Relax and recharge!", width=50))
        print(render_progress_bar(0, width=40))
        print(render_time_bubble(int(self.break_minutes * 60), label="BREAK"))
        
        # Simulate break period
        for i in range(self.break_minutes * 60):
            time.sleep(1)
            if i % 60 == 0:
                rendered = render_progress_bar(i // 60, width=40)
                print(f"  Progress: {rendered}")
        
        self.break_count += 1
        print(f"\n🎉 Break session completed! Count: {self.break_count}\n")
        self.break_count = 0
    
    def show_summary(self):
        """Display timer summary"""
        total_work = self.work_count * self.work_minutes
        total_break = self.break_count * self.break_minutes
        total = total_work + total_break
        
        print("\n" + "=" * 50)
        print("📊 TIMER SUMMARY")
        print("=" * 50)
        print(f"  Work sessions: {self.work_count}")
        print(f"  Break sessions: {self.break_count}")
        print(f"  Total time: {total} minutes")
        print(f"  Mode: {'Work' if self.current_mode == 'work' else 'Break'}")
        print("=" * 50)
    
    def is_interrupted(self):
        """Check if timer was interrupted"""
        return False


def main():
    """Entry point for the ASCII Timer"""
    print("""
╔══════════════════════════════════════╗
║     ASCII PRODUCTIVITY TIMER         ║
║     🕐 Simple & Stylish Timer        ║
╚══════════════════════════════════════╝

Choose mode:
  1 - Work Phase (25 min)
  2 - Break Phase (5 min)
  3 - Custom Timer (enter duration)
  q - Quit

Select mode (1/2/3/q):\n""")
    
    choice = input().strip()
    
    if choice == "1":
        timer = AsyncTimer(work_minutes=25, break_minutes=5)
        timer.start("work")
    elif choice == "2":
        timer = AsyncTimer(work_minutes=25, break_minutes=5)
        timer.start("break")
    elif choice == "3":
        try:
            duration = float(input("Enter duration in minutes (e.g., 30): "))
            timer = AsyncTimer(work_minutes=int(duration // 25), break_minutes=int(duration % 25))
            timer.start("work")
        except ValueError:
            print("Invalid input. Using default 25/5 split.")
            timer = AsyncTimer(work_minutes=25, break_minutes=5)
            timer.start("work")
    elif choice.lower() == "q":
        print("👋 Goodbye!")
        sys.exit(0)
    else:
        print("Unknown option. Use 1, 2, 3, or q.")


if __name__ == "__main__":
    main()
