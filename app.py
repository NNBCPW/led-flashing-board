import streamlit as st
import matplotlib.pyplot as plt
import imageio.v2 as imageio
import numpy as np
import io
import time

# --- LED Flashing Board (Side-by-Side Layout) ---

st.set_page_config(page_title="LED Flashing Board", layout="wide")

# --- Layout split ---
left, right = st.columns([1, 2])

# --- Global LED settings ---
dot_w, dot_h = 5, 7
dot_size = 0.8
rows, cols = 4, 10
char_space = 1.5
ON = "#f9ed32"
OFF = "#3b3c3d"
BG = "#141414"

# 5x7 LED font map
font = {
    "A": ["01110","10001","10001","11111","10001","10001","10001"],
    "B": ["11110","10001","11110","10001","10001","10001","11110"],
    "C": ["01110","10001","10000","10000","10000","10001","01110"],
    "D": ["11110","10001","10001","10001","10001","10001","11110"],
    "E": ["11111","10000","11110","10000","10000","10000","11111"],
    "F": ["11111","10000","11110","10000","10000","10000","10000"],
    "G": ["01110","10001","10000","10111","10001","10001","01110"],
    "H": ["10001","10001","11111","10001","10001","10001","10001"],
    "I": ["01110","00100","00100","00100","00100","00100","01110"],
    "J": ["00001","00001","00001","00001","10001","10001","01110"],
    "K": ["10001","10010","11100","10100","10010","10001","10001"],
    "L": ["10000","10000","10000","10000","10000","10000","11111"],
    "M": ["10001","11011","10101","10101","10001","10001","10001"],
    "N": ["10001","11001","10101","10011","10001","10001","10001"],
    "O": ["01110","10001","10001","10001","10001","10001","01110"],
    "P": ["11110","10001","10001","11110","10000","10000","10000"],
    "Q": ["01110","10001","10001","10001","10101","10010","01101"],
    "R": ["11110","10001","10001","11110","10100","10010","10001"],
    "S": ["01111","10000","10000","01110","00001","00001","11110"],
    "T": ["11111","00100","00100","00100","00100","00100","00100"],
    "U": ["10001","10001","10001","10001","10001","10001","01110"],
    "V": ["10001","10001","10001","10001","01010","01010","00100"],
    "W": ["10001","10001","10001","10101","10101","11011","10001"],
    "X": ["10001","01010","00100","00100","00100","01010","10001"],
    "Y": ["10001","01010","00100","00100","00100","00100","00100"],
    "Z": ["11111","00001","00010","00100","01000","10000","11111"],
    "0": ["01110","10001","10011","10101","11001","10001","01110"],
    "1": ["00100","01100","00100","00100","00100","00100","01110"],
    "2": ["01110","10001","00001","00010","00100","01000","11111"],
    "3": ["11110","00001","00001","01110","00001","00001","11110"],
    "4": ["00010","00110","01010","10010","11111","00010","00010"],
    "5": ["11111","10000","11110","00001","00001","10001","01110"],
    "6": ["01110","10000","11110","10001","10001","10001","01110"],
    "7": ["11111","00001","00010","00100","01000","01000","01000"],
    "8": ["01110","10001","10001","01110","10001","10001","01110"],
    "9": ["01110","10001","10001","01111","00001","00001","01110"],
    " ": ["00000","00000","00000","00000","00000","00000","00000"]
}


def render_scene(lines):
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    for row_idx, line in enumerate(lines):
        text = line[:cols].ljust(cols)
        for c_idx, ch in enumerate(text):
            char = font.get(ch, font[" "])
            x_offset = c_idx * (dot_w + char_space)
            y_offset = -(row_idx * (dot_h + char_space))
            for y in range(dot_h):
                for x in range(dot_w):
                    color = ON if char[y][x] == "1" else OFF
                    ax.add_patch(plt.Circle((x + x_offset, -y + y_offset), dot_size / 2, color=color))
    ax.set_xlim(-1, cols * (dot_w + char_space))
    ax.set_ylim(-rows * (dot_h + char_space) - 1, 3)
    ax.set_aspect("equal")
    return fig


# --- LEFT PANEL CONTROLS ---
with left:
    st.markdown("### 🎛️ LED Message Control")

    multi_scenes = st.checkbox("Enable multiple scenes")
    scene_time = st.slider("Scene duration (seconds)", 1, 10, 5)

    if not multi_scenes:
        line1 = st.text_input("Line 1", "").upper()
        line2 = st.text_input("Line 2", "").upper()
        line3 = st.text_input("Line 3", "").upper()
        line4 = st.text_input("Line 4", "").upper()
        current_scene = [line1, line2, line3, line4]
        scenes = [current_scene]
    else:
        scenes = []
        for i in range(1, 5):
            with st.expander(f"Scene {i}"):
                l1 = st.text_input(f"Scene {i} - Line 1", "").upper()
                l2 = st.text_input(f"Scene {i} - Line 2", "").upper()
                l3 = st.text_input(f"Scene {i} - Line 3", "").upper()
                l4 = st.text_input(f"Scene {i} - Line 4", "").upper()
                scenes.append([l1, l2, l3, l4])

    col1, col2 = st.columns(2)
    play = col1.button("▶️ Play Animation")
    download = col2.button("💾 Download GIF")

# --- RIGHT PANEL LIVE DISPLAY ---
with right:
    st.markdown("### 💡 LED Display Preview")

    if not multi_scenes:
        fig = render_scene(scenes[0])
        st.pyplot(fig)
    else:
        st.write("Preview of Scene 1")
        fig = render_scene(scenes[0])
        st.pyplot(fig)

# --- ANIMATION AND DOWNLOAD ---
if play or download:
    frames = []
    for s in scenes:
        fig = render_scene(s)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=150)
        buf.seek(0)
        frames.append(imageio.imread(buf))
        plt.close(fig)

    if play:
        img_slot = right.empty()
        for frame in frames:
            img_slot.image(frame, use_column_width=True)
            time.sleep(scene_time)

    if download and frames:
        gif_bytes = io.BytesIO()
        imageio.mimsave(gif_bytes, frames, format="GIF", duration=scene_time)
        st.download_button(
            label="Download Animated GIF",
            data=gif_bytes.getvalue(),
            file_name="led_flashing_message.gif",
            mime="image/gif"
        )
