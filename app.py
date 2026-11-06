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
        st.toast("Token Accepted! Cabinet initialization sequence complete.", icon="🕹️")
        st.rerun()

st.write(" ")

# --- NATIVE SELF-CONTAINED HTML5/JS PAC-MAN GAME ---
native_pacman_code = """
<div style="display: flex; flex-direction: column; align-items: center; background-color: #000; padding: 15px; border: 6px solid #00D2FF; border-radius: 8px; box-shadow: 0 0 30px #0055FF; width: 620px; margin: 0 auto;">
    <div style="color: #FFDD00; font-family: monospace; font-size: 20px; margin-bottom: 10px;">SCORE: <span id="score">0</span></div>
    <canvas id="gameCanvas" width="400" height="400" style="background-color: #111; border: 2px solid #0055FF;"></canvas>
    <div style="color: #666; font-family: monospace; font-size: 12px; margin-top: 10px;">Click screen & use Arrow Keys to play</div>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const scoreEl = document.getElementById("score");

const grid = 20;
let score = 0;

// Game entities
let pacman = { x: 200, y: 300, dx: 0, dy: 0, targetDx: 0, targetDy: 0 };
let ghost = { x: 200, y: 100, dx: 2, dy: 0 };

// Simulating simple map walls (boundaries & center blocks)
const walls = [
    {x: 0, y: 0, w: 400, h: 20}, {x: 0, y: 0, w: 20, h: 400},
    {x: 0, y: 380, w: 400, h: 20}, {x: 380, y: 0, w: 20, h: 400},
    {x: 80, y: 80, w: 80, h: 40}, {x: 240, y: 80, w: 80, h: 40},
    {x: 80, y: 240, w: 80, h: 40}, {x: 240, y: 240, w: 80, h: 40},
    {x: 160, y: 160, w: 80, h: 80}
];

// Generate food dots
let dots = [];
for (let r = 30; r < 380; r += 30) {
    for (let c = 30; c < 380; c += 30) {
        if (!checkWallCollision(c, r, 8, 8)) {
            dots.push({ x: c, y: r, eaten: false });
        }
    }
}

function checkWallCollision(x, y, w, h) {
    return walls.some(wall => x < wall.x + wall.w && x + w > wall.x && y < wall.y + wall.h && y + h > wall.y);
}

// Controls stream listener
window.addEventListener("keydown", e => {
    if (e.key === "ArrowLeft")  { pacman.targetDx = -2; pacman.targetDy = 0; }
    if (e.key === "ArrowRight") { pacman.targetDx = 2;  pacman.targetDy = 0; }
    if (e.key === "ArrowUp")    { pacman.targetDx = 0;  pacman.targetDy = -2; }
    if (e.key === "ArrowDown")  { pacman.targetDx = 0;  pacman.targetDy = 2; }
    if (["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"].includes(e.key)) e.preventDefault();
});

function loop() {
    requestAnimationFrame(loop);
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Apply Pacman Movement safely inside wall buffers
    if (!checkWallCollision(pacman.x + pacman.targetDx, pacman.y + pacman.targetDy, 16, 16)) {
        pacman.dx = pacman.targetDx;
        pacman.dy = pacman.targetDy;
    }
    if (!checkWallCollision(pacman.x + pacman.dx, pacman.y + pacman.dy, 16, 16)) {
        pacman.x += pacman.dx;
        pacman.y += pacman.dy;
    }

    // Basic Ghost tracking AI loop
    if (Math.random() < 0.02 || checkWallCollision(ghost.x + ghost.dx, ghost.y + ghost.dy, 16, 16)) {
        const dirs = [{x:2,y:0}, {x:-2,y:0}, {x:0,y:2}, {x:0,y:-2}];
        const validDirs = dirs.filter(d => !checkWallCollision(ghost.x + d.x, ghost.y + d.y, 16, 16));
        if (validDirs.length > 0) {
            let pick = validDirs[Math.floor(Math.random() * validDirs.length)];
            ghost.dx = pick.x; ghost.dy = pick.y;
        }
    }
    ghost.x += ghost.dx;
    ghost.y += ghost.dy;

    // Check food collision metrics
    dots.forEach(dot => {
        if (!dot.eaten && Math.hypot(pacman.x + 8 - dot.x, pacman.y + 8 - dot.y) < 12) {
            dot.eaten = true;
            score += 10;
            scoreEl.innerText = score;
        }
    });

    // Check game over ghost hit matrix
    if (Math.hypot(pacman.x - ghost.x, pacman.y - ghost.y) < 16) {
        score = 0;
        scoreEl.innerText = score;
        pacman.x = 200; pacman.y = 300; pacman.dx = 0; pacman.dy = 0;
        ghost.x = 200; ghost.y = 100;
        dots.forEach(d => d.eaten = false);
    }

    // Draw Map Walls
    ctx.fillStyle = "#0055FF";
    walls.forEach(w => ctx.fillRect(w.x, w.y, w.w, w.h));

    // Draw Food Dots
    ctx.fillStyle = "#FFBB00";
    dots.forEach(d => { if (!d.eaten) ctx.fillRect(d.x, d.y, 4, 4); });

    // Draw Ghost
    ctx.fillStyle = "#FF0000";
    ctx.beginPath(); ctx.arc(ghost.x + 8, ghost.y + 8, 8, 0, Math.PI * 2); ctx.fill();

    // Draw Pac-Man
    ctx.fillStyle = "#FFFF00";
    ctx.beginPath(); ctx.arc(pacman.x + 8, pacman.y + 8, 8, 0.2 * Math.PI, 1.8 * Math.PI);
    ctx.lineTo(pacman.x + 8, pacman.y + 8); ctx.fill();
}

loop();
</script>
"""

# Render the game frame cleanly without cross-origin URLs
st.components.v1.html(native_pacman_code, height=540)

# --- CABINET PLAY INSTRUCTIONS ---
st.write("---")
st.markdown("""
### ⌨️ HOW TO CONTROL PAC-MAN
1. **Click directly inside the canvas box grid above** to focus your keyboard controls.
2. Use your standard computer **Arrow Keys** (`Up`, `Down`, `Left`, `Right`) to navigate corridors instantly.
3. Eat all the gold food pellets and make sure to **dodge the red ghost**!
""")

# --- DOCUMENTATION LINK CORNER ---
st.divider()
st.subheader("📖 Arcade & Repository Manual")
st.write("Want to learn more about hosting standalone Python deployments?")

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
