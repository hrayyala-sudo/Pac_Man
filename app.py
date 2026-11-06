import streamlit as st

st.set_page_config(
    page_title="Retro Pac-Man Arcade Arena",
    page_icon="🕹️",
    layout="centered"
)

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle, #150F30 0%, #0A0813 100%);
    color: white;
}
h1, h2, h3 {
    color: #00D2FF !important;
    text-align: center;
    font-family: monospace;
}
</style>
""", unsafe_allow_html=True)

st.title("🕹️ RETRO PAC-MAN ARCADE ARENA")
st.markdown(
    "<center>Insert your token and clear the maze!</center>",
    unsafe_allow_html=True
)

st.divider()

game_html = r"""
<div style="text-align:center;background:#05030a;padding:15px;
            border:5px dashed #0055ff;border-radius:12px;">
    <div style="display:flex;justify-content:space-around;
                color:white;font-family:monospace;font-size:18px;">
        <span>SCORE: <span id="score">0</span></span>
        <span>LIVES: <span id="lives">❤️❤️❤️</span></span>
    </div>

    <canvas id="game" width="440" height="440"
            tabindex="0"
            style="background:black;border:3px solid blue;
                   max-width:100%;outline:none;">
    </canvas>

    <p style="color:#aaa;font-family:monospace;">
        CLICK THE GAME AND USE YOUR ARROW KEYS
    </p>
    <button onclick="restartGame()"
        style="padding:10px 20px;background:#00d2ff;
               border:0;border-radius:5px;font-weight:bold;
               cursor:pointer;">
        RESTART GAME
    </button>
</div>

<script>
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const scoreEl = document.getElementById("score");
const livesEl = document.getElementById("lives");

const tile = 20;
const rows = 22;
const cols = 22;

// 1 = wall, 0 = pellet path
const map = [
"1111111111111111111111",
"1000000000110000000001",
"1011101100110110110101",
"1000001000000100000001",
"1011101011101101110101",
"1000000000000000000001",
"1011011101110111011011",
"1001000001000000010001",
"1101011101011101010111",
"1000000000000000000001",
"1011101101110110110101",
"1000000000000000000001",
"1011011101110111011011",
"1001000001000000010001",
"1101011101011101010111",
"1000000000000000000001",
"1011101011101101110101",
"1000001000000100000001",
"1011101100110110110101",
"1000000000110000000001",
"1000000000000000000001",
"1111111111111111111111"
].map(row => row.split("").map(Number));

let score = 0;
let lives = 3;
let gameOver = false;
let pellets = [];

let pacman = {
    x: 210,
    y: 200,
    dx: 0,
    dy: 0,
    nextDx: 0,
    nextDy: 0,
    speed: 2,
    angle: 0,
    targetAngle: 0,
    mouth: 0.25
};

let ghosts = [];

function createPellets() {
    pellets = [];
    for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
            if (map[y][x] === 0) {
                pellets.push({
                    x: x * tile + tile / 2,
                    y: y * tile + tile / 2,
                    eaten: false
                });
            }
        }
    }
}

function resetPositions() {
    pacman.x = 210;
    pacman.y = 200;
    pacman.dx = 0;
    pacman.dy = 0;
    pacman.nextDx = 0;
    pacman.nextDy = 0;
    pacman.angle = 0;
    pacman.targetAngle = 0;

    ghosts = [
        {name:"Blinky", color:"#FF0000", x:200, y:180, dx:2, dy:0},
        {name:"Pinky", color:"#FFB8FF", x:220, y:180, dx:-2, dy:0},
        {name:"Inky", color:"#00FFFF", x:180, y:180, dx:0, dy:2},
        {name:"Clyde", color:"#FFB852", x:240, y:180, dx:0, dy:-2}
    ];
}

function wallAt(x, y) {
    const col = Math.floor(x / tile);
    const row = Math.floor(y / tile);

    if (row < 0 || row >= rows || col < 0 || col >= cols) {
        return true;
    }

    return map[row][col] === 1;
}

function canMove(x, y) {
    const size = 7;
    return !wallAt(x-size, y-size) &&
           !wallAt(x+size, y-size) &&
           !wallAt(x-size, y+size) &&
           !wallAt(x+size, y+size);
}

function setDirection(key) {
    if (key === "ArrowRight") {
        pacman.nextDx = pacman.speed;
        pacman.nextDy = 0;
        pacman.targetAngle = 0;
    } else if (key === "ArrowDown") {
        pacman.nextDx = 0;
        pacman.nextDy = pacman.speed;
        pacman.targetAngle = Math.PI / 2;
    } else if (key === "ArrowLeft") {
        pacman.nextDx = -pacman.speed;
        pacman.nextDy = 0;
        pacman.targetAngle = Math.PI;
    } else if (key === "ArrowUp") {
        pacman.nextDx = 0;
        pacman.nextDy = -pacman.speed;
        pacman.targetAngle = -Math.PI / 2;
    }
}

canvas.addEventListener("click", () => canvas.focus());

window.addEventListener("keydown", function(e) {
    if (["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"].includes(e.key)) {
        e.preventDefault();
        setDirection(e.key);
    }
});

