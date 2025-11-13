import streamlit as st
from PIL import Image
import base64
import pygame
import os

def play_sound(file_path):
    """Play sound locally with pygame; fallback to browser audio online."""
    try:
        # Detect Streamlit Cloud or limited environment
        if "streamlit" in os.getenv("HOME", "").lower() or not pygame.mixer.get_init():
            with open(file_path, "rb") as f:
                data = f.read()
            b64 = base64.b64encode(data).decode()
            sound_html = f"""
            <script>
            setTimeout(() => {{
                var audio = new Audio("data:audio/wav;base64,{b64}");
                audio.volume = 0.8;
                audio.play();
            }}, 150);
            </script>
            """
            st.markdown(sound_html, unsafe_allow_html=True)
        else:
            pygame.mixer.Sound(file_path).play()
    except Exception as e:
        print("⚠️ Could not play sound:", e)


from ai import best_move, check_winner, is_full

try:
    pygame.mixer.init()
except Exception as e:
    print("⚠️ Pygame mixer not available, using browser sound only.")

st.set_page_config(page_title="Tic Tac Toe", page_icon="🎮", layout="wide")

x_img = Image.open("assets/x.png")
o_img = Image.open("assets/o.png")
SND_CLICK = "assets/click.wav"
SND_WIN = "assets/win.wav"
SND_DRAW = "assets/draw.wav"
SND_LOSE = "assets/lose.wav"

st.markdown("""
<style>

@keyframes floatParticle {
  0%,100%{transform:translateY(0)translateX(0);opacity:0.9;}
  50%{transform:translateY(-30px)translateX(15px);opacity:0.7;}
}
.particle{position:absolute;border-radius:50%;
  background:radial-gradient(circle,rgba(0,255,255,0.8),rgba(0,255,255,0.05));
  box-shadow:0 0 15px rgba(0,255,255,0.5);
  width:8px;height:8px;animation:floatParticle 6s ease-in-out infinite;}
.particle:nth-child(even){animation-duration:9s;}
.particle:nth-child(3n){animation-duration:11s;transform:scale(1.3);}
.particle-container{position:fixed;inset:0;overflow:hidden;z-index:-1;}


@keyframes bgFlow{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
.stApp{
  background:linear-gradient(120deg,#0f2027,#203a43,#2c5364);
  background-size:200% 200%;animation:bgFlow 20s ease infinite;
  font-family:"Poppins",sans-serif;color:#e8faff;
}

.app-title{
  display:flex;align-items:center;justify-content:center;gap:12px;
  margin-top:40px;margin-bottom:20px;
  font-size:50px;font-weight:900;
  background:linear-gradient(90deg,#00d2ff,#3a7bd5);
  -webkit-background-clip:text;
  color:#00d2ff;
  text-shadow:0 0 25px rgba(0,210,255,0.6);
}
.app-title svg{width:45px;height:45px;fill:#00d2ff;
  filter:drop-shadow(0 0 12px rgba(0,210,255,0.8));transition:transform .5s;}
.app-title svg:hover{transform:rotate(10deg)scale(1.1);}

.menu-title{
  font-size:38px;font-weight:800;color:#00d2ff;text-shadow:0 0 20px #00d2ff;
  margin-bottom:40px;text-align:center;
}

.stButton>button{
  height:80px;width:200px;font-size:20px;font-weight:600;border-radius:12px;
  margin:10px;background:linear-gradient(135deg,#232526,#414345);color:#e8faff;
  border:2px solid #00d2ff;transition:.3s;box-shadow:0 0 10px rgba(0,210,255,0.3);
}
.stButton>button:hover{
  background:linear-gradient(135deg,#00c6ff,#0072ff);
  transform:scale(1.07);box-shadow:0 0 25px rgba(0,210,255,0.7);color:#fff;
}

.tile{
  border:2px solid rgba(0,255,255,0.5);background:rgba(255,255,255,0.08);
  border-radius:10px;box-shadow:0 0 15px rgba(0,255,255,0.2);
  transition:.25s;display:flex;justify-content:center;align-items:center;
  height:120px;
}
.tile:hover{box-shadow:0 0 25px rgba(0,255,255,0.5);transform:scale(1.05);}

@keyframes winnerGlow{
  0%{box-shadow:0 0 10px #FFD54A,0 0 20px #FFD54A;}
  50%{box-shadow:0 0 30px #FFD54A,0 0 60px #FFD54A;}
  100%{box-shadow:0 0 10px #FFD54A,0 0 20px #FFD54A;}
}
.winner-cell{animation:winnerGlow 1.5s infinite alternate;border-color:#FFD54A!important;}

.turn-text{text-align:center;color:#00d2ff;font-size:22px;font-weight:600;margin:10px 0 18px;}
.win-text{text-align:center;color:#FFD54A;font-size:26px;font-weight:800;text-shadow:0 0 25px #FFD54A;margin:8px 0 18px;}

.col-score{text-align:center;display:flex;justify-content:center;align-items:center;}
.score-card{
  background:rgba(255,255,255,0.06);border-radius:12px;padding:25px;width:260px;
  text-align:center;box-shadow:0 0 10px rgba(0,255,255,0.1);backdrop-filter:blur(10px);
  margin-top:0;
}
.score-title{font-size:22px;font-weight:800;color:#00d2ff;text-shadow:0 0 10px #00d2ff;margin-bottom:10px;}
.score-line{display:flex;justify-content:space-between;color:#fff;font-size:17px;margin:6px 0;}
.score-hr{height:1px;background:#00d2ff;margin:10px 0;}
</style>

<div class="particle-container">
  <div class="particle" style="top:10%;left:20%;animation-delay:0s;"></div>
  <div class="particle" style="top:30%;left:50%;animation-delay:1s;"></div>
  <div class="particle" style="top:60%;left:70%;animation-delay:2s;"></div>
  <div class="particle" style="top:80%;left:40%;animation-delay:3s;"></div>
  <div class="particle" style="top:50%;left:15%;animation-delay:2s;"></div>
  <div class="particle" style="top:25%;left:75%;animation-delay:4s;"></div>
  <div class="particle" style="top:90%;left:30%;animation-delay:5s;"></div>
  <div class="particle" style="top:10%;left:80%;animation-delay:1.5s;"></div>
  <div class="particle" style="top:40%;left:60%;animation-delay:3.5s;"></div>
  <div class="particle" style="top:70%;left:90%;animation-delay:2.5s;"></div>
</div>
""", unsafe_allow_html=True)

