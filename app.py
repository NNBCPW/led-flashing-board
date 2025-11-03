import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import io, imageio, time

# ---------------------------------------------------
# FAST LED FLASHING BOARD (Compact Window Layout)
# ---------------------------------------------------
st.set_page_config(page_title="LED Flashing Board", layout="wide")

# ---------- CONFIG ----------
LED_ON = (249, 237, 50)
LED_OFF = (59, 60, 61)
BG_COLOR = (20, 20, 20)

DOT_W, DOT_H = 5, 7
DOT_SIZE = 10
GAP = 4
PAD = 10
ROWS, COLS = 4, 10

# ---------- FONT MAP ----------
def mk(rows): return rows
font = {
    " ": mk(["00000","00000","00000","00000","00000","00000","00000"]),
    "A": mk(["01110","10001","11111","10001","10001","10001","10001"]),
    "B": mk(["11110","10001","11110","10001","10001","10001","11110"]),
    "C": mk(["01110","10001","10000","10000","10000","10001","01110"]),
    "D": mk(["11110","10001","10001","10001","10001","10001","11110"]),
    "E": mk(["11111","10000","11110","10000","10000","10000","11111"]),
    "F": mk(["11111","10000","11110","10000","10000","10000","10000"]),
    "G": mk(["01110","10001","10000","10111","10001","10001","01110"]),
    "H": mk(["10001","10001","11111","10001","10001","10001","10001"]),
    "I": mk(["01110","00100","00100","00100","00100","00100","01110"]),
    "J": mk(["00001","00001","00001","10001","10001","10001","01110"]),
    "K": mk(["10001","10010","11100","10100","10010","10001","10001"]),
    "L": mk(["10000","10000","10000","10000","10000","10000","11111"]),
    "M": mk(["10001","11011","10101","10101","10001","10001","10001"]),
    "N": mk(["10001","11001","10101","10011","10001","10001","10001"]),
    "O": mk(["01110","10001","10001","10001","10001","10001","01110"]),
    "P": mk(["11110","10001","11110","10000","10000","10000","10000"]),
    "Q": mk(["01110","10001","10001","10001","10101","10010","01101"]),
    "R": mk(["11110","10001","11110","10100","10010","10001","10001"]),
    "S": mk(["01111","10000","10000","01110","00001","00001","11110"]),
    "T": mk(["11111","00100","00100","00100","00100","00100","00100"]),
    "U": mk(["10001","10001","10001","10001","10001","10001","01110"]),
    "V": mk(["10001","10001","10001","01010","01010","00100","00100"]),
    "W": mk(["10001","10001","10101","10101","10101","11011","10001"]),
    "X": mk(["10001","01010","00100","00100","00100","01010","10001"]),
    "Y": mk(["10001","01010","00100","00100","00100","00100","00100"]),
    "Z": mk(["11111","00001","00010","00100","01000","10000","11111"]),
    "0": mk(["01110","10001","10011","10101","11001","10001","01110"]),
    "1": mk(["00100","01100","00100","00100","00100","00100","01110"]),
    "2": mk(["01110","10001","00001","00110","01000","10000","11111"]),
    "3": mk(["11110","00001","01110","00001","00001","00001","11110"]),
    "4": mk(["00010","00110","01010","10010","11111","00010","00010"]),
    "5": mk(["11111","10000","11110","00001","00001","10001","01110"]),
    "6": mk(["01110","10000","11110","10001","10001","10001","01110"]),
    "7": mk(["11111","00001","00010","00100","01000","01000","01000"]),
    "8": mk(["01110","10001","01110","10001","10001","10001","01110"]),
    "9": mk(["01110","10001","10001","01111","00001","00001","01110"]),
}

# ---------- DRAW ----------
def draw_char(draw, ch, x, y):
    pattern = font.get(ch.upper(), font[" "])
    for gy in range(DOT_H):
        for gx in range(DOT_W):
            color = LED_ON if pattern[gy][gx] == "1" else LED_OFF
            cx = x + gx * (DOT_SIZE + GAP)
            cy = y + gy * (DOT_SIZE + GAP)
            draw.ellipse([cx, cy, cx + DOT_SIZE, cy + DOT_SIZE], fill=color, outline=None)

def render_scene(lines):
    img_w = COLS * (DOT_W * (DOT_SIZE + GAP)) + PAD * 2
    img_h = ROWS * (DOT_H * (DOT_SIZE + GAP)) + PAD * 2
    im = Image.new("RGB", (img_w, img_h), BG_COLOR)
    d = ImageDraw.Draw(im)
    for row, line in enumerate(lines):
        text = (line or "").upper().ljust(COLS)[:COLS]
        for col, ch in enumerate(text):
            x = PAD + col * (DOT_W * (DOT_SIZE + GAP))
            y = PAD + row * (DOT_H * (DOT_SIZE + GAP))
            draw_char(d, ch, x, y)
    return im

# ---------- SIDEBAR ----------
st.sidebar.title("⚙️ LED Scene Settings")
use_scenes = st.sidebar.checkbox("Enable multiple scenes", value=False)
scene_time = st.sidebar.slider("Seconds per scene", 1, 10, 5)

# ---------- INPUTS ----------
scenes = []
if use_scenes:
    for s in range(1, 5):
        with st.sidebar.expander(f"Scene {s}"):
            lines = [
                st.text_input(f"Scene {s} - Line 1", key=f"s{s}_l1"),
                st.text_input(f"Scene {s} - Line 2", key=f"s{s}_l2"),
                st.text_input(f"Scene {s} - Line 3", key=f"s{s}_l3"),
                st.text_input(f"Scene {s} - Line 4", key=f"s{s}_l4"),
            ]
        scenes.append(lines)
else:
    with st.sidebar.expander("Message"):
        lines = [
            st.text_input("Line 1", key="l1"),
            st.text_input("Line 2", key="l2"),
            st.text_input("Line 3", key="l3"),
            st.text_input("Line 4", key="l4"),
        ]
        scenes = [lines]

# ---------- BUTTONS ----------
col1, col2 = st.columns([1, 1])
play = col1.button("▶ Play")
download = col2.button("💾 GIF")

# ---------- BOARD ----------
center_col = st.container()
board_placeholder = center_col.empty()
frames = [np.array(render_scene(lines)) for lines in scenes]

# ---------- DISPLAY INITIAL SCENE ----------
board_placeholder.image(frames[0], width=600)

# ---------- PLAYBACK ----------
if play:
    for img in frames:
        board_placeholder.image(img, width=600)
        time.sleep(scene_time)

# ---------- GIF ----------
if download:
    buf = io.BytesIO()
    imageio.mimsave(buf, frames, format="GIF", duration=scene_time)
    st.download_button("Download LED Animation", buf.getvalue(),
                       file_name="led_board.gif", mime="image/gif")

st.markdown("<hr><center>Compact LED Board by NN — Streamlit + PIL</center>", unsafe_allow_html=True)
