#!/usr/bin/env python3
"""
Finger Tracking with Visual Effects 🤏
Real-time finger tracking from webcam with colorful effects

Requirements:
    pip install opencv-python mediapipe numpy

Usage:
    python3 tracker.py
"""

import cv2
import mediapipe as mp
import numpy as np
from collections import deque
from typing import List, Tuple

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Color palette for different fingers (BGR format)
FINGER_COLORS = {
    "thumb": (255, 0, 0),      # Blue - Thumb
    "index": (0, 255, 0),      # Green - Index
    "middle": (0, 0, 255),     # Red - Middle
    "ring": (255, 255, 0),     # Cyan - Ring
    "pinky": (255, 0, 255),    # Magenta - Pinky
}

# Finger tip landmark indices (MediaPipe)
FINGER_TIPS = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
FINGER_NAMES = ["thumb", "index", "middle", "ring", "pinky"]

# Trail configuration
TRAIL_MAX_POINTS = 32
particle_count = 15

# Modes
modes = {
    1: "track",       # Finger tracking with color
    2: "trail",       # Trail effect
    3: "particle",    # Particle effect
    4: "paint",       # Virtual paint
    5: "normal"
}


def draw_colored_fingers(img: np.ndarray, landmarks) -> None:
    """Draw each finger tip with its own color"""
    h, w, _ = img.shape
    
    for name, idx in zip(FINGER_NAMES, FINGER_TIPS):
        cx = int(landmarks[idx].x * w)
        cy = int(landmarks[idx].y * h)
        color = FINGER_COLORS.get(name, (255, 255, 255))
        
        # Draw finger tip
        cv2.circle(img, (cx, cy), 15, color, -1)
        cv2.circle(img, (cx, cy), 5, (255, 255, 255), -1)
        cv2.circle(img, (cx, cy), 2, (0, 0, 0), -1)


def draw_trail(img: np.ndarray, points: deque, color: Tuple[int, int, int]) -> None:
    """Draw a trail effect from points"""
    if len(points) < 2:
        return
    
    points_list = list(points)
    for i in range(1, len(points_list)):
        pt1, pt2 = points_list[i-1], points_list[i]
        thickness = int(10 * (1 - i / len(points_list)))
        cv2.line(img, pt1, pt2, color, thickness)


def draw_particles(img: np.ndarray, center: Tuple[int, int]) -> None:
    """Draw particle burst at center position"""
    cx, cy = center
    h, w = img.shape[:2]
    
    for _ in range(particle_count):
        angle = np.random.uniform(0, 2 * np.pi)
        distance = np.random.uniform(20, 80)
        px = int(cx + distance * np.cos(angle))
        py = int(cy + distance * np.sin(angle))
        
        if 0 <= px < w and 0 <= py < h:
            color = tuple(np.random.randint(100, 255, 3).tolist())
            radius = np.random.randint(2, 6)
            cv2.circle(img, (px, py), radius, color, -1)


def draw_virtual_canvas(img: np.ndarray, landmarks) -> None:
    """Virtual paint canvas - index finger as stamp tool"""
    h, w = img.shape[:2]
    
    # Get index finger tip position
    idx_x = int(landmarks[8].x * w)
    idx_y = int(landmarks[8].y * h)
    
    # Draw circular stamp
    cv2.circle(img, (idx_x, idx_y), 30, (255, 255, 255), -1)
    cv2.circle(img, (idx_x, idx_y), 30, (0, 0, 0), 1)


def detect_fingers_up(landmarks) -> List[int]:
    """Detect which fingers are up (binary: 0=down, 1=up)"""
    finger_states = []
    
    # Non-thumb fingers (index, middle, ring, pinky)
    for i, tip_idx in enumerate([8, 12, 16, 20]):
        mcp_idx = tip_idx - 4  # MCP joint
        if landmarks[tip_idx].y < landmarks[mcp_idx].y:
            finger_states.append(1)  # Up
        else:
            finger_states.append(0)  # Down
    
    # Thumb (different logic - compare x position)
    if landmarks[4].x > landmarks[3].x:
        finger_states.insert(0, 1)  # Thumb up to the right
    else:
        finger_states.insert(0, 0)
    
    return finger_states


