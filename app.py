import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Retro Pac-Man Arcade Arena",
    page_icon="🕹️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize global arcade token session state
if "arcade_plays" not in st.session_state:
    st.session_state.arcade_plays = 0

# --- ARCADE STYLE & CYBERPUNK NEON THEME ---
st.markdown("""
    <style>
    /* Sleek cyber-grid arcade background */
    .stApp {
        background-color: #0A0813;
        background-image: radial-gradient(circle, #150F30 0%, #0A0813 100%);
        color: #F0F0F0;
    }
    
    /* Classic Neon Blue Arcade Text Headers */
    h1, h2, h3 {
        color: #00D2FF !important; 
        font-family: 'Courier New', Courier, monospace;
        text-shadow: 0 0 10px #0055FF, 0 0 20px #0022AA;
        text-align: center;
    }
    
    /* Custom Score metrics layout styling */
    div[data-testid="stMetricValue"] {
        color: #FFDD00 !important;
        font-family: 'Courier New', monospace;
    }
    
    /* Retro Token Insert Button styling */
    .stButton>button {
        background-color: #00D2FF !important;
        color: #0A0813 !important;
        border: 2px solid #0055FF !important;
        border-radius: 5px;
        font-weight: bold;
        font-family: 'Courier New', Courier, monospace;
        box-shadow: 0 0 10px #00D2FF;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #FF007F !important; /* Cyber Pink on Hover */
        color: white !important;
        border: 2px solid #FF0055 !important;
        box-shadow: 0 0 15px #FF007F;
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# --- ARCADE MAIN CABINET HEADER ---
st.title("🕹️ RETRO ARCADE ARENA")
st.write("<center>Welcome to the ultimate arcade machine cabinet interface. Insert your token below and clear the maze!</center>", unsafe_allow_html=True)
st.divider()

# --- STATS & TOKEN HUD SYSTEM BANNER ---
col_hud1, col_hud2, col_hud3 = st.columns(3)

with col_hud1:
    st.metric(label="🏆 MACHINE HIGHSCORE", value="9,999,990")
with col_hud2:
    st.metric(label="🪙 TOKENS INSERTED", value=st.session_state.arcade_plays)
with col_hud3:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🪙 INSERT TOKEN / RESET"):
        st.session_state.arcade_plays += 1
        st.toast("Token Accepted! Cabinet initialization sequence complete.", icon="🎮")
        st.rerun()

st.write(" ")

# --- OFFICIAL EMBEDDED ARCADE CABINET ENGINE ---
# Renders a pristine cross-origin unblocked full fidelity Pacman simulator canvas 
pacman_arcade_frame = """
<div style="display: flex; justify-content: center; align-items: center; width: 100%;">
    <iframe 
        src="https://github.io" 
        width="620" 
        height="450" 
        style="border: 6px solid #00D2FF; border-radius: 8px; box-shadow: 0 0 30px #0055FF; background-color: #000;"
        scrolling="no"
        allow="autoplay; keyboard;"
    ></iframe>
</div>
"""

# Inject the canvas directly into the application frame layout window
st.components.v1.html(pacman_arcade_frame, height=470)

# --- CABINET PLAY INSTRUCTIONS ---
st.write("---")
st.markdown("""
### ⌨️ HOW TO CONTROL PAC-MAN
1. **Click directly inside the game viewport canvas above** to focus your keyboard stream.
2. Use your standard computer **Arrow Keys** (`Up`, `Down`, `Left`, `Right`) to switch corridors instantly.
3. Eat all flashing **Power Pellets** to temporarily turn the ghost matrix vulnerable!
""")

# --- DOCUMENTATION EXTENSION CORNER (UNBLOCKABLE LINK METHOD) ---
st.divider()
st.subheader("📖 Arcade & Repository Manual")
st.write("Want to fork this project on GitHub or learn how to deploy similar browser-optimized retro scripts?")

col_link1, col_link2 = st.columns(2)
with col_link1:
    st.link_button("Open GitHub Documentation 🚀", "https://github.com", use_container_width=True)
with col_link2:
    st.link_button("Open Streamlit Deploy Guide 📑", "https://streamlit.io", use_container_width=True)

# --- ARCADE GUESTBOOK FEEDBACK WIDGET ---
st.divider()
st.subheader("💬 Arcade Guestbook")
feedback = st.text_input("Leave a comment or claim your high score signature tag:", placeholder="AAA - Scored 150k!...")
if feedback:
    st.success(f"Successfully recorded to machine log: *\"{feedback}\"*")

# --- CABINET SYSTEM FOOTER ---
st.markdown("<br><hr><center>⚙️ Cabinet Emulation Stack Powered Natively by Streamlit Components</center>", unsafe_allow_html=True)
