import streamlit as st
import random

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Pac-Man 67 Arcade Room",
    page_icon="🕹️",
    layout="centered"
)

# --- INITIALIZE ENGINE STATE ---
if "pm_x" not in st.session_state:
    st.session_state.pm_x = 2
if "pm_y" not in st.session_state:
    st.session_state.pm_y = 2
if "ghost_x" not in st.session_state:
    st.session_state.ghost_x = random.randint(0, 4)
if "ghost_y" not in st.session_state:
    st.session_state.ghost_y = random.randint(0, 4)
if "is_super_mode" not in st.session_state:
    st.session_state.is_super_mode = False
if "super_mode_timer" not in st.session_state:
    st.session_state.super_mode_timer = 0
if "pm_score" not in st.session_state:
    st.session_state.pm_score = 0
if "orbs_active" not in st.session_state:
    st.session_state.orbs_active = {"Orb1": True, "Orb2": True, "Orb3": True, "Orb4": True}
if "pm_game_over" not in st.session_state:
    st.session_state.pm_game_over = False

# --- HEADER ---
st.title("🕹️ Classic Pac-Man 67")
st.write("Navigate the matrix board, eat power orbs, and chase down the ghost!")
st.divider()

# --- GAME SYSTEM LOGIC ---
if st.session_state.pm_game_over:
    st.error("💀 GAME OVER! The Ghost caught you in normal mode.")
    if st.button("🎮 Insert Coin to Retry"):
        st.session_state.pm_x, st.session_state.pm_y = 2, 2
        st.session_state.ghost_x, st.session_state.ghost_y = random.randint(0, 4), random.randint(0, 4)
        st.session_state.is_super_mode = False
        st.session_state.orbs_active = {"Orb1": True, "Orb2": True, "Orb3": True, "Orb4": True}
        st.session_state.pm_score = 0
        st.session_state.pm_game_over = False
        st.rerun()
else:
    # Handle Super Mode step counter limits
    if st.session_state.is_super_mode:
        st.session_state.super_mode_timer -= 1
        if st.session_state.super_mode_timer <= 0:
            st.session_state.is_super_mode = False
            st.toast("⚡ Super Mode Expired!", icon="⏳")

    # Display HUD Stats Banner
    col_hud1, col_hud2 = st.columns(2)
    with col_hud1:
        st.metric(label="🌟 Current Score", value=st.session_state.pm_score)
    with col_hud2:
        if st.session_state.is_super_mode:
            st.warning(f"⚡ SUPER MODE: {st.session_state.super_mode_timer} Steps Left")
        else:
            st.info("Status: Normal Mode")

    # Build 5x5 Matrix Screen View 
    grid = [["▪️" for _ in range(5)] for _ in range(5)]
    
    # Render active corner Power Orbs
    if st.session_state.orbs_active["Orb1"]: grid[0][0] = "🔮"
    if st.session_state.orbs_active["Orb2"]: grid[0][4] = "🔮"
    if st.session_state.orbs_active["Orb3"]: grid[4][0] = "🔮"
    if st.session_state.orbs_active["Orb4"]: grid[4][4] = "🔮"
    
    # Render Ghost based on active threat vulnerability color
    ghost_icon = "🟢" if not st.session_state.is_super_mode else "💙"
    grid[st.session_state.ghost_y][st.session_state.ghost_x] = ghost_icon
    
    # Render Pac-Man Player
    grid[st.session_state.pm_y][st.session_state.pm_x] = "🟡" if not st.session_state.is_super_mode else "⚡"

    # Draw Matrix Layout Board on Streamlit Display
    for row in grid:
        st.subheader("  ".join(row))

    # --- CONTROLLER INTERFACE ---
    st.write("---")
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns(4)
    moved = False

    with ctrl_col1:
        if st.button("◀️ Button A (Left)") and st.session_state.pm_x > 0:
            st.session_state.pm_x -= 1
            moved = True
    with ctrl_col2:
        if st.button("▶️ Button B (Right)") and st.session_state.pm_x < 4:
            st.session_state.pm_x += 1
            moved = True
    with ctrl_col3:
        if st.button("🔽 Button A+B (Down)") and st.session_state.pm_y < 4:
            st.session_state.pm_y += 1
            moved = True
    with ctrl_col4:
        if st.button("🔼 Logo Touch (Up)") and st.session_state.pm_y > 0:
            st.session_state.pm_y -= 1
            moved = True

    if moved:
        # Ghost random movement generator engine
        gg = random.randint(1, 4)
        if gg == 1 and st.session_state.ghost_x < 4: st.session_state.ghost_x += 1
        elif gg == 2 and st.session_state.ghost_x > 0: st.session_state.ghost_x -= 1
        elif gg == 3 and st.session_state.ghost_y < 4: st.session_state.ghost_y += 1
        elif gg == 4 and st.session_state.ghost_y > 0: st.session_state.ghost_y -= 1

        # Check Power Orb Collection Conditions
        if st.session_state.pm_x == 0 and st.session_state.pm_y == 0 and st.session_state.orbs_active["Orb1"]:
            st.session_state.orbs_active["Orb1"] = False
            st.session_state.is_super_mode = True
            st.session_state.super_mode_timer = 10
            st.toast("Super Power Unlocked! ⚡")
        elif st.session_state.pm_x == 4 and st.session_state.pm_y == 0 and st.session_state.orbs_active["Orb2"]:
            st.session_state.orbs_active["Orb2"] = False
            st.session_state.is_super_mode = True
            st.session_state.super_mode_timer = 10
            st.toast("Super Power Unlocked! ⚡")
        elif st.session_state.pm_x == 0 and st.session_state.pm_y == 4 and st.session_state.orbs_active["Orb3"]:
            st.session_state.orbs_active["Orb3"] = False
            st.session_state.is_super_mode = True
            st.session_state.super_mode_timer = 10
            st.toast("Super Power Unlocked! ⚡")
        elif st.session_state.pm_x == 4 and st.session_state.pm_y == 4 and st.session_state.orbs_active["Orb4"]:
            st.session_state.orbs_active["Orb4"] = False
            st.session_state.is_super_mode = True
            st.session_state.super_mode_timer = 10
            st.toast("Super Power Unlocked! ⚡")

        # Handle Object Overlaps / Collisions 
        if st.session_state.pm_x == st.session_state.ghost_x and st.session_state.pm_y == st.session_state.ghost_y:
            if st.session_state.is_super_mode:
                st.session_state.pm_score += 10
                st.toast("Chased the Ghost! +10 Points 👻")
                st.session_state.ghost_x = random.randint(0, 4)
                st.session_state.ghost_y = random.randint(0, 4)
            else:
                st.session_state.pm_game_over = True
        
        st.rerun()

    if st.button("🔄 Full System Reset"):
        st.session_state.pm_x, st.session_state.pm_y = 2, 2
        st.session_state.ghost_x, st.session_state.ghost_y = random.randint(0, 4), random.randint(0, 4)
        st.session_state.is_super_mode = False
        st.session_state.orbs_active = {"Orb1": True, "Orb2": True, "Orb3": True, "Orb4": True}
        st.session_state.pm_score = 0
        st.session_state.pm_game_over = False
        st.rerun()
