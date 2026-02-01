import pygame
import time
import sys
import wave
import threading
import tkinter as tk
from tkinter import messagebox
import random
import webbrowser
import os

# ----------------- SETUP -----------------
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Media Player")
clock = pygame.time.Clock()

# ----------------- LOAD FRAMES -----------------
frame1 = pygame.transform.scale(
    pygame.image.load("frame.png").convert(), (WIDTH, HEIGHT)
)
frame2 = pygame.transform.scale(
    pygame.image.load("frame2.png").convert(), (WIDTH, HEIGHT)
)

# ----------------- CREATE CRASH SOUND -----------------
def create_crash_sound(source, out, start_sec=12.3, length_sec=0.08):
    with wave.open(source, "rb") as src:
        params = src.getparams()
        framerate = src.getframerate()
        src.setpos(int(start_sec * framerate))
        frames = src.readframes(int(length_sec * framerate))
    with wave.open(out, "wb") as dst:
        dst.setparams(params)
        dst.writeframes(frames)

create_crash_sound("daisy_bell.wav", "crash.wav")

normal_sound = pygame.mixer.Sound("daisy_bell.wav")
crash_sound = pygame.mixer.Sound("crash.wav")

# ----------------- SAFE GLITCH -----------------
def glitch_surface(surface):
    glitch = surface.copy()

    for _ in range(random.randint(6, 12)):
        y = random.randint(0, HEIGHT - 10)
        h = random.randint(4, 12)
        offset = random.randint(-40, 40)

        src_x = max(0, -offset)
        dst_x = max(0, offset)
        width = WIDTH - abs(offset)

        if width <= 0:
            continue

        strip = surface.subsurface((src_x, y, width, h)).copy()
        glitch.blit(strip, (dst_x, y))

    return glitch

# ----------------- POPUP -----------------
def error_popup():
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Fehler",
        "Dieses Programm wurde gelöscht.\n\n"
        "Bitte installieren Sie es nie wieder!!!!!\n\n"
        "Fehlercode: Unbekannt"
    )
    root.destroy()

# ----------------- REALTIME TXT -----------------
def write_realtime(path, text, duration=60):
    delay = duration / len(text)
    with open(path, "w", encoding="utf-8") as f:
        for ch in text:
            f.write(ch)
            f.flush()
            time.sleep(delay)

# ----------------- STATES -----------------
clicked = False
crashed = False
start_time = None
freeze_start = None
glitch_frame = None

# Bewegung für frame2
frame2_x = 0
frame2_y = 0
move_speed_x = 2
move_speed_y = 1

# ----------------- MAIN LOOP -----------------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT and not crashed:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and not clicked:
            clicked = True
            start_time = time.time()
            normal_sound.play()

    if not clicked:
        screen.blit(frame1, (0, 0))

    else:
        if time.time() - start_time > 5 and not crashed:
            crashed = True
            normal_sound.stop()
            crash_sound.play(-1)
            freeze_start = time.time()

            glitch_frame = glitch_surface(frame2)
            frame2_x = 0
            frame2_y = 0

            threading.Thread(target=error_popup, daemon=True).start()
            threading.Thread(
                target=write_realtime,
                args=("README.txt", "I SEE YOU", 60),
                daemon=True
            ).start()

        if not crashed:
            screen.blit(frame1, (0, 0))
        else:
            # Bewegung aktualisieren
            frame2_x += move_speed_x
            frame2_y += move_speed_y

            # Wenn aus dem Bild raus → wieder rein
            if frame2_x > WIDTH:
                frame2_x = -WIDTH
            if frame2_y > HEIGHT:
                frame2_y = -HEIGHT

            screen.blit(glitch_frame, (frame2_x, frame2_y))

            if time.time() - freeze_start > 60:
                pygame.quit()
                path = os.path.abspath("frame3.html")
                webbrowser.open(f"file:///{path}")
                sys.exit()

    pygame.display.flip()
    clock.tick(60)