def new_board(): return [[" " for _ in range(3)] for _ in range(3)]
for k, v in {
    "board": new_board(), "current_player": "X", "mode": None,
    "player1": "Player 1", "player2": "Player 2",
    "game_over": False, "winner": None, "winning_cells": [],
    "score_x": 0, "score_o": 0, "draws": 0, "matches": 0
}.items():
    if k not in st.session_state: st.session_state[k] = v

def reset(full=False):
    st.session_state.board = new_board()
    st.session_state.current_player = "X"
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.winning_cells = []
    if full:
        st.session_state.mode = None
        st.session_state.player1, st.session_state.player2 = "Player 1", "Player 2"
        st.session_state.score_x = st.session_state.score_o = st.session_state.draws = st.session_state.matches = 0

def find_winning_cells(b, sym):
    lines = [
        [(0,0),(0,1),(0,2)],[(1,0),(1,1),(1,2)],[(2,0),(2,1),(2,2)],
        [(0,0),(1,0),(2,0)],[(0,1),(1,1),(2,1)],[(0,2),(1,2),(2,2)],
        [(0,0),(1,1),(2,2)],[(0,2),(1,1),(2,0)]
    ]
    for line in lines:
        if all(b[i][j] == sym for i,j in line): return line
    return []

def move(i,j):
    if st.session_state.game_over or st.session_state.board[i][j]!=" ": return
    st.session_state.board[i][j]=st.session_state.current_player
    play_sound(SND_CLICK)
    winner=check_winner(st.session_state.board)
    if winner:
        st.session_state.winner=winner; st.session_state.game_over=True
        st.session_state.winning_cells=find_winning_cells(st.session_state.board,winner)
        st.session_state.matches+=1
        if winner=="X": st.session_state.score_x+=1; play_sound(SND_WIN)
        else: st.session_state.score_o+=1; play_sound(SND_LOSE)
        return
    if is_full(st.session_state.board):
        st.session_state.game_over=True; st.session_state.winner=None
        st.session_state.matches+=1; st.session_state.draws+=1
        play_sound(SND_DRAW); return
    if st.session_state.mode=="2P":
        st.session_state.current_player="O" if st.session_state.current_player=="X" else "X"
    else:
        st.session_state.current_player="O"; ai_turn()