def main():
    """Main application loop"""
    
    print("=" * 50)
    print("  FINGER TRACKING WITH VISUAL EFFECTS")
    print("=" * 50)
    print("\n[TOMBOL KONTROL]")
    print("1 = Track (colored fingers)")
    print("2 = Trail effect")
    print("3 = Particle effect")
    print("4 = Virtual paint")
    print("5 = Normal tracking")
    print("q = Quit")
    print("=" * 50)
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ ERROR: Tidak bisa mengakses webcam!")
        return
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Trail buffers for smooth trails
    trail_history = {
        "index": deque(maxlen=TRAIL_MAX_POINTS),
        "thumb": deque(maxlen=TRAIL_MAX_POINTS),
    }
    
    # Current mode state
    current_mode = "track"
    
    # Hands detector
    with mp_hands.Hands(
        model_complexity=1,
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.6
    ) as hands:
        
        while True:
            # Read frame
            success, frame = cap.read()
            if not success:
                print("❌ Frame read error")
                continue
            
            # Flip horizontal for mirror effect
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process hands
            results = hands.process(rgb_frame)
            
            # Mode info overlay
            cv2.putText(
                frame, f"Mode: {current_mode.upper()}",
                (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                (0, 255, 0), 2, cv2.LINE_AA
            )
            
            if results.multi_hand_landmarks:
                for hand_landmarks, handedness in zip(
                    results.multi_hand_landmarks,
                    results.multi_handedness
                ):
                    landmarks = hand_landmarks.landmark
                    h, w, _ = frame.shape
                    
                    # Get finger positions
                    idx_x = int(landmarks[8].x * w)
                    idx_y = int(landmarks[8].y * h)
                    thumb_x = int(landmarks[4].x * w)
                    thumb_y = int(landmarks[4].y * h)
                    
                    # Update trail history
                    trail_history["index"].append((idx_x, idx_y))
                    trail_history["thumb"].append((thumb_x, thumb_y))
                    
                    # Execute mode-specific effects
                    if current_mode == "track":
                        draw_colored_fingers(frame, landmarks)
                    
                    elif current_mode == "trail":
                        draw_trail(frame, trail_history["index"], FINGER_COLORS["index"])
                        draw_trail(frame, trail_history["thumb"], FINGER_COLORS["thumb"])
                        draw_colored_fingers(frame, landmarks)
                    
                    elif current_mode == "particle":
                        center = ((idx_x + thumb_x) // 2, (idx_y + thumb_y) // 2)
                        draw_particles(frame, center)
                        draw_colored_fingers(frame, landmarks)
                    
                    elif current_mode == "paint":
                        draw_virtual_canvas(frame, landmarks)
                    
                    elif current_mode == "normal":
                        # Just draw hand connections
                        mp_drawing.draw_landmarks(
                            frame, hand_landmarks,
                            mp_hands.HAND_CONNECTIONS,
                            mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2),
                            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1)
                        )
                    
                    # Display hand label
                    label = handedness.classification[0].label
                    label_color = (0, 255, 0) if label == "Right" else (0, 0, 255)
                    cv2.putText(
                        frame, f"Hand: {label}",
                        (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        label_color, 2, cv2.LINE_AA
                    )
            
            # Show result
            cv2.imshow("Finger Tracking Effects", frame)
            
            # Keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\n👋 Terima kasih sudah main! Sampai jumpa!")
                break
            elif key in range(49, 54):  # Keys 1-5
                mode_name = modes.get(key - 48, "track")
                current_mode = mode_name
                print(f"✅ Mode: {mode_name}")
            
            # Exit condition
            if cv2.getWindowProperty("Finger Tracking Effects", cv2.WND_PROP_VISIBLE) < 1:
                break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()