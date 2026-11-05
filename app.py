import streamlit as st
import random
import time

# --- PAGE CONFIG & THEME ---
st.set_page_config(
    page_title="The Haunted Streamlit Mansion",
    page_icon="🎃",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize Session State tracking for Easter Eggs and Game States
if "egg_porch" not in st.session_state:
    st.session_state.egg_porch = False
if "egg_story" not in st.session_state:
    st.session_state.egg_story = False
if "egg_candy" not in st.session_state:
    st.session_state.egg_candy = False
if "draw_count" not in st.session_state:
    st.session_state.draw_count = 0
if "ghost_dimension_unlocked" not in st.session_state:
    st.session_state.ghost_dimension_unlocked = False
if "graveyard_finished" not in st.session_state:
    st.session_state.graveyard_finished = False
if "arcade_unlocked" not in st.session_state:
    st.session_state.arcade_unlocked = False

# Custom CSS for Halloween Vibe & Animations
st.markdown("""
    <style>
    /* Dark, spooky background and neon accents */
    .stApp {
        background-color: #0F0C20;
        background-image: radial-gradient(circle, #241442 0%, #0F0C20 100%);
        color: #E0E0E0;
    }
    
    /* Custom Headers */
    h1, h2, h3 {
        color: #FF5E00 !important; /* Halloween Orange */
        font-family: 'Courier New', Courier, monospace;
        text-shadow: 2px 2px 4px #000000, 0 0 10px #9D00FF;
    }
    
    /* Spooky glowing buttons */
    .stButton>button {
        background-color: #9D00FF !important;
        color: white !important;
        border: 2px solid #FF5E00 !important;
        border-radius: 10px;
        font-weight: bold;
        box-shadow: 0 0 8px #9D00FF;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FF5E00 !important;
        border: 2px solid #9D00FF !important;
        box-shadow: 0 0 15px #FF5E00;
        transform: scale(1.05);
    }
    
    /* Floating Ghost Animation */
    @keyframes float {
        0% { transform: translate(0, 0px); }
        50% { transform: translate(0, -15px); }
        100% { transform: translate(0, 0px); }
    }
    .ghost-style {
        font-size: 50px;
        animation: float 3s ease-in-out infinite;
        text-align: center;
        margin-bottom: -10px;
    }
    </style>
""", unsafe_allow_html=True)

# Check if all Easter Eggs are found
all_eggs_found = st.session_state.egg_porch and st.session_state.egg_story and st.session_state.egg_candy

# Unblockable Native Browser Speech Generator with Voice Modifiers
def speak_like_a_monster(text, pitch, rate):
    js_html = f"""
    <script>
    (function() {{
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel(); 
            var msg = new SpeechSynthesisUtterance("{text}");
            msg.pitch = {pitch}; 
            msg.rate = {rate};   
            window.speechSynthesis.speak(msg);
        }}
    }})();
    </script>
    """
    st.components.v1.html(js_html, height=0)

# --- HEADER & FLOATING GHOST EASTER EGG TRACKING ---
st.markdown("<div class='ghost-style'>👻</div>", unsafe_allow_html=True)

if all_eggs_found and not st.session_state.ghost_dimension_unlocked:
    if st.button("✨ The Floating Ghost is glowing! CLICK ME! ✨", use_container_width=True):
        st.session_state.ghost_dimension_unlocked = True
        st.toast("The air grows cold... The Haunted Graveyard has opened in the sidebar!", icon="🔮")
        st.rerun()

st.title("🎃 The Haunted Streamlit Mansion 💀")

# Menu routing logic setup
menu_options = ["🚪 Front Porch", "📖 Spooky Story Generator", "🍬 Trick or Treat Roulette", "🔮 Monster Mash Soundboard"]
if st.session_state.ghost_dimension_unlocked:
    menu_options.append("🌌 Haunted Graveyard")
if st.session_state.arcade_unlocked:
    menu_options.append("🕹️ Pac-Man Arcade")

page = st.sidebar.selectbox("Choose Your Activity:", menu_options)

# --- PAGE 1: FRONT PORCH ---
if page == "🚪 Front Porch":
    st.header("Welcome to the Mansion")
    st.image("https://unsplash.com", 
             caption="The fog rolls in...", use_container_width=True)
    
    # Hide inputs once respect is fully earned
    if not st.session_state.arcade_unlocked:
        secret_knock = st.text_input("Psst... do you know the secret pass-phrase?", placeholder="Type here...")
        if secret_knock.lower() == "neon mint":
            if not st.session_state.egg_porch:
                st.session_state.egg_porch = True
                st.rerun()
        
        if st.session_state.egg_porch:
            st.success("🌟 EASTER EGG UNLOCKED: The walls glow bright in green (#05f7bf)!")
    
    if st.button("Knock on the Door 🚪"):
        with st.spinner("Knocking..."):
            time.sleep(1)
        
        if st.session_state.graveyard_finished:
            st.session_state.arcade_unlocked = True
            st.rerun()
        else:
            st.error("A disembodied voice whispers: *'Who dares disturb the mansion?!'*")
            speak_like_a_monster("Who dares disturb the mansion?!", 0.2, 0.8)

    # Celebratory HUD view instantly triggered right after nice greeting
    if st.session_state.arcade_unlocked:
        st.success("👑 The monster bows deeply and whispers: 'Welcome back, Master Explorer. I respect your legendary bravery. Your Arcade prize is unlocked inside the sidebar!'")
        st.snow()

# --- PAGE 2: SPOOKY STORY GENERATOR ---
elif page == "📖 Spooky Story Generator":
    st.header("📜 Create Your Own Spooky Tale")
    col1, col2 = st.columns(2)
    with col1:
        protagonist = st.text_input("Main Character's Name", value="Brave Traveler")
        adjective = st.text_input("Spooky Adjective", value="slimy")
        creature = st.text_input("Monster/Creature", value="Shadow Beast")
    with col2:
        place = st.text_input("Creepy Place", value="The Graveyard")
        object_held = st.text_input("An Object", value="Flashlight")
        exclamation = st.text_input("Scared Exclamation", value="Help me!")

    if protagonist.lower() == "goofy gang":
        if not st.session_state.egg_story:
            st.session_state.egg_story = True
            st.rerun()

    if st.session_state.egg_story:
        st.warning("👾 EASTER EGG UNLOCKED: Welcome to the official Goofy Gang sanctuary portal! 🚀")

    if st.button("🔮 Conjure Story"):
        story = f"It was a dark and stormy night at **{place}**. **{protagonist}** was minding their own business when a **{adjective}** **{creature}** burst out!"
        st.info(story)

# --- PAGE 3: TRICK OR TREAT ROULETTE ---
elif page == "🍬 Trick or Treat Roulette":
    st.header("🍬 Trick or Treat Roulette")
    if st.button("🎃 Draw from the Bowl 🍬"):
        st.session_state.draw_count += 1
        if st.session_state.draw_count >= 5:
            if not st.session_state.egg_candy:
                st.session_state.egg_candy = True
                st.rerun()
            
        outcomes = [{"type": "Treat", "text": "You got a King-Sized Peanut Butter Cup! 🍫", "icon": "🎉"}]
        result = random.choice(outcomes)
        st.success(result["text"])

    if st.session_state.egg_candy:
        st.warning("💀 EASTER EGG UNLOCKED: You found the hidden golden skull token down at the bottom of the bowl!")

# --- PAGE 4: MONSTER MASH SOUNDBOARD ---
elif page == "🔮 Monster Mash Soundboard":
    st.header("🎵 The Monster Mash Board")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🐺 Werewolf"):
            speak_like_a_monster("Ah-wwooooo! Ow-ow-ow-wwoooo! Grrrr.", 0.2, 0.7)
    with c2:
        if st.button("🧛 Vampire"):
            speak_like_a_monster("Mwahahahahaha! Ahahahaha!", 0.5, 0.85)
    with c3:
        if st.button("🧟 Zombie"):
            speak_like_a_monster("Uuuuuurrrrgh. Grrrrroaaaannn. Hhhhungggerrr.", 0.1, 0.4)

# --- SECRET PAGE 5: HAUNTED GRAVEYARD ---
elif page == "🌌 Haunted Graveyard" and st.session_state.ghost_dimension_unlocked:
    st.header("🌌 Secret Zone: The Haunted Graveyard")
    st.write("The spirits rise from the catacombs. Finish the final trial to confront the master!")
    
    if st.button("🔮 Summon The Grand Phantom Presence"):
        speak_like_a_monster("WwooooooOooooo. You have finished the graveyard challenge. Return to the porch to face the master.", 1.2, 0.7)
        st.session_state.graveyard_finished = True
        st.success("The Grand Phantom whispers: 'The challenge is complete! Go back to the front porch and knock on the door.' 👑")

# --- UNLOCKED BONUS PAGE 6: FULL CLASSIC PAC-MAN SITE ARCADE ---
elif page == "🕹️ Pac-Man Arcade" and st.session_state.arcade_unlocked:
    st.header("🕹️ Retro Pac-Man Arcade Arena")
    st.write("<center>Click inside the arcade frame and use your computer <b>Arrow Keys</b> to play!</center>", unsafe_allow_html=True)
    
    # Safe Cross-Origin cloud-optimized deployment frame mirror
    pacman_embed_html = """
    <div style="display: flex; justify-content: center; align-items: center; width: 100%;">
        <iframe 
            src="https://github.io" 
            width="620" 
            height="450" 
            style="border: 4px solid #FFBB00; border-radius: 15px; box-shadow: 0 0 25px #9D00FF; background-color: #000;"
            scrolling="no"
            allow="autoplay; keyboard;"
        ></iframe>
    </div>
    """
    st.components.v1.html(pacman_embed_html, height=480)

# --- FOOTER ---
st.markdown("<br><hr><center>Made with 🧡 and 🔮 by a Spooky Developer</center>", unsafe_allow_html=True)