def ai_turn():
    mv=best_move(st.session_state.board)
    if mv:
        st.session_state.board[mv[0]][mv[1]]="O"
        winner=check_winner(st.session_state.board)
        if winner:
            st.session_state.winner=winner; st.session_state.game_over=True
            st.session_state.winning_cells=find_winning_cells(st.session_state.board,winner)
            st.session_state.matches+=1; st.session_state.score_o+=1; play_sound(SND_LOSE)
        elif is_full(st.session_state.board):
            st.session_state.game_over=True; st.session_state.winner=None
            st.session_state.matches+=1; st.session_state.draws+=1; play_sound(SND_DRAW)
        else: st.session_state.current_player="X"

st.markdown("""
<div class='app-title'>
  <span>Tic Tac Toe</span>
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512">
    <path d="M480 0c-52.9 0-96 43.1-96 96v16H256V96c0-52.9-43.1-96-96-96S64 43.1 64 96v48c0 17.7 14.3 32 32 32v80c0 8.8 7.2 16 16 16h80v96c0 17.7 14.3 32 32 32h192c17.7 0 32-14.3 32-32v-96h80c8.8 0 16-7.2 16-16v-80c17.7 0 32-14.3 32-32V96c0-52.9-43.1-96-96-96zM192 160c-26.5 0-48-21.5-48-48s21.5-48 48-48s48 21.5 48 48s-21.5 48-48 48zm256 0c-26.5 0-48-21.5-48-48s21.5-48 48-48s48 21.5 48 48s-21.5 48-48 48z"/>
  </svg>
</div>
""", unsafe_allow_html=True)

if st.session_state.mode is None:
    st.markdown("""
    <div style='display:flex;justify-content:center;'>
        <div class='menu-title'>Choose Your Battle Mode</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2,1,2])
    with c2:
        if st.button("👤 Player vs AI"):
            st.session_state.mode = "AI"
            st.session_state.player1 = "You"
            st.session_state.player2 = "AI"
            st.session_state.needs_rerun = True
        if st.button("👥 2 Player Mode"):
            st.session_state.mode = "2P_SETUP"
            st.session_state.needs_rerun = True

    if st.session_state.get("needs_rerun", False):
        st.session_state.needs_rerun = False
        st.rerun()


elif st.session_state.mode == "2P_SETUP":
    st.markdown("<div class='menu-title'>👥 Enter Player Names</div>", unsafe_allow_html=True)

    p1 = st.text_input("Player 1 Name (X):", value="Player 1")
    p2 = st.text_input("Player 2 Name (O):", value="Player 2")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("✅ Start Game"):
            st.session_state.player1 = p1.strip() or "Player 1"
            st.session_state.player2 = p2.strip() or "Player 2"
            st.session_state.mode = "2P"
            st.rerun()
    with col_b:
        if st.button("⬅️ Back"):
            reset(full=True)
            st.rerun()

else:
    col_game, col_score = st.columns([3,1], gap="large")
    with col_game:
        if not st.session_state.game_over:
            turn = st.session_state.player1 if st.session_state.current_player=="X" else st.session_state.player2
            st.markdown(f"<div class='turn-text'>🎯 Turn: {turn} ({st.session_state.current_player})</div>", unsafe_allow_html=True)
        else:
            if st.session_state.winner:
                winname = st.session_state.player1 if st.session_state.winner=="X" else st.session_state.player2
                st.markdown(f"<div class='win-text'>🏆 {winname} Wins!</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='win-text'>It's a Draw!</div>", unsafe_allow_html=True)

        for i in range(3):
            cols = st.columns(3)
            for j in range(3):
                val = st.session_state.board[i][j]
                klass = "winner-cell" if (i,j) in st.session_state.winning_cells else "tile"
                with cols[j]:
                    if val == "X":
                        st.image(x_img, width=80)
                    elif val == "O":
                        st.image(o_img, width=80)
                    else:
                        if st.button(" ", key=f"{i}-{j}"):
                            move(i, j)
                            st.rerun()

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Play Again"):
                reset(); st.rerun()
        with c2:
            if st.button("🏠 Back to Menu"):
                reset(full=True); st.rerun()

    with col_score:
        st.markdown("<div class='col-score'><div class='score-card'>", unsafe_allow_html=True)
        st.markdown("<div class='score-title'>🏆 Scoreboard</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='score-line'><span>{st.session_state.player1}</span><span>{st.session_state.score_x}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='score-line'><span>{st.session_state.player2}</span><span>{st.session_state.score_o}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='score-line'><span>Draws</span><span>{st.session_state.draws}</span></div>", unsafe_allow_html=True)
        st.markdown("<div class='score-hr'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='score-line'><span>Matches Played</span><span>{st.session_state.matches}</span></div>", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)