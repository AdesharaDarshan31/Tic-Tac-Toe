import streamlit as st
from PIL import Image
import base64
import pygame
import random
from ai import best_move, check_winner, is_full

# ---------------- SOUND ---------------- #
def play_sound(file_path):
    try:
        if not pygame.mixer.get_init():
            with open(file_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            st.markdown(
                f"""
                <script>
                var audio = new Audio("data:audio/wav;base64,{encoded}");
                audio.volume = 0.85;
                audio.play();
                </script>
                """,
                unsafe_allow_html=True
            )
        else:
            pygame.mixer.Sound(file_path).play()
    except:
        pass

try:
    pygame.mixer.init()
except:
    pass

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(page_title="Tic Tac Toe", page_icon="🎮", layout="wide")

x_img = Image.open("assets/x.png")
o_img = Image.open("assets/o.png")

SND_CLICK = "assets/click.wav"
SND_WIN = "assets/win.wav"
SND_DRAW = "assets/draw.wav"
SND_LOSE = "assets/lose.wav"

# ---------------- CSS ---------------- #
st.markdown("""
<style>

.stApp{
  background:linear-gradient(120deg,#0f2027,#203a43,#2c5364);
  background-size:200% 200%;
  animation:bgFlow 20s ease infinite;
  font-family:"Poppins",sans-serif;color:#e8faff;
}

@keyframes bgFlow{
  0%{background-position:0% 50%}
  50%{background-position:100% 50%}
  100%{background-position:0% 50%}
}

.app-title{
  display:flex;align-items:center;justify-content:center;gap:12px;
  margin-top:40px;margin-bottom:20px;
  font-size:50px;font-weight:900;
  background:linear-gradient(90deg,#00d2ff,#3a7bd5);
  -webkit-background-clip:text;color:#00d2ff;
  text-shadow:0 0 25px rgba(0,210,255,0.6);
}

.menu-title{
  text-align:center;font-size:38px;font-weight:800;color:#00d2ff;
  text-shadow:0 0 20px #00d2ff;margin-bottom:20px;
}

.stButton>button{
  height:80px;width:220px;font-size:22px;font-weight:600;border-radius:12px;
  margin:10px;background:linear-gradient(135deg,#232526,#414345);
  color:#e8faff;border:2px solid #00d2ff;transition:.3s;
  box-shadow:0 0 10px rgba(0,210,255,0.3);
}
.stButton>button:hover{
  background:linear-gradient(135deg,#00c6ff,#0072ff);
  transform:scale(1.07);
  box-shadow:0 0 25px rgba(0,210,255,0.7);
  color:#fff;
}

.turn-text{text-align:center;color:#00d2ff;font-size:24px;font-weight:700;margin:10px 0;}
.win-text{text-align:center;color:#FFD54A;font-size:28px;font-weight:900;text-shadow:0 0 25px #FFD54A;margin:10px 0;}

.score-card{
  background:rgba(255,255,255,0.06);border-radius:12px;padding:25px;width:250px;
  text-align:center;box-shadow:0 0 10px rgba(0,255,255,0.1);backdrop-filter:blur(10px);
}
.score-title{font-size:22px;font-weight:800;color:#00d2ff;text-shadow:0 0 10px #00d2ff;}
.score-line{display:flex;justify-content:space-between;color:#fff;font-size:17px;margin:6px 0;}
.score-hr{height:1px;background:#00d2ff;margin:10px 0;}

</style>
""", unsafe_allow_html=True)

# ---------------- STATE ---------------- #
def new_board():
    return [[" " for _ in range(3)] for _ in range(3)]

defaults = {
    "board": new_board(),
    "current_player": "X",
    "mode": None,
    "player1": "Player 1",
    "player2": "Player 2",
    "difficulty": "Medium",
    "difficulty_js": "",
    "game_over": False,
    "winner": None,
    "winning_cells": [],
    "score_x": 0,
    "score_o": 0,
    "draws": 0,
    "matches": 0,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def reset(full=False):
    st.session_state.board = new_board()
    st.session_state.current_player = "X"
    st.session_state.game_over = False
    st.session_state.winner = None

    if full:
        for key in ["score_x","score_o","draws","matches"]:
            st.session_state[key] = 0
        st.session_state.mode = None
        st.session_state.difficulty = "Medium"

# ---------------- AI LOGIC ---------------- #
def get_ai_move(board):
    empty = [(i, j) for i in range(3) for j in range(3) if board[i][j] == " "]
    if not empty:
        return None

    diff = st.session_state.difficulty

    if diff == "Easy":
        return random.choice(empty)

    if diff == "Medium":
        return best_move(board) if random.random() < 0.5 else random.choice(empty)

    return best_move(board) or random.choice(empty)


def ai_turn():
    mv = get_ai_move(st.session_state.board)
    if mv:
        st.session_state.board[mv[0]][mv[1]] = "O"

    winner = check_winner(st.session_state.board)
    if winner:
        st.session_state.winner = winner
        st.session_state.score_o += 1
        st.session_state.matches += 1
        st.session_state.game_over = True
        play_sound(SND_LOSE)
        return

    if is_full(st.session_state.board):
        st.session_state.draws += 1
        st.session_state.matches += 1
        st.session_state.game_over = True
        play_sound(SND_DRAW)
        return

    st.session_state.current_player = "X"

# ---------------- MOVE HANDLER ---------------- #
def move(i, j):
    if st.session_state.game_over:
        return
    if st.session_state.board[i][j] != " ":
        return

    st.session_state.board[i][j] = st.session_state.current_player
    play_sound(SND_CLICK)

    winner = check_winner(st.session_state.board)
    if winner:
        st.session_state.winner = winner
        st.session_state.matches += 1
        st.session_state.game_over = True

        if winner == "X":
            st.session_state.score_x += 1
            play_sound(SND_WIN)
        else:
            st.session_state.score_o += 1
            play_sound(SND_LOSE)
        return

    if is_full(st.session_state.board):
        st.session_state.draws += 1
        st.session_state.matches += 1
        st.session_state.game_over = True
        play_sound(SND_DRAW)
        return

    if st.session_state.mode == "2P":
        st.session_state.current_player = "O" if st.session_state.current_player == "X" else "X"
    else:
        st.session_state.current_player = "O"
        ai_turn()

# ---------------- TITLE ---------------- #
st.markdown("<div class='app-title'>Tic Tac Toe 🎮</div>", unsafe_allow_html=True)

# ---------------- MODE SELECT ---------------- #
if st.session_state.mode is None:

    st.markdown("<div class='menu-title'>Choose Game Mode</div>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,2,1])

    with c2:
        left,right = st.columns(2)
        if left.button("👤 Player vs AI"):
            st.session_state.mode="AI_SETUP"
            st.session_state.player1="You"
            st.session_state.player2="AI"
            st.rerun()

        if right.button("👥 2 Player Mode"):
            st.session_state.mode="2P_SETUP"
            st.rerun()

# ---------------- AI DIFFICULTY ---------------- #
elif st.session_state.mode == "AI_SETUP":

    st.markdown("<div class='menu-title'>😊 Choose Difficulty</div>", unsafe_allow_html=True)

    # JS WRITES difficulty HERE
    if st.session_state.difficulty_js:
        st.session_state.difficulty = st.session_state.difficulty_js
        st.session_state.difficulty_js = ""
        st.rerun()

    diffs = ["Easy","Medium","Hard"]

    html = "<div style='display:flex;justify-content:center;gap:40px;margin-top:20px;margin-bottom:45px;'>"

    for diff in diffs:
        active = (st.session_state.difficulty == diff)

        html += f"""
        <button 
            onclick="document.getElementById('diff_input').value='{diff}';
                     document.getElementById('diff_form').submit();"
            style="
                width:220px;
                height:80px;
                font-size:22px;
                font-weight:700;
                border-radius:12px;
                border:2px solid #00d2ff;
                cursor:pointer;
                transition:.3s;
                background:linear-gradient(135deg,#232526,#414345);
                color:#e8faff;
                box-shadow:0 0 12px rgba(0,210,255,0.4);
                {
                    'background:linear-gradient(135deg,#00c6ff,#0072ff);color:white;box-shadow:0 0 35px rgba(0,210,255,1);'
                    if active else ''
                }
            "
        >{diff}</button>
        """

    html += "</div>"

    st.components.v1.html(html, height=200)

    # hidden auto-submitting form
    st.components.v1.html("""
        <form id="diff_form" method="post">
            <input type="hidden" id="diff_input" name="difficulty_js">
        </form>
    """, height=0)

    # Streamlit sees POST data here
    if "difficulty_js" in st.session_state:
        pass

    # START / BACK
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        a,b = st.columns(2)
        if a.button("Start Game"):
            st.session_state.mode="AI"
            reset(full=False)
            st.rerun()

        if b.button("Back"):
            reset(full=True)
            st.rerun()

# ---------------- 2P SETUP ---------------- #
elif st.session_state.mode == "2P_SETUP":

    st.markdown("<div class='menu-title'>👥 Enter Player Names</div>", unsafe_allow_html=True)

    p1 = st.text_input("Player 1 (X):", st.session_state.player1)
    p2 = st.text_input("Player 2 (O):", st.session_state.player2)

    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        a,b = st.columns(2)

        if a.button("Start"):
            st.session_state.player1 = p1 or "Player 1"
            st.session_state.player2 = p2 or "Player 2"
            st.session_state.mode="2P"
            reset(full=False)
            st.rerun()

        if b.button("Back"):
            reset(full=True)
            st.rerun()

# ---------------- GAME ---------------- #
else:

    game,score = st.columns([4,1])

    with game:

        if not st.session_state.game_over:
            name = st.session_state.player1 if st.session_state.current_player=="X" else st.session_state.player2
            st.markdown(f"<div class='turn-text'>🎯 Turn: {name} ({st.session_state.current_player})</div>", unsafe_allow_html=True)
        else:
            if st.session_state.winner:
                name = st.session_state.player1 if st.session_state.winner=="X" else st.session_state.player2
                st.markdown(f"<div class='win-text'>🏆 {name} Wins!</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='win-text'>It's a Draw!</div>", unsafe_allow_html=True)

        for i in range(3):
            row = st.columns(3)
            for j in range(3):
                val = st.session_state.board[i][j]
                with row[j]:
                    if val=="X":
                        st.image(x_img, width=80)
                    elif val=="O":
                        st.image(o_img, width=80)
                    else:
                        if st.button(" ", key=f"{i}-{j}"):
                            move(i,j)
                            st.rerun()

        r1,r2 = st.columns(2)
        if r1.button("🔄 Play Again"):
            reset(full=False); st.rerun()
        if r2.button("🏠 Back to Menu"):
            reset(full=True); st.rerun()

    with score:
        st.markdown("<div class='score-card'>", unsafe_allow_html=True)
        st.markdown("<div class='score-title'>🏆 Scoreboard</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='score-line'><span>{st.session_state.player1}</span><span>{st.session_state.score_x}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='score-line'><span>{st.session_state.player2}</span><span>{st.session_state.score_o}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='score-line'><span>Draws</span><span>{st.session_state.draws}</span></div>", unsafe_allow_html=True)
        st.markdown("<div class='score-hr'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='score-line'><span>Matches</span><span>{st.session_state.matches}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
