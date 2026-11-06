import streamlit as st

st.set_page_config(
    page_title="Classic Pac-Man Arcade",
    page_icon="🟡",
    layout="centered",
)

st.markdown(
    """
    <style>
      .stApp { background: #050505; color: white; }
      h1 { color: #ffdf00 !important; text-align: center; font-family: monospace; }
      .block-container { padding-top: 1.2rem; max-width: 760px; }
      div[data-testid="stMarkdownContainer"] p { color: #ddd; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("PAC-MAN")
st.markdown(
    "<p style='text-align:center;color:#f5d742;font-family:monospace'>"
    "READY!  •  CLASSIC ARCADE-STYLE MAZE</p>",
    unsafe_allow_html=True,
)

html = r"""
<div id="arcade" style="width:100%;max-width:560px;margin:auto;text-align:center;
background:#000;padding:12px;border:3px solid #253cff;box-sizing:border-box;">

  <div style="display:flex;justify-content:space-between;color:#fff;
  font:bold 15px monospace;padding:2px 4px 8px">
    <span>1UP<br><span id="score">00</span></span>
    <span>HIGH SCORE<br><span id="high">00</span></span>
    <span>LEVEL<br><span id="level">1</span></span>
  </div>

  <!-- Controls ABOVE the game screen -->
  <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:2px 0 8px">
    <button id="start" style="background:#ffdf00;color:#000;border:0;border-radius:3px;padding:10px 20px;
      font-weight:bold;cursor:pointer">START / RESTART</button>

    <button id="sound" style="background:#222;color:#fff;border:1px solid #777;border-radius:3px;
      padding:10px 20px;cursor:pointer">SOUND: ON</button>
  </div>

  <div id="message" style="color:#ffdf00;font:bold 16px monospace;margin:4px 0 8px">
    PRESS START
  </div>

  <canvas id="board" width="504" height="558"
    style="width:100%;height:auto;display:block;background:#000;outline:none"
    tabindex="0"></canvas>

  <div style="color:#fff;font:13px monospace;margin:9px 0 4px">
    ARROW KEYS / WASD TO MOVE · SPACE TO PAUSE
  </div>

</div>

<script>
(() => {

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

  let walls, dots, powerDots, fruit;

  let score = 0;
  let high = 0;
  let lives = 3;
  let level = 1;

  let running = false;
  let paused = false;
  let gameEnded = false;

  let soundOn = true;
  let audioCtx = null;

  let lastTime = 0;
  let accumulator = 0;

  // Fixed 60 FPS simulation for smooth movement.
  const STEP = 1000 / 60;

  const dirs = {
    left:  {x:-1, y:0,  angle:Math.PI},
    right: {x:1,  y:0,  angle:0},
    up:    {x:0,  y:-1, angle:-Math.PI/2},
    down:  {x:0,  y:1,  angle:Math.PI/2}
  };

  let pac;
  let ghosts;

  let frightenedUntil = 0;
  let ghostCombo = 0;
  let fruitUntil = 0;

  let mouthPhase = 0;
  let frame = 0;
  let dotsInitial = 1;


  // --------------------------------------------------
  // MAZE
  // --------------------------------------------------

  function blankGrid() {
    return Array.from(
      {length: ROWS},
      () => Array(COLS).fill(0)
    );
  }


  function makeMaze() {

    const g = blankGrid();

    // Outer boundary and side tunnels.
    for (let x = 0; x < COLS; x++) {
      g[0][x] = 1;
      g[ROWS - 1][x] = 1;
    }

    for (let y = 0; y < ROWS; y++) {
      g[y][0] = 1;
      g[y][COLS - 1] = 1;
    }

    g[14][0] = 0;
    g[14][COLS - 1] = 0;


    const rect = (x, y, w, h) => {
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
    };


    const hwall = (y, x1, x2, gaps = []) => {
      for (let x = x1; x <= x2; x++) {
        if (!gaps.includes(x)) {
          g[y][x] = 1;
        }
      }
    };


    const vwall = (x, y1, y2, gaps = []) => {
      for (let y = y1; y <= y2; y++) {
        if (!gaps.includes(y)) {
          g[y][x] = 1;
        }
      }
    };


    // Upper-left and upper-right maze sections.
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


    // Central top corridors and side chambers.
    hwall(4, 12, 15, [13, 14]);

    vwall(6, 13, 17, [15]);
    vwall(21, 13, 17, [15]);

    rect(2, 15, 4, 2);
    rect(22, 15, 4, 2);

    hwall(19, 1, 6, [3]);
    hwall(19, 21, 26, [24]);

    rect(8, 15, 3, 2);
    rect(17, 15, 3, 2);


    // Ghost pen.
    rect(10, 13, 8, 1);
    rect(10, 17, 1, 3);
    rect(17, 17, 1, 3);

    rect(11, 20, 6, 1);
    rect(11, 24, 6, 1);


    // Lower-middle maze sections.
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


    // Lower cross-corridors.
    hwall(21, 1, 6, [3]);
    hwall(21, 21, 26, [24]);

    hwall(24, 8, 19, [10, 13, 14, 17]);


    // Open central lanes.
    g[12][13] = 0;
    g[12][14] = 0;
    g[12][15] = 0;

    g[13][13] = 0;
    g[13][14] = 0;
    g[13][15] = 0;

    g[14][13] = 0;
    g[14][14] = 0;
    g[14][15] = 0;

    g[15][13] = 0;
    g[15][14] = 0;
    g[15][15] = 0;


    // Ensure the player start pocket and ghost pen are clear.
    for (let y = 13; y <= 17; y++) {
      for (let x = 10; x <= 17; x++) {
        g[y][x] = 0;
      }
    }

    // Open center exit for ghosts.
    g[12][13] = 0;
    g[12][14] = 0;
    g[12][15] = 0;

    g[14][0] = 0;
    g[14][COLS - 1] = 0;


    // Connected openings.
    [
      [5,5], [6,5], [12,5], [15,5], [20,5], [22,5],
      [5,11], [6,11], [21,11], [22,11],
      [5,20], [6,20], [21,20], [22,20],
      [5,24], [6,24], [21,24], [22,24],
      [12,18], [15,18], [12,20], [15,20],
      [12,23], [15,23], [8,14], [19,14],
      [8,20], [19,20]
    ].forEach(([x, y]) => {
      g[y][x] = 0;
    });

    return g;
  }


  // --------------------------------------------------
  // LEVEL AND ACTORS
  // --------------------------------------------------

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
          dots.push({x, y});
        }
      }
    }

    // Keep the player spawn area clear.
    dots = dots.filter(
      p => !(p.x >= 12 && p.x <= 15 && p.y >= 23 && p.y <= 27)
    );

    // Power pellets.
    [[1, 3], [26, 3], [1, 27], [26, 27]].forEach(([x, y]) => {

      dots = dots.filter(
        p => p.x !== x || p.y !== y
      );

      powerDots.push({x, y});
    });

    fruit = {
      x: 14,
      y: 23,
      visible: false,
      eaten: false
    };

    resetActors();
  }


  function resetActors() {

    // Actor coordinates are tile-center coordinates.
    // (0,0) is the center of the top-left tile.

    pac = {
      x: 13,
      y: 23,
      dir: null,
      want: null,
      dead: false
    };

    const home = [

      {
        name: "Blinky",
        color: "#ff2020",
        x: 13,
        y: 13,
        dir: "left",
        mode: "chase"
      },

      {
        name: "Pinky",
        color: "#ff9de2",
        x: 12,
        y: 15,
        dir: "up",
        mode: "scatter"
      },

      {
        name: "Inky",
        color: "#00e5ff",
        x: 14,
        y: 15,
        dir: "down",
        mode: "scatter"
      },

      {
        name: "Clyde",
        color: "#ffad32",
        x: 15,
        y: 15,
        dir: "right",
        mode: "scatter"
      }

    ];

    ghosts = home.map(g => ({
      ...g,
      homeX: g.x,
      homeY: g.y,
      frightened: false,
      returning: false
    }));
  }


  // --------------------------------------------------
  // WALL COLLISION AND MOVEMENT
  // --------------------------------------------------

  function wallAt(x, y) {

    // x/y are tile indices, not pixel positions.

    if (
      x < 0 ||
      x >= COLS ||
      y < 0 ||
      y >= ROWS
    ) {
      return true;
    }

    return walls[y]?.[x] === 1;
  }


  function canGo(x, y, dir) {

    const d = dirs[dir];

    if (!d) {
      return false;
    }

    const nx = x + d.x;
    const ny = y + d.y;

    // The only out-of-bounds passage is the horizontal tunnel on row 14.
    if (
      y === 14 &&
      ny === 14 &&
      (nx < 0 || nx >= COLS)
    ) {
      return true;
    }

    return !wallAt(nx, ny);
  }


  function aligned(v) {
    return Math.abs(v - Math.round(v)) < 0.105;
  }


  function atNode(actor) {
    return aligned(actor.x) && aligned(actor.y);
  }


  function snap(v) {
    return Math.round(v);
  }


  function wrapTunnel(actor) {

    if (Math.round(actor.y) !== 14) {
      return;
    }

    if (actor.x < -0.5) {
      actor.x = COLS - 0.5;
    } else if (actor.x > COLS - 0.5) {
      actor.x = -0.5;
    }
  }


  // --------------------------------------------------
  // SOUND AND SCORE
  // --------------------------------------------------

  function playTone(
    freq = 440,
    duration = 0.05,
    type = "square",
    vol = 0.025
  ) {

    if (!soundOn) {
      return;
    }

    try {

      audioCtx ||= new (
        window.AudioContext ||
        window.webkitAudioContext
      )();

      const o = audioCtx.createOscillator();
      const gain = audioCtx.createGain();

      o.type = type;
      o.frequency.value = freq;

      gain.gain.value = vol;

      o.connect(gain);
      gain.connect(audioCtx.destination);

      o.start();

      gain.gain.exponentialRampToValueAtTime(
        0.001,
        audioCtx.currentTime + duration
      );

      o.stop(audioCtx.currentTime + duration);

    } catch (e) {}
  }


  function addScore(n) {

    score += n;
    high = Math.max(high, score);

    scoreNode.textContent = String(score).padStart(2, "0");
    highNode.textContent = String(high).padStart(2, "0");
  }


  function setDirection(key) {

    if (dirs[key]) {
      pac.want = key;
    }
  }


  // --------------------------------------------------
  // PAC-MAN MOVEMENT
  // --------------------------------------------------

  function movePac() {

    // Turns are buffered and can only happen at the center of a tile.
    if (atNode(pac)) {

      pac.x = snap(pac.x);
      pac.y = snap(pac.y);

      // Turn only if the requested corridor is open.
      if (
        pac.want &&
        canGo(pac.x, pac.y, pac.want)
      ) {
        pac.dir = pac.want;
      }

      // Stop if the next tile is a wall.
      if (
        !pac.dir ||
        !canGo(pac.x, pac.y, pac.dir)
      ) {
        pac.dir = null;
        return;
      }
    }

    if (!pac.dir) {
      return;
    }

    const d = dirs[pac.dir];

    // Faster movement: 0.105 tiles per simulation frame.
    // Movement is only started after checking the next tile.
    pac.x += d.x * 0.105;
    pac.y += d.y * 0.105;

    wrapTunnel(pac);

    mouthPhase += 0.38;
  }


  // --------------------------------------------------
  // GHOST AI
  // --------------------------------------------------

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
      ? {x: pac.x, y: pac.y}
      : {x: 1, y: ROWS - 2};
  }


  function moveGhost(g) {

    if (atNode(g)) {

      g.x = snap(g.x);
      g.y = snap(g.y);

      const reverse = {
        left: "right",
        right: "left",
        up: "down",
        down: "up"
      };

      let choices = Object.keys(dirs).filter(
        d => d !== reverse[g.dir] && canGo(g.x, g.y, d)
      );

      if (
        !choices.length &&
        canGo(g.x, g.y, reverse[g.dir])
      ) {
        choices = [reverse[g.dir]];
      }

      if (choices.length) {

        if (
          Date.now() < frightenedUntil &&
          !g.returning
        ) {

          g.dir = choices[
            Math.floor(Math.random() * choices.length)
          ];

        } else {

          const t = targetForGhost(g);

          choices.sort((a, b) => {

            const da = dirs[a];
            const db = dirs[b];

            return (
              Math.hypot(
                g.x + da.x - t.x,
                g.y + da.y - t.y
              ) -
              Math.hypot(
                g.x + db.x - t.x,
                g.y + db.y - t.y
              )
            );
          });

          g.dir = choices[0];
        }

      } else {

        g.dir = null;
      }
    }


    if (g.dir) {

      const d = dirs[g.dir];

      const speed = g.returning
        ? 0.14
        : (Date.now() < frightenedUntil ? 0.055 : 0.075);

      g.x += d.x * speed;
      g.y += d.y * speed;

      wrapTunnel(g);
    }


    if (
      g.returning &&
      Math.hypot(g.x - g.homeX, g.y - g.homeY) < 0.35
    ) {

      g.returning = false;
      g.x = g.homeX;
      g.y = g.homeY;
    }
  }


  // --------------------------------------------------
  // DOTS, POWER PELLETS AND FRUIT
  // --------------------------------------------------

  function collect() {

    const px = Math.round(pac.x);
    const py = Math.round(pac.y);

    const i = dots.findIndex(
      p => p.x === px && p.y === py
    );

    if (i >= 0) {

      dots.splice(i, 1);

      addScore(10);

      playTone(
        300 + (frame % 2) * 80,
        0.025
      );
    }


    const j = powerDots.findIndex(
      p => p.x === px && p.y === py
    );

    if (j >= 0) {

      powerDots.splice(j, 1);

      addScore(50);

      frightenedUntil = Date.now() + 8000;
      ghostCombo = 0;

      ghosts.forEach(g => {
        if (!g.returning) {
          g.frightened = true;
        }
      });

      playTone(180, 0.3, "sawtooth", 0.04);
    }


    if (
      dots.length < dotsInitial / 2 &&
      !fruit.visible &&
      !fruit.eaten
    ) {

      fruit.visible = true;
      fruitUntil = Date.now() + 7000;
    }


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


    if (
      fruit.visible &&
      Date.now() > fruitUntil
    ) {
      fruit.visible = false;
    }


    // Move to the next level when all pellets are collected.
    if (
      dots.length === 0 &&
      powerDots.length === 0
    ) {

      level++;

      levelNode.textContent = level;

      frightenedUntil = 0;

      initLevel();

      dotsInitial = dots.length;

      message.textContent = "LEVEL " + level + " — READY!";
    }
  }


  // --------------------------------------------------
  // COLLISIONS AND LIVES
  // --------------------------------------------------

  function hitTest() {

    for (const g of ghosts) {

      if (g.returning) {
        continue;
      }

      if (
        Math.hypot(
          pac.x - g.x,
          pac.y - g.y
        ) < 0.58
      ) {

        if (Date.now() < frightenedUntil) {

          g.returning = true;

          ghostCombo++;

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


  function loseLife() {

    lives--;

    if (lives <= 0) {

      running = false;
      gameEnded = true;

      message.textContent = "GAME OVER — PRESS START";

      playTone(90, 0.5, "sawtooth");

    } else {

      message.textContent = "READY!";

      resetActors();
    }
  }


  // --------------------------------------------------
  // DRAWING
  // --------------------------------------------------

  function drawWall(x, y) {

    const px = x * TILE;
    const py = y * TILE;

    ctx.strokeStyle = "#245bff";
    ctx.lineWidth = 2.2;

    ctx.fillStyle = "#000";

    ctx.fillRect(
      px,
      py,
      TILE,
      TILE
    );

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

    // Ghost-house gate decoration.
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


    powerDots.forEach(p => {

      const r = 4 + Math.sin(Date.now() / 110) * 1.2;

      ctx.fillStyle = "#fff1cf";

      ctx.beginPath();

      ctx.arc(
        (p.x + 0.5) * TILE,
        (p.y + 0.5) * TILE,
        r,
        0,
        Math.PI * 2
      );

      ctx.fill();
    });


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


  function drawPac() {

    const d = dirs[
      pac.dir || pac.want || "left"
    ];

    const x = (pac.x + 0.5) * TILE;
    const y = (pac.y + 0.5) * TILE;

    const open = 0.18 + Math.abs(
      Math.sin(mouthPhase)
    ) * 0.38;

    ctx.fillStyle = "#ffe500";

    ctx.beginPath();

    ctx.moveTo(x, y);

    ctx.arc(
      x,
      y,
      8.5,
      d.angle + open,
      d.angle + Math.PI * 2 - open
    );

    ctx.closePath();

    ctx.fill();
  }


  function drawGhost(g) {

    const x = (g.x + 0.5) * TILE;
    const y = (g.y + 0.5) * TILE;

    const frightened =
      Date.now() < frightenedUntil &&
      !g.returning;

    const color = g.returning
      ? "#fff"
      : (frightened ? "#1748d8" : g.color);

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

      ctx.fillStyle = "#fff";

      const look = dirs[g.dir] || dirs.left;

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

      ctx.fillStyle = "#fff";

      ctx.fillRect(x - 5, y - 2, 3, 2);
      ctx.fillRect(x + 2, y - 2, 3, 2);
    }
  }


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


  // --------------------------------------------------
  // GAME RENDERING
  // --------------------------------------------------

  function render() {

    drawMaze();
    drawDots();
    drawPac();

    ghosts.forEach(drawGhost);

    drawLives();

    if (paused) {
      overlay("PAUSED");
    }

    if (!running && !gameEnded) {
      overlay("READY!");
    }

    if (gameEnded) {
      overlay("GAME OVER");
    }
  }


  function overlay(text) {

    ctx.fillStyle = "rgba(0,0,0,.72)";

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


  // --------------------------------------------------
  // GAME LOOP
  // --------------------------------------------------

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

    message.textContent = " ";
  }


  function loop(t) {

    const dt = Math.min(
      t - lastTime,
      100
    );

    lastTime = t;

    accumulator += dt;

    while (accumulator >= STEP) {

      tick();

      accumulator -= STEP;
    }

    render();

    requestAnimationFrame(loop);
  }


  // --------------------------------------------------
  // START / RESTART
  // --------------------------------------------------

  function startGame() {

    score = 0;
    lives = 3;
    level = 1;

    gameEnded = false;
    paused = false;
    running = true;

    frightenedUntil = 0;
    ghostCombo = 0;

    scoreNode.textContent = "00";
    levelNode.textContent = "1";

    initLevel();

    dotsInitial = dots.length;

    message.textContent = "READY!";

    canvas.focus();

    playTone(520, 0.12);
  }


  // --------------------------------------------------
  // KEYBOARD CONTROLS
  // --------------------------------------------------

  function keyHandler(e) {

    const mapKey = {

      ArrowLeft: "left",
      a: "left",
      A: "left",

      ArrowRight: "right",
      d: "right",
      D: "right",

      ArrowUp: "up",
      w: "up",
      W: "up",

      ArrowDown: "down",
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
          : " ";
      }
    }
  }


  window.addEventListener(
    "keydown",
    keyHandler
  );


  canvas.addEventListener(
    "pointerdown",
    () => canvas.focus()
  );


  // Start button.
  document.getElementById("start").addEventListener(
    "click",
    startGame
  );


  // Sound button.
  document.getElementById("sound").addEventListener(
    "click",
    e => {

      soundOn = !soundOn;

      e.target.textContent =
        "SOUND: " + (soundOn ? "ON" : "OFF");
    }
  );


  // Initialize the game.
  initLevel();

  dotsInitial = dots.length;

  render();

  requestAnimationFrame(loop);

})();
</script>
"""

st.components.v1.html(
    html,
    height=760,
    scrolling=False
)

st.caption(
    "This is an original browser-based arcade-style recreation with classic Pac-Man "
    "mechanics and a 28 × 31 maze. It does not use the original arcade ROM or proprietary assets."
)
