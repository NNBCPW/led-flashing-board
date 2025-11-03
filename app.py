import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import io, imageio, time

# ---------------------------------------------------
# COMPACT LED BOARD — 7x5 TILES, FAINT GAPS, SCENES
# ---------------------------------------------------
st.set_page_config(page_title="LED Board (Tiles)", layout="wide")

# ---------- COLORS ----------
LED_ON      = (249, 237, 50)   # center yellow you gave
LED_OFF     = (59, 60, 61)     # off dot dark gray
BG_COLOR    = (20, 20, 20)     # page/canvas background
GAP_LINE    = (34, 34, 34)     # very faint gray between tiles (subtle)

# ---------- GRID / TILE GEOMETRY ----------
ROWS, COLS = 4, 10       # 4 rows of characters, 10 chars per row
DOT_W, DOT_H = 5, 7      # each character is 5x7 dots

DOT_SIZE  = 10           # diameter of a single dot (px)
DOT_GAP   = 4            # spacing between dots (px) within a tile
TILE_PAD  = 6            # inner padding inside each tile around dots (px)
TILE_GAP  = 6            # faint gap between tiles (px)
OUTER_PAD = 10           # outer padding around whole board (px)

DISPLAY_WIDTH = 640      # target display width in Streamlit (keeps it compact)

# ---------- 5x7 FONT ----------
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

# ---------- TILE SIZE HELPERS ----------
def tile_inner_w():  # dots row width
    return DOT_W * DOT_SIZE + (DOT_W - 1) * DOT_GAP

def tile_inner_h():  # dots col height
    return DOT_H * DOT_SIZE + (DOT_H - 1) * DOT_GAP

def tile_w():        # full tile including inner pad
    return tile_inner_w() + TILE_PAD * 2

def tile_h():        # full tile including inner pad
    return tile_inner_h() + TILE_PAD * 2

def board_w():
    return OUTER_PAD * 2 + COLS * tile_w() + (COLS - 1) * TILE_GAP

def board_h():
    return OUTER_PAD * 2 + ROWS * tile_h() + (ROWS - 1) * TILE_GAP

# ---------- DRAW ONE CHARACTER TILE ----------
def draw_char_tile(draw, ch, top_left_x, top_left_y):
    # faint gap lines: draw a subtle rectangle outline (nearly BG)
    draw.rectangle(
        [top_left_x - TILE_GAP/2, top_left_y - TILE_GAP/2,
         top_left_x + tile_w() + TILE_GAP/2, top_left_y + tile_h() + TILE_GAP/2],
        outline=GAP_LINE, width=1
    )

    # draw dots inside the tile
    pattern = font.get(ch.upper(), font[" "])
    start_x = top_left_x + TILE_PAD
    start_y = top_left_y + TILE_PAD
    for gy in range(DOT_H):
        for gx in range(DOT_W):
            color = LED_ON if pattern[gy][gx] == "1" else LED_OFF
            cx = start_x + gx * (DOT_SIZE + DOT_GAP)
            cy = start_y + gy * (DOT_SIZE + DOT_GAP)
            draw.ellipse([cx, cy, cx + DOT_SIZE, cy + DOT_SIZE], fill=color, outline=None)

# ---------- RENDER A SCENE (4 lines) ----------
def render_scene(lines):
    W, H = board_w(), board_h()
    im = Image.new("RGB", (W, H), BG_COLOR)
    d = ImageDraw.Draw(im)

    for r, line in enumerate(lines):
        text = (line or "").upper().ljust(COLS)[:COLS]
        for c, ch in enumerate(text):
            x = OUTER_PAD + c * (tile_w() + TILE_GAP)
            y = OUTER_PAD + r * (tile_h() + TILE_GAP)
            draw_char_tile(d, ch, x, y)
    return im

# ---------- SIDEBAR (compact controls) ----------
st.sidebar.title("⚙️ LED Scene Settings")
use_scenes  = st.sidebar.checkbox("Enable multiple scenes", value=False)
scene_time  = st.sidebar.slider("Seconds per scene", 1, 10, 5)

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

# ---------- ACTIONS ----------
col1, col2 = st.columns([1, 1])
play     = col1.button("▶ Play")
download = col2.button("💾 GIF")

# ---------- RENDER FIRST / PREVIEW ----------
frames = [np.array(render_scene(lines)) for lines in scenes]
board_placeholder = st.empty()
board_placeholder.image(frames[0], width=DISPLAY_WIDTH)

# ---------- PLAYBACK ----------
if play:
    for img in frames:
        board_placeholder.image(img, width=DISPLAY_WIDTH)
        time.sleep(scene_time)

# ---------- GIF DOWNLOAD ----------
if download:
    buf = io.BytesIO()
    imageio.mimsave(buf, frames, format="GIF", duration=scene_time)
    st.download_button("Download LED Animation", buf.getvalue(),
                       file_name="led_board.gif", mime="image/gif")

st.markdown(
    "<hr><center>LED Board — 7×5 Tiles • Compact • Scenes • GIF • Streamlit + PIL</center>",
    unsafe_allow_html=True
)
