import streamlit as st

st.set_page_config(
    page_title="Classic Pac-Man Arcade",
    page_icon="🟡",
    layout="centered",
)

st.markdown(
    """
    <style>
        .stApp {
            background: #050505;
            color: white;
        }

        h1 {
            color: #ffdf00 !important;
            text-align: center;
            font-family: monospace;
        }

        .block-container {
            padding-top: 1rem;
            max-width: 760px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("PAC-MAN")

st.markdown(
    """
    <p style="text-align:center;color:#f5d742;font-family:monospace">
        CLASSIC ARCADE-STYLE MAZE
    </p>
    """,
    unsafe_allow_html=True,
)

html = r"""
<div id="arcade" style="
    width:100%;
    max-width:560px;
    margin:auto;
    text-align:center;
    background:#000;
    padding:12px;
    border:3px solid #253cff;
    box-sizing:border-box;
">

    <div style="
        display:flex;
        justify-content:space-between;
        color:#fff;
        font:bold 14px monospace;
        padding:2px 4px 10px;
    ">
        <span>1UP<br><span id="score">00</span></span>
        <span>HIGH SCORE<br><span id="high">00</span></span>
        <span>LEVEL<br><span id="level">1</span></span>
    </div>

    <!-- START AND SOUND BUTTONS ABOVE THE GAME -->
    <div style="
        display:flex;
        gap:8px;
        justify-content:center;
        flex-wrap:wrap;
        margin:2px 0 8px;
    ">

        <button id="start" style="
            background:#ffdf00;
            color:#000;
            border:0;
            border-radius:3px;
            padding:10px 20px;
            font-weight:bold;
            cursor:pointer;
        ">
            START / RESTART
        </button>

        <button id="sound" style="
            background:#222;
            color:#fff;
            border:1px solid #777;
            border-radius:3px;
            padding:10px 20px;
            cursor:pointer;
        ">
            SOUND: ON
        </button>

    </div>

    <div id="message" style="
        color:#ffdf00;
        font:bold 16px monospace;
        margin:4px 0 8px;
    ">
        PRESS START
    </div>

    <canvas
        id="board"
        width="504"
        height="558"
        tabindex="0"
        style="
            width:100%;
            height:auto;
            display:block;
            background:#000;
            outline:none;
            touch-action:none;
        "
    ></canvas>

    <!-- MOBILE DIRECTION BUTTONS -->
    <div style="
        display:grid;
        grid-template-columns:50px 50px 50px;
        grid-template-rows:42px 42px;
        justify-content:center;
        gap:5px;
        margin-top:12px;
    ">

        <button data-dir="up"
            style="grid-column:2;grid-row:1">
            ▲
        </button>

        <button data-dir="left"
            style="grid-column:1;grid-row:2">
            ◀
        </button>

        <button data-dir="down"
            style="grid-column:2;grid-row:2">
            ▼
        </button>

        <button data-dir="right"
            style="grid-column:3;grid-row:2">
            ▶
        </button>

    </div>

    <div style="
        color:#fff;
        font:13px monospace;
        margin:10px 0 4px;
    ">
        ARROW KEYS / WASD TO MOVE · SPACE TO PAUSE
    </div>

</div>


<script>
(() => {

    // ==================================================
    // CANVAS AND GAME SETTINGS
    // ==================================================

    const canvas = document.getElementById("board");
    const ctx = canvas.getContext("2d");

    const scoreNode = document.getElementById("score");
    const highNode = document.getElementById("high");
    const levelNode = document.getElementById("level");
    const message = document.getElementById("message");

    const TILE = 18;
    const COLS = 28;
    const ROWS = 31;

    const W = COLS * TILE;
    const H = ROWS * TILE;

    const STEP = 1000 / 60;

    // Normal arcade-style movement speeds.
    // These are tiles per simulation frame.
    const PAC_SPEED = 0.075;
    const GHOST_SPEED = 0.055;
    const FRIGHTENED_SPEED = 0.045;
    const RETURN_SPEED = 0.09;

    const dirs = {
        left: {
            x: -1,
            y: 0,
            angle: Math.PI
        },

        right: {
            x: 1,
            y: 0,
            angle: 0
        },

        up: {
            x: 0,
            y: -1,
            angle: -Math.PI / 2
        },

        down: {
            x: 0,
            y: 1,
            angle: Math.PI / 2
        }
    };


    // ==================================================
    // GAME VARIABLES
    // ==================================================

    let walls = [];
    let dots = [];
    let powerDots = [];
    let fruit = {};

    let pac;
    let ghosts = [];

    let score = 0;
    let high = 0;
    let lives = 3;
    let level = 1;

    let running = false;
    let paused = false;
    let gameEnded = false;

    let soundOn = true;
    let audioCtx = null;

    let frightenedUntil = 0;
    let ghostCombo = 0;

    let fruitUntil = 0;
    let dotsInitial = 1;

    let mouthPhase = 0;
    let frame = 0;

    let lastTime = 0;
    let accumulator = 0;


    // ==================================================
    // MAZE CREATION
    // ==================================================

    function blankGrid() {

        return Array.from(
            { length: ROWS },
            () => Array(COLS).fill(0)
        );

    }


    function makeMaze() {

        const g = blankGrid();

        // Outer boundaries.
        for (let x = 0; x < COLS; x++) {
            g[0][x] = 1;
            g[ROWS - 1][x] = 1;
        }

        for (let y = 0; y < ROWS; y++) {
            g[y][0] = 1;
            g[y][COLS - 1] = 1;
        }

        // Side tunnels.
        g[14][0] = 0;
        g[14][COLS - 1] = 0;


        function rect(x, y, w, h) {

            for (let yy = y; yy < y + h; yy++) {

                for (let xx = x; xx < x + w; xx++) {

                    if (
                        xx > 0 &&
                        xx < COLS - 1 &&
                        yy > 0 &&
                        yy < ROWS - 1
                    ) {
                        g[yy][xx] = 1;
                    }

                }
            }
        }


        function hwall(y, x1, x2, gaps = []) {

            for (let x = x1; x <= x2; x++) {

                if (!gaps.includes(x)) {
                    g[y][x] = 1;
                }

            }
        }


        function vwall(x, y1, y2, gaps = []) {

            for (let y = y1; y <= y2; y++) {

                if (!gaps.includes(y)) {
                    g[y][x] = 1;
                }

            }
        }


        // Upper maze.
        rect(2, 2, 5, 2);
        rect(9, 2, 3, 2);
        rect(16, 2, 3, 2);
        rect(21, 2, 5, 2);

        rect(2, 6, 3, 3);
        rect(7, 6, 5, 2);
        rect(16, 6, 5, 2);
        rect(23, 6, 3, 3);

        hwall(10, 1, 6, [3]);
        hwall(10, 21, 26, [24]);

        rect(8, 9, 3, 3);
        rect(17, 9, 3, 3);

        hwall(12, 2, 6, [4]);
        hwall(12, 21, 25, [23]);

        vwall(13, 2, 11, [5, 8]);
        vwall(14, 2, 11, [5, 8]);

        hwall(4, 12, 15, [13, 14]);


        // Middle maze.
        vwall(6, 13, 17, [15]);
        vwall(21, 13, 17, [15]);

        rect(2, 15, 4, 2);
        rect(22, 15, 4, 2);

        hwall(19, 1, 6, [3]);
        hwall(19, 21, 26, [24]);

        rect(8, 15, 3, 2);
        rect(17, 15, 3, 2);


        // Ghost pen walls.
        rect(10, 13, 8, 1);
        rect(10, 17, 1, 3);
        rect(17, 17, 1, 3);

        rect(11, 20, 6, 1);
        rect(11, 24, 6, 1);


        // Lower maze.
        rect(2, 22, 5, 2);
        rect(9, 22, 3, 2);
        rect(16, 22, 3, 2);
        rect(21, 22, 5, 2);

        rect(2, 26, 3, 3);
        rect(7, 26, 5, 2);
        rect(16, 26, 5, 2);
        rect(23, 26, 3, 3);

        hwall(25, 1, 6, [3]);
        hwall(25, 21, 26, [24]);

        vwall(13, 20, 28, [23, 26]);
        vwall(14, 20, 28, [23, 26]);

        hwall(21, 1, 6, [3]);
        hwall(21, 21, 26, [24]);

        hwall(24, 8, 19, [10, 13, 14, 17]);


        // Clear ghost-house interior.
        for (let y = 13; y <= 17; y++) {

            for (let x = 10; x <= 17; x++) {
                g[y][x] = 0;
            }

        }


        // Open central lanes.
        [
            [13, 12],
            [14, 12],
            [15, 12],

            [13, 13],
            [14, 13],
            [15, 13],

            [13, 14],
            [14, 14],
            [15, 14],

            [13, 15],
            [14, 15],
            [15, 15],

            [13, 16],
            [14, 16],
            [15, 16]
        ].forEach(([x, y]) => {
            g[y][x] = 0;
        });


        // Open the player's starting corridor.
        [
            [12, 12],
            [13, 12],
            [14, 12],
            [15, 12],
            [16, 12],
            [17, 12],
            [18, 12],
            [19, 12],
            [20, 12]
        ].forEach(([x, y]) => {
            g[y][x] = 0;
        });


        // Additional openings.
        [
            [5, 5], [6, 5],
            [12, 5], [15, 5],
            [20, 5], [22, 5],

            [5, 11], [6, 11],
            [21, 11], [22, 11],

            [5, 20], [6, 20],
            [21, 20], [22, 20],

            [5, 24], [6, 24],
            [21, 24], [22, 24],

            [12, 18], [15, 18],
            [12, 20], [15, 20],

            [12, 23], [15, 23],
            [8, 14], [19, 14],

            [8, 20], [19, 20]
        ].forEach(([x, y]) => {
            g[y][x] = 0;
        });


        return g;
    }


    // ==================================================
    // INITIALIZE LEVEL
    // ==================================================

    function initLevel() {

        walls = makeMaze();

        dots = [];
        powerDots = [];

        for (let y = 1; y < ROWS - 1; y++) {

            for (let x = 1; x < COLS - 1; x++) {

                if (
                    !walls[y][x] &&
                    !(x >= 10 && x <= 17 && y >= 13 && y <= 17)
                ) {
                    dots.push({ x, y });
                }

            }
        }


        // Keep the starting area clear.
        dots = dots.filter(
            p => !(p.x >= 12 && p.x <= 15 && p.y >= 10 && p.y <= 12)
        );


        // Power pellets.
        [
            [1, 3],
            [26, 3],
            [1, 27],
            [26, 27]
        ].forEach(([x, y]) => {

            dots = dots.filter(
                p => p.x !== x || p.y !== y
            );

            powerDots.push({ x, y });

        });


        fruit = {
            x: 14,
            y: 23,
            visible: false,
            eaten: false
        };


        resetActors();
    }


    // ==================================================
    // RESET PLAYERS AND GHOSTS
    // ==================================================

    function resetActors() {

        // Pac-Man starts in an open corridor.
        // He automatically starts moving to the right.

        pac = {
            x: 12,
            y: 12,
            dir: "right",
            want: "right",
            target: null
        };


        const home = [

            {
                name: "Blinky",
                color: "#ff2020",
                x: 13,
                y: 13,
                dir: "left"
            },

            {
                name: "Pinky",
                color: "#ff9de2",
                x: 12,
                y: 15,
                dir: "up"
            },

            {
                name: "Inky",
                color: "#00e5ff",
                x: 14,
                y: 15,
                dir: "down"
            },

            {
                name: "Clyde",
                color: "#ffad32",
                x: 15,
                y: 15,
                dir: "right"
            }

        ];


        ghosts = home.map(g => ({
            ...g,
            homeX: g.x,
            homeY: g.y,
            target: null,
            returning: false
        }));

    }


    // ==================================================
    // WALL COLLISION
    // ==================================================

    function wallAt(x, y) {

        if (
            x < 0 ||
            x >= COLS ||
            y < 0 ||
            y >= ROWS
        ) {
            return true;
        }

        return walls[y][x] === 1;
    }


    function canGo(x, y, direction) {

        const d = dirs[direction];

        if (!d) {
            return false;
        }

        const nx = x + d.x;
        const ny = y + d.y;


        // Side tunnels are only available on row 14.
        if (
            y === 14 &&
            ny === 14 &&
            (nx < 0 || nx >= COLS)
        ) {
            return true;
        }


        return !wallAt(nx, ny);
    }


    // ==================================================
    // TILE-TO-TILE MOVEMENT
    // ==================================================

    // This is the important movement fix.
    // Actors travel to a specific next tile center.
    // They cannot drift through walls or get snapped
    // backward every frame.

    function moveTowardTarget(actor, speed) {

        if (!actor.target) {
            return;
        }

        const dx = actor.target.x - actor.x;
        const dy = actor.target.y - actor.y;

        const distance = Math.hypot(dx, dy);


        if (distance <= speed) {

            actor.x = actor.target.x;
            actor.y = actor.target.y;

            actor.target = null;


            // Wrap through the side tunnels.
            if (
                actor.y === 14 &&
                actor.x < 0
            ) {
                actor.x = COLS - 1;
            }

            if (
                actor.y === 14 &&
                actor.x >= COLS
            ) {
                actor.x = 0;
            }

        } else {

            actor.x += (dx / distance) * speed;
            actor.y += (dy / distance) * speed;

        }

    }


    // ==================================================
    // PAC-MAN MOVEMENT
    // ==================================================

    function movePac() {

        // Only make turns at the center of a tile.
        if (!pac.target) {

            pac.x = Math.round(pac.x);
            pac.y = Math.round(pac.y);


            // First try the direction requested by the player.
            if (
                pac.want &&
                canGo(pac.x, pac.y, pac.want)
            ) {
                pac.dir = pac.want;
            }


            // If the next tile is a wall, stop.
            if (
                !pac.dir ||
                !canGo(pac.x, pac.y, pac.dir)
            ) {

                pac.dir = null;
                return;

            }


            const d = dirs[pac.dir];


            // Set the exact next tile target.
            pac.target = {
                x: pac.x + d.x,
                y: pac.y + d.y
            };

        }


        // Move smoothly toward the checked tile.
        moveTowardTarget(pac, PAC_SPEED);

        mouthPhase += 0.28;
    }


    function setDirection(direction) {

        if (dirs[direction]) {
            pac.want = direction;
        }

    }


    // ==================================================
    // SOUND
    // ==================================================

    function playTone(
        freq = 440,
        duration = 0.05,
        type = "square",
        volume = 0.025
    ) {

        if (!soundOn) {
            return;
        }

        try {

            audioCtx ||= new (
                window.AudioContext ||
                window.webkitAudioContext
            )();

            const oscillator = audioCtx.createOscillator();
            const gain = audioCtx.createGain();

            oscillator.type = type;
            oscillator.frequency.value = freq;

            gain.gain.value = volume;

            oscillator.connect(gain);
            gain.connect(audioCtx.destination);

            oscillator.start();

            gain.gain.exponentialRampToValueAtTime(
                0.001,
                audioCtx.currentTime + duration
            );

            oscillator.stop(
                audioCtx.currentTime + duration
            );

        } catch (e) {
            console.log("Audio unavailable", e);
        }

    }


    // ==================================================
    // SCORE
    // ==================================================

    function addScore(amount) {

        score += amount;
        high = Math.max(high, score);

        scoreNode.textContent =
            String(score).padStart(2, "0");

        highNode.textContent =
            String(high).padStart(2, "0");

    }


    // ==================================================
    // GHOST TARGETS
    // ==================================================

    function targetForGhost(g) {

        if (g.returning) {

            return {
                x: g.homeX,
                y: g.homeY
            };

        }


        if (Date.now() < frightenedUntil) {

            return {
                x: Math.random() * COLS,
                y: Math.random() * ROWS
            };

        }


        if (g.name === "Blinky") {

            return {
                x: pac.x,
                y: pac.y
            };

        }


        if (g.name === "Pinky") {

            const d = dirs[pac.dir || "left"];

            return {
                x: pac.x + d.x * 4,
                y: pac.y + d.y * 4
            };

        }


        if (g.name === "Inky") {

            return {
                x: pac.x + (pac.x - 13) * 0.6,
                y: pac.y + (pac.y - 14) * 0.6
            };

        }


        return Math.hypot(
            g.x - pac.x,
            g.y - pac.y
        ) > 8

            ? {
                x: pac.x,
                y: pac.y
            }

            : {
                x: 1,
                y: ROWS - 2
            };

    }


    // ==================================================
    // GHOST MOVEMENT
    // ==================================================

    function moveGhost(g) {

        // Choose a new direction at each tile center.
        if (!g.target) {

            g.x = Math.round(g.x);
            g.y = Math.round(g.y);


            const reverse = {
                left: "right",
                right: "left",
                up: "down",
                down: "up"
            };


            let choices = Object.keys(dirs).filter(
                direction => (
                    direction !== reverse[g.dir] &&
                    canGo(g.x, g.y, direction)
                )
            );


            // Allow reversing if there is no other way.
            if (!choices.length) {

                const opposite = reverse[g.dir];

                if (
                    opposite &&
                    canGo(g.x, g.y, opposite)
                ) {
                    choices = [opposite];
                }

            }


            if (!choices.length) {
                g.dir = null;
                return;
            }


            // Frightened ghosts move randomly.
            if (
                Date.now() < frightenedUntil &&
                !g.returning
            ) {

                g.dir = choices[
                    Math.floor(Math.random() * choices.length)
                ];

            } else {

                const target = targetForGhost(g);

                choices.sort((a, b) => {

                    const da = dirs[a];
                    const db = dirs[b];

                    const distanceA = Math.hypot(
                        g.x + da.x - target.x,
                        g.y + da.y - target.y
                    );

                    const distanceB = Math.hypot(
                        g.x + db.x - target.x,
                        g.y + db.y - target.y
                    );

                    return distanceA - distanceB;

                });

                g.dir = choices[0];

            }


            const d = dirs[g.dir];

            g.target = {
                x: g.x + d.x,
                y: g.y + d.y
            };

        }


        let speed = GHOST_SPEED;

        if (g.returning) {
            speed = RETURN_SPEED;
        } else if (Date.now() < frightenedUntil) {
            speed = FRIGHTENED_SPEED;
        }


        moveTowardTarget(g, speed);


        // Return ghosts to their starting positions.
        if (
            g.returning &&
            !g.target &&
            Math.round(g.x) === g.homeX &&
            Math.round(g.y) === g.homeY
        ) {

            g.returning = false;
            g.x = g.homeX;
            g.y = g.homeY;
            g.target = null;

        }

    }


    // ==================================================
    // DOT COLLECTION
    // ==================================================

    function collect() {

        const px = Math.round(pac.x);
        const py = Math.round(pac.y);


        // Regular pellets.
        const dotIndex = dots.findIndex(
            p => p.x === px && p.y === py
        );

        if (dotIndex >= 0) {

            dots.splice(dotIndex, 1);

            addScore(10);

            playTone(
                300 + (frame % 2) * 80,
                0.025
            );

        }


        // Power pellets.
        const powerIndex = powerDots.findIndex(
            p => p.x === px && p.y === py
        );

        if (powerIndex >= 0) {

            powerDots.splice(powerIndex, 1);

            addScore(50);

            frightenedUntil = Date.now() + 8000;
            ghostCombo = 0;

            playTone(
                180,
                0.3,
                "sawtooth",
                0.04
            );

        }


        // Fruit appears after half the pellets are collected.
        if (
            dots.length < dotsInitial / 2 &&
            !fruit.visible &&
            !fruit.eaten
        ) {

            fruit.visible = true;
            fruitUntil = Date.now() + 7000;

        }


        // Collect fruit.
        if (
            fruit.visible &&
            px === fruit.x &&
            py === fruit.y
        ) {

            fruit.visible = false;
            fruit.eaten = true;

            addScore(100);

            playTone(700, 0.15);

        }


        // Fruit disappears after a few seconds.
        if (
            fruit.visible &&
            Date.now() > fruitUntil
        ) {
            fruit.visible = false;
        }


        // Advance to the next level.
        if (
            dots.length === 0 &&
            powerDots.length === 0
        ) {

            level++;

            levelNode.textContent = level;

            frightenedUntil = 0;

            initLevel();

            dotsInitial = dots.length;

            message.textContent =
                "LEVEL " + level + " — READY!";

        }

    }


    // ==================================================
    // GHOST COLLISIONS
    // ==================================================

    function hitTest() {

        for (const g of ghosts) {

            if (g.returning) {
                continue;
            }


            const distance = Math.hypot(
                pac.x - g.x,
                pac.y - g.y
            );


            if (distance < 0.58) {

                if (Date.now() < frightenedUntil) {

                    g.returning = true;

                    ghostCombo++;

                    g.target = null;

                    addScore(
                        [200, 400, 800, 1600][
                            Math.min(ghostCombo - 1, 3)
                        ]
                    );

                    playTone(
                        220 + ghostCombo * 100,
                        0.12
                    );

                } else {

                    loseLife();
                    return;

                }

            }

        }

    }


    // ==================================================
    // LIVES
    // ==================================================

    function loseLife() {

        lives--;

        if (lives <= 0) {

            running = false;
            gameEnded = true;

            message.textContent =
                "GAME OVER — PRESS START";

            playTone(
                90,
                0.5,
                "sawtooth"
            );

        } else {

            message.textContent = "READY!";

            resetActors();

        }

    }


    // ==================================================
    // DRAW MAZE
    // ==================================================

    function drawWall(x, y) {

        const px = x * TILE;
        const py = y * TILE;

        ctx.fillStyle = "#000";

        ctx.fillRect(
            px,
            py,
            TILE,
            TILE
        );

        ctx.strokeStyle = "#245bff";
        ctx.lineWidth = 2.2;

        ctx.strokeRect(
            px + 1.5,
            py + 1.5,
            TILE - 3,
            TILE - 3
        );

    }


    function drawMaze() {

        ctx.fillStyle = "#000";

        ctx.fillRect(
            0,
            0,
            W,
            H
        );


        for (let y = 0; y < ROWS; y++) {

            for (let x = 0; x < COLS; x++) {

                if (walls[y][x]) {
                    drawWall(x, y);
                }

            }

        }


        // Ghost-house gate.
        ctx.strokeStyle = "#ff9de2";
        ctx.lineWidth = 2;

        ctx.beginPath();

        ctx.moveTo(
            10 * TILE,
            13 * TILE + TILE / 2
        );

        ctx.lineTo(
            18 * TILE,
            13 * TILE + TILE / 2
        );

        ctx.stroke();

    }


    // ==================================================
    // DRAW PELLETS
    // ==================================================

    function drawDots() {

        ctx.fillStyle = "#ffd8a8";

        dots.forEach(p => {

            ctx.beginPath();

            ctx.arc(
                (p.x + 0.5) * TILE,
                (p.y + 0.5) * TILE,
                2,
                0,
                Math.PI * 2
            );

            ctx.fill();

        });


        // Power pellets.
        powerDots.forEach(p => {

            const radius =
                4 + Math.sin(Date.now() / 110) * 1.2;

            ctx.fillStyle = "#fff1cf";

            ctx.beginPath();

            ctx.arc(
                (p.x + 0.5) * TILE,
                (p.y + 0.5) * TILE,
                radius,
                0,
                Math.PI * 2
            );

            ctx.fill();

        });


        // Fruit.
        if (fruit.visible) {

            ctx.fillStyle = "#ff3030";

            ctx.beginPath();

            ctx.arc(
                (fruit.x + 0.5) * TILE,
                (fruit.y + 0.5) * TILE,
                6,
                0,
                Math.PI * 2
            );

            ctx.fill();

            ctx.fillStyle = "#45e05a";

            ctx.fillRect(
                (fruit.x + 0.5) * TILE,
                (fruit.y + 0.5) * TILE - 9,
                2,
                5
            );

        }

    }


    // ==================================================
    // DRAW PAC-MAN
    // ==================================================

    function drawPac() {

        const direction = dirs[
            pac.dir || pac.want || "right"
        ];

        const x = (pac.x + 0.5) * TILE;
        const y = (pac.y + 0.5) * TILE;

        const mouthOpen =
            0.18 +
            Math.abs(Math.sin(mouthPhase)) * 0.38;

        ctx.fillStyle = "#ffe500";

        ctx.beginPath();

        ctx.moveTo(x, y);

        ctx.arc(
            x,
            y,
            8.5,
            direction.angle + mouthOpen,
            direction.angle + Math.PI * 2 - mouthOpen
        );

        ctx.closePath();
        ctx.fill();

    }


    // ==================================================
    // DRAW GHOSTS
    // ==================================================

    function drawGhost(g) {

        const x = (g.x + 0.5) * TILE;
        const y = (g.y + 0.5) * TILE;

        const frightened =
            Date.now() < frightenedUntil &&
            !g.returning;

        const color = g.returning
            ? "#ffffff"
            : (
                frightened
                    ? "#1748d8"
                    : g.color
            );


        // Ghost body.
        ctx.fillStyle = color;

        ctx.beginPath();

        ctx.arc(
            x,
            y - 1,
            8,
            Math.PI,
            0
        );

        ctx.lineTo(x + 8, y + 8);
        ctx.lineTo(x + 4, y + 5);
        ctx.lineTo(x, y + 8);
        ctx.lineTo(x - 4, y + 5);
        ctx.lineTo(x - 8, y + 8);

        ctx.closePath();
        ctx.fill();


        if (!g.returning) {

            const look = dirs[g.dir] || dirs.left;

            // Eyes.
            ctx.fillStyle = "#fff";

            ctx.beginPath();

            ctx.ellipse(
                x - 3 + look.x * 1.5,
                y - 2 + look.y * 1.5,
                2.5,
                3.2,
                0,
                0,
                Math.PI * 2
            );

            ctx.ellipse(
                x + 3 + look.x * 1.5,
                y - 2 + look.y * 1.5,
                2.5,
                3.2,
                0,
                0,
                Math.PI * 2
            );

            ctx.fill();


            // Pupils.
            ctx.fillStyle = "#111";

            ctx.beginPath();

            ctx.arc(
                x - 3 + look.x * 2,
                y - 2 + look.y * 2,
                1.2,
                0,
                Math.PI * 2
            );

            ctx.arc(
                x + 3 + look.x * 2,
                y - 2 + look.y * 2,
                1.2,
                0,
                Math.PI * 2
            );

            ctx.fill();

        } else {

            // Returning ghost eyes.
            ctx.fillStyle = "#fff";

            ctx.fillRect(x - 5, y - 2, 3, 2);
            ctx.fillRect(x + 2, y - 2, 3, 2);

        }

    }


    // ==================================================
    // DRAW LIVES
    // ==================================================

    function drawLives() {

        ctx.fillStyle = "#ffe500";

        for (let i = 0; i < lives; i++) {

            const x = 12 + i * 22;
            const y = H - 8;

            ctx.beginPath();

            ctx.moveTo(x, y);

            ctx.arc(
                x,
                y,
                7,
                0.35,
                Math.PI * 2 - 0.35
            );

            ctx.closePath();
            ctx.fill();

        }

    }


    // ==================================================
    // OVERLAY
    // ==================================================

    function overlay(text) {

        ctx.fillStyle = "rgba(0,0,0,.75)";

        ctx.fillRect(
            0,
            H / 2 - 28,
            W,
            56
        );

        ctx.fillStyle = "#ffe500";
        ctx.font = "bold 25px monospace";
        ctx.textAlign = "center";

        ctx.fillText(
            text,
            W / 2,
            H / 2 + 9
        );

    }


    // ==================================================
    // RENDER GAME
    // ==================================================

    function render() {

        drawMaze();
        drawDots();
        drawPac();

        ghosts.forEach(drawGhost);

        drawLives();


        if (!running && !gameEnded) {
            overlay("READY!");
        }

        if (paused) {
            overlay("PAUSED");
        }

        if (gameEnded) {
            overlay("GAME OVER");
        }

    }


    // ==================================================
    // GAME UPDATE
    // ==================================================

    function tick() {

        if (
            !running ||
            paused ||
            gameEnded
        ) {
            return;
        }


        frame++;

        movePac();

        ghosts.forEach(moveGhost);

        collect();

        hitTest();


        if (Date.now() > frightenedUntil) {

            ghosts.forEach(g => {
                g.frightened = false;
            });

        }


        message.textContent = "";

    }


    // ==================================================
    // ANIMATION LOOP
    // ==================================================

    function loop(timestamp) {

        if (!lastTime) {
            lastTime = timestamp;
        }

        const dt = Math.min(
            timestamp - lastTime,
            100
        );

        lastTime = timestamp;

        accumulator += dt;


        while (accumulator >= STEP) {

            tick();

            accumulator -= STEP;

        }


        render();

        requestAnimationFrame(loop);

    }


    // ==================================================
    // START / RESTART GAME
    // ==================================================

    function startGame() {

        score = 0;
        lives = 3;
        level = 1;

        running = true;
        paused = false;
        gameEnded = false;

        frightenedUntil = 0;
        ghostCombo = 0;

        mouthPhase = 0;
        frame = 0;

        scoreNode.textContent = "00";
        levelNode.textContent = "1";

        initLevel();

        dotsInitial = dots.length;

        message.textContent = "READY!";

        canvas.focus();

        playTone(520, 0.12);

    }


    // ==================================================
    // KEYBOARD CONTROLS
    // ==================================================

    function keyHandler(e) {

        const mapKey = {

            ArrowLeft: "left",
            ArrowRight: "right",
            ArrowUp: "up",
            ArrowDown: "down",

            a: "left",
            A: "left",

            d: "right",
            D: "right",

            w: "up",
            W: "up",

            s: "down",
            S: "down"

        };


        if (mapKey[e.key]) {

            e.preventDefault();

            setDirection(mapKey[e.key]);

        }


        if (e.code === "Space") {

            e.preventDefault();

            if (running && !gameEnded) {

                paused = !paused;

                message.textContent = paused
                    ? "PAUSED"
                    : "";

            }

        }

    }


    // Capture keyboard input within the game iframe.
    document.addEventListener(
        "keydown",
        keyHandler,
        true
    );


    // Clicking the game screen gives it keyboard focus.
    canvas.addEventListener(
        "pointerdown",
        () => canvas.focus()
    );


    // ==================================================
    // BUTTON EVENTS
    // ==================================================

    document.getElementById("start").addEventListener(
        "click",
        startGame
    );


    document.getElementById("sound").addEventListener(
        "click",
        function() {

            soundOn = !soundOn;

            this.textContent =
                "SOUND: " + (soundOn ? "ON" : "OFF");

        }
    );


    // Mobile direction controls.
    document.querySelectorAll("[data-dir]").forEach(button => {

        button.addEventListener(
            "pointerdown",
            function(e) {

                e.preventDefault();

                setDirection(this.dataset.dir);

                canvas.focus();

            }
        );

    });


    // ==================================================
    // INITIALIZE GAME
    // ==================================================

    initLevel();

    dotsInitial = dots.length;

    render();

    requestAnimationFrame(loop);

})();
</script>
"""

st.components.v1.html(
    html,
    height=850,
    scrolling=False,
)

st.caption(
    "Classic arcade-style Pac-Man recreation. "
    "Use the arrow keys, WASD, or the on-screen directional controls."
)
