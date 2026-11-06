    ctx.fillStyle="#000";
    ctx.fillRect(px,py,TILE,TILE);
    ctx.strokeRect(px+1.5,py+1.5,TILE-3,TILE-3);
  }
  function drawMaze() {
    ctx.fillStyle="#000"; ctx.fillRect(0,0,W,H);
    for(let y=0;y<ROWS;y++) for(let x=0;x<COLS;x++) if(walls[y][x]) drawWall(x,y);
    // Ghost-house gate.
    ctx.strokeStyle="#ff9de2"; ctx.lineWidth=2;
    ctx.beginPath(); ctx.moveTo(10*TILE,13*TILE+TILE/2); ctx.lineTo(18*TILE,13*TILE+TILE/2); ctx.stroke();
  }
  function drawDots() {
    ctx.fillStyle="#ffd8a8";
    dots.forEach(p=>{ctx.beginPath();ctx.arc((p.x+.5)*TILE,(p.y+.5)*TILE,2,0,Math.PI*2);ctx.fill();});
    powerDots.forEach(p=>{
      const r=4+Math.sin(Date.now()/110)*1.2;
      ctx.fillStyle="#fff1cf";ctx.beginPath();ctx.arc((p.x+.5)*TILE,(p.y+.5)*TILE,r,0,Math.PI*2);ctx.fill();
    });
    if(fruit.visible) {
      ctx.fillStyle="#ff3030";ctx.beginPath();ctx.arc((fruit.x+.5)*TILE,(fruit.y+.5)*TILE,6,0,Math.PI*2);ctx.fill();
      ctx.fillStyle="#45e05a";ctx.fillRect((fruit.x+.5)*TILE,(fruit.y+.5)*TILE-9,2,5);
    }
  }
  function drawPac() {
    const d=dirs[pac.dir||pac.want||"left"];
    const x=(pac.x+.5)*TILE, y=(pac.y+.5)*TILE;
    const open=0.18+Math.abs(Math.sin(mouthPhase))*0.38;
    ctx.fillStyle="#ffe500";ctx.beginPath();ctx.moveTo(x,y);
    ctx.arc(x,y,8.5,d.angle+open,d.angle+Math.PI*2-open);ctx.closePath();ctx.fill();
  }
  function drawGhost(g) {
    const x=(g.x+.5)*TILE, y=(g.y+.5)*TILE;
    const frightened=Date.now()<frightenedUntil && !g.returning;
    const color=g.returning?"#fff":(frightened?"#1748d8":g.color);
    ctx.fillStyle=color;
    ctx.beginPath();ctx.arc(x,y-1,8,Math.PI,0);ctx.lineTo(x+8,y+8);
    ctx.lineTo(x+4,y+5);ctx.lineTo(x,y+8);ctx.lineTo(x-4,y+5);
    ctx.lineTo(x-8,y+8);ctx.closePath();ctx.fill();
    if(!g.returning) {
      ctx.fillStyle="#fff";
      const look=dirs[g.dir]||dirs.left;
      ctx.beginPath();
      ctx.ellipse(x-3+look.x*1.5,y-2+look.y*1.5,2.5,3.2,0,0,Math.PI*2);
      ctx.ellipse(x+3+look.x*1.5,y-2+look.y*1.5,2.5,3.2,0,0,Math.PI*2);ctx.fill();
      ctx.fillStyle="#111";
      ctx.beginPath();
      ctx.arc(x-3+look.x*2,y-2+look.y*2,1.2,0,Math.PI*2);
      ctx.arc(x+3+look.x*2,y-2+look.y*2,1.2,0,Math.PI*2);ctx.fill();
    } else {
      ctx.fillStyle="#fff";ctx.fillRect(x-5,y-2,3,2);ctx.fillRect(x+2,y-2,3,2);
    }
  }
  function drawLives() {
    ctx.fillStyle="#ffe500";
    for(let i=0;i<lives;i++) {
      const x=12+i*22,y=H-8;
      ctx.beginPath();ctx.moveTo(x,y);ctx.arc(x,y,7,0.35,Math.PI*2-0.35);ctx.closePath();ctx.fill();
    }
  }
  function render() {
    drawMaze(); drawDots(); drawPac(); ghosts.forEach(drawGhost); drawLives();
    if(paused) overlay("PAUSED");
    if(!running && !gameEnded) overlay("READY!");
    if(gameEnded) overlay("GAME OVER");
  }
  function overlay(text) {
    ctx.fillStyle="rgba(0,0,0,.72)";ctx.fillRect(0,H/2-28,W,56);
    ctx.fillStyle="#ffe500";ctx.font="bold 25px monospace";ctx.textAlign="center";
    ctx.fillText(text,W/2,H/2+9);
  }
  function tick() {
    if(!running||paused||gameEnded) return;
    frame++;
    movePac();
    ghosts.forEach(moveGhost);
    collect();
    hitTest();
    if(Date.now()>frightenedUntil) ghosts.forEach(g=>g.frightened=false);
    message.textContent=" ";
  }
  function loop(t) {
    const dt=Math.min(t-lastTime,100); lastTime=t; accumulator+=dt;
    while(accumulator>=STEP) { tick(); accumulator-=STEP; }
    render();
    requestAnimationFrame(loop);
  }
  function startGame() {
    score=0;lives=3;level=1;gameEnded=false;paused=false;running=true;
    frightenedUntil=0;ghostCombo=0;scoreNode.textContent="00";levelNode.textContent="1";
    initLevel(); dotsInitial=dots.length;
    message.textContent="READY!";
    canvas.focus();
    playTone(520,0.12);
  }
  function keyHandler(e) {
    const mapKey={ArrowLeft:"left",a:"left",A:"left",ArrowRight:"right",d:"right",D:"right",
      ArrowUp:"up",w:"up",W:"up",ArrowDown:"down",s:"down",S:"down"};
    if(mapKey[e.key]) {e.preventDefault();setDirection(mapKey[e.key]);}
    if(e.code==="Space") {e.preventDefault();if(running&&!gameEnded){paused=!paused;message.textContent=paused?"PAUSED":" ";}}
  }
  window.addEventListener("keydown",keyHandler);
  canvas.addEventListener("pointerdown",()=>canvas.focus());
  document.getElementById("start").addEventListener("click",startGame);
  document.getElementById("sound").addEventListener("click",e=>{
    soundOn=!soundOn;e.target.textContent="SOUND: "+(soundOn?"ON":"OFF");
  });

  initLevel(); dotsInitial=dots.length; render();
  requestAnimationFrame(loop);
})();
</script>
"""

st.components.v1.html(html, height=690, scrolling=False)

st.caption(
    "This is an original browser-based arcade-style recreation with classic Pac-Man "
    "mechanics and a 28 × 31 maze. It does not use the original arcade ROM or proprietary assets."
)