function movePacman() {
    if (canMove(
        pacman.x + pacman.nextDx,
        pacman.y + pacman.nextDy
    )) {
        pacman.dx = pacman.nextDx;
        pacman.dy = pacman.nextDy;
        pacman.angle = pacman.targetAngle;
    }

    if (canMove(
        pacman.x + pacman.dx,
        pacman.y + pacman.dy
    )) {
        pacman.x += pacman.dx;
        pacman.y += pacman.dy;
    }
}

function moveGhosts() {
    ghosts.forEach(g => {
        if (Math.random() < 0.025 ||
            !canMove(g.x + g.dx, g.y + g.dy)) {

            const directions = [
                {dx:2,dy:0},
                {dx:-2,dy:0},
                {dx:0,dy:2},
                {dx:0,dy:-2}
            ];

            const possible = directions.filter(d =>
                canMove(g.x + d.dx, g.y + d.dy)
            );

            if (possible.length) {
                const choice = possible[
                    Math.floor(Math.random() * possible.length)
                ];
                g.dx = choice.dx;
                g.dy = choice.dy;
            }
        }

        if (canMove(g.x + g.dx, g.y + g.dy)) {
            g.x += g.dx;
            g.y += g.dy;
        }

        if (Math.hypot(pacman.x-g.x, pacman.y-g.y) < 15) {
            loseLife();
        }
    });
}

function loseLife() {
    if (gameOver) return;

    lives--;
    livesEl.textContent = "❤️".repeat(Math.max(0,lives));

    if (lives <= 0) {
        gameOver = true;
    } else {
        resetPositions();
    }
}

function eatPellets() {
    pellets.forEach(p => {
        if (!p.eaten &&
            Math.hypot(pacman.x-p.x, pacman.y-p.y) < 10) {
            p.eaten = true;
            score += 10;
            scoreEl.textContent = score;
        }
    });

    if (pellets.every(p => p.eaten)) {
        gameOver = true;
    }
}

function drawMaze() {
    for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
            if (map[y][x] === 1) {
                ctx.fillStyle = "#0022FF";
                ctx.fillRect(x*tile, y*tile, tile, tile);
                ctx.strokeStyle = "#001188";
                ctx.strokeRect(x*tile, y*tile, tile, tile);
            }
        }
    }
}

function drawPellets() {
    ctx.fillStyle = "#FFB8AE";

    pellets.forEach(p => {
        if (!p.eaten) {
            ctx.beginPath();
            ctx.arc(p.x, p.y, 3, 0, Math.PI*2);
            ctx.fill();
        }
    });
}

function drawPacman() {
    ctx.save();
    ctx.translate(pacman.x, pacman.y);
    ctx.rotate(pacman.angle);

    const mouth = Math.abs(Math.sin(Date.now()/100)) * 0.45;

    ctx.fillStyle = "#FFFF00";
    ctx.beginPath();
    ctx.moveTo(0,0);
    ctx.arc(0,0,9,mouth,Math.PI*2-mouth);
    ctx.closePath();
    ctx.fill();

    ctx.restore();
}

function drawGhosts() {
    ghosts.forEach(g => {
        ctx.fillStyle = g.color;
        ctx.beginPath();
        ctx.arc(g.x,g.y-2,8,Math.PI,0);
        ctx.lineTo(g.x+8,g.y+8);
        ctx.lineTo(g.x+4,g.y+5);
        ctx.lineTo(g.x,g.y+8);
        ctx.lineTo(g.x-4,g.y+5);
        ctx.lineTo(g.x-8,g.y+8);
        ctx.closePath();
        ctx.fill();

        ctx.fillStyle = "white";
        ctx.beginPath();
        ctx.arc(g.x-3,g.y-2,2,0,Math.PI*2);
        ctx.arc(g.x+3,g.y-2,2,0,Math.PI*2);
        ctx.fill();
    });
}

function drawGameOver() {
    ctx.fillStyle = "rgba(0,0,0,0.75)";
    ctx.fillRect(0,0,canvas.width,canvas.height);
    ctx.fillStyle = "#FFFF00";
    ctx.font = "bold 30px monospace";
    ctx.textAlign = "center";
    ctx.fillText("GAME OVER",220,210);
    ctx.font = "16px monospace";
    ctx.fillText("Press RESTART GAME",220,245);
}

function gameLoop() {
    ctx.clearRect(0,0,canvas.width,canvas.height);

    if (!gameOver) {
        movePacman();
        moveGhosts();
        eatPellets();
    }

    drawMaze();
    drawPellets();
    drawGhosts();
    drawPacman();

    if (gameOver) drawGameOver();

    requestAnimationFrame(gameLoop);
}

function restartGame() {
    score = 0;
    lives = 3;
    gameOver = false;
    scoreEl.textContent = score;
    livesEl.textContent = "❤️❤️❤️";
    createPellets();
    resetPositions();
}

createPellets();
resetPositions();
gameLoop();
</script>
"""

st.components.v1.html(game_html, height=550)

st.markdown("""
### ⌨️ How to Play
1. Click inside the Pac-Man game.
2. Use the **Up, Down, Left, and Right arrow keys**.
3. Eat the pellets to earn points.
4. Avoid Blinky, Pinky, Inky, and Clyde.
5. Use **Restart Game** to play again.
""")
