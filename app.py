import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Classic Pac-Man Online Arcade",
    page_icon="🕹️",
    layout="centered"
)

# --- STYLE THE THEME ---
st.markdown("""
    <style>
    /* Spooky dark arcade background matching your theme */
    .stApp {
        background-color: #0F0C20;
        background-image: radial-gradient(circle, #1a0f30 0%, #0F0C20 100%);
        color: #E0E0E0;
    }
    
    /* Neon glowing arcade header */
    h1 {
        color: #FFBB00 !important;
        font-family: 'Courier New', Courier, monospace;
        text-shadow: 2px 2px 4px #000000, 0 0 15px #FF5E00;
        text-align: center;
    }
    
    /* Center the layout container */
    .arcade-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🕹️ Classic Pac-Man Arcade")
st.write("<center>Click inside the arcade screen below and use your <b>Arrow Keys</b> to play the official game!</center>", unsafe_allow_html=True)
st.divider()

# --- ARCADE EMBED ENGINE ---
# Using the high-availability Google Pac-Man full fidelity engine emulation mirror
pacman_html = """
<div style="display: flex; justify-content: center; align-items: center; width: 100%;">
    <iframe 
        src="https://github.io" 
        width="600" 
        height="450" 
        style="border: 4px solid #FF5E00; border-radius: 15px; box-shadow: 0 0 20px #9D00FF; background-color: #000;"
        scrolling="no"
        allow="autoplay; keyboard;"
    ></iframe>
</div>
"""

# Render the game frame securely
st.components.v1.html(pacman_html, height=480)

# --- FOOTER ---
st.markdown("<br><hr><center>🕹️ Use Left/Right/Up/Down Arrow keys to steer Pac-Man</center>", unsafe_allow_html=True)
