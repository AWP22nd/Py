"""
ASCII Art Library for Productivity Timer
Contains visual elements for timer display
"""

def render_progress_bar(percent, width=40):
    """Render a progress bar with Unicode block characters"""
    filled = int(width * percent / 100)
    empty = width - filled
    
    # Use gradient blocks for fancy look
    bar = '█' * filled + '░' * empty
    return f"[{bar}] {percent:.0f}%"


def render_time_bubble(seconds, label="TIME"):
    """Display time in a cute bubble format"""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    
    time_str = f"{mins:02d}:{secs:02d}"
    
    bubble = f"""
   ╭─────{label}─────╮
   │   {time_str}    │
   ╰─────────────────╯
"""
    return bubble


def render_heart_beat(count=0):
    """Animated heart beat for work sessions"""
    hearts = ["♥", "♥", "♦", "♥", "♥"]
    return hearts[count % len(hearts)]


async def render_wave_animation(seconds):
    """Generate wave animation for timer"""
    from itertools import cycle
    
    waves = [
        "🌊",
        "🌊",
        "🌊",
        "🌊",
        "🌊",
    ]
    
    positions = ["~", "~", "~", "~", "~", "~", "~", "~"]
    animation = f"""
    {' '.join(positions[:seconds % 8])}
    {chr(960) * min(10, 4 + seconds // 5)}
    """
    return animation


def render_zen_text(text, width=40):
    """Render text in a zen box"""
    lines = text.center(width - 4).split('\n')
    box = "╭" + "─" * (width - 2) + "╮\n"
    for line in lines:
        box += f"│ {line.ljust(width - 4)} │\n"
    box += "╰" + "─" * (width - 2) + "╯"
    return box


def render_clock_ascii(state="work"):
    """Display a simple ASCII clock face"""
    if state == "work":
        return """
        ╔═════════╗
        ║  🔨  WORK ║
        ╚═════════╝
        """
    elif state == "break":
        return """
        ╔═════════╗
        ║  ☕ BREAK ║
        ╚═════════╝
        """
    elif state == "done":
        return """
        ╔═════════╗
        ║  ✅ DONE ║
        ╚═════════╝
        """
    return ""


def render_progress_dots(count=0):
    """Render progress dots"""
    return "[" + "●" * count + "○" * (5 - count) + "]"


def render_vertical_bar(percent, height=8):
    """Vertical progress bar (like a histogram)"""
    filled = int(height * percent / 100)
    empty = height - filled
    
    bar = "██\n" * filled + "  \n" * empty
    return f"│{bar}|"


def render_road_trip(progress):
    """Road trip visualization - marker moving along road"""
    length = 40
    marker_pos = int(length * progress / 100)
    
    road = "┌" + "─" * length + "┐\n"
    road += "│" + " " * marker_pos + "🚗" + " " * (length - marker_pos - 1) + "│\n"
    road += "└" + "─" * length + "┘\n"
    road += "    START          " + f"{progress:.0f}%".ljust(8) + "END"
    return road


# Pre-defined ASCII arts for different states
WORKS_ASCII = """
    🔨 Mulai Kerja! 🔨
    ┏━━━━━━━━━━━━━━━━━━━┓
    ┃  💪 Fokus! Focus! ┃
    ┗━━━━━━━━━━━━━━━━━━━┛
"""

BREAK_ASCII = """
    ☕ Waktu Istirahat ☕
    ┏━━━━━━━━━━━━━━━━━━━┓
    ┃  🧘 Relax & Breathe ┃
    ┗━━━━━━━━━━━━━━━━━━━┛
"""

COMPLETE_ASCII = """
    ✅ SESSION SELESAI ✅
    ┏━━━━━━━━━━━━━━━━━━━┓
    ┃  🎉 GOOD JOB! 🎉  ┃
    ┗━━━━━━━━━━━━━━━━━━━┛
"""