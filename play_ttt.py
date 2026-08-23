import os
import json
import re
import random

STATE_FILE = "ttt_state.json"
BOARD_SVG = "ttt_board.svg"

WIN_CONDITIONS = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], # Yatay
    [0, 3, 6], [1, 4, 7], [2, 5, 8], # Dikey
    [0, 4, 8], [2, 4, 6]             # Çapraz
]

def check_winner(board):
    for cond in WIN_CONDITIONS:
        if board[cond[0]] == board[cond[1]] == board[cond[2]] != "":
            return board[cond[0]]
    if "" not in board:
        return "DRAW"
    return None

def get_ai_move(board):
    empty_cells = [i for i, cell in enumerate(board) if cell == ""]
    if not empty_cells:
        return None
    
    for cell in empty_cells:
        temp_board = list(board)
        temp_board[cell] = "O"
        if check_winner(temp_board) == "O":
            return cell
            

    for cell in empty_cells:
        temp_board = list(board)
        temp_board[cell] = "X"
        if check_winner(temp_board) == "X":
            return cell
            

    if 4 in empty_cells:
        return 4
    return random.choice(empty_cells)

def draw_svg(board, status_text=""):
    # Tokyonight Dark Tema renkleri
    bg_color = "#1a1b26"
    line_color = "#414868"
    x_color = "#7aa2f7"
    o_color = "#f7768e"
    text_color = "#c0caf5"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="340" viewBox="0 0 300 340">
  <rect width="300" height="340" fill="{bg_color}" rx="10"/>
  <!-- Izgara Çizgileri -->
  <line x1="100" y1="20" x2="100" y2="280" stroke="{line_color}" stroke-width="4" stroke-linecap="round"/>
  <line x1="200" y1="20" x2="200" y2="280" stroke="{line_color}" stroke-width="4" stroke-linecap="round"/>
  <line x1="20" y1="106" x2="280" y2="106" stroke="{line_color}" stroke-width="4" stroke-linecap="round"/>
  <line x1="20" y1="193" x2="280" y2="193" stroke="{line_color}" stroke-width="4" stroke-linecap="round"/>
'''


    centers = [
        (60, 63),   (150, 63),   (240, 63),
        (60, 150),  (150, 150),  (240, 150),
        (60, 236),  (150, 236),  (240, 236)
    ]

    for i, cell in enumerate(board):
        cx, cy = centers[i]
        if cell == "X":
            svg += f'''  <line x1="{cx-25}" y1="{cy-25}" x2="{cx+25}" y2="{cy+25}" stroke="{x_color}" stroke-width="6" stroke-linecap="round"/>\n'''
            svg += f'''  <line x1="{cx+25}" y1="{cy-25}" x2="{cx-25}" y2="{cy+25}" stroke="{x_color}" stroke-width="6" stroke-linecap="round"/>\n'''
        elif cell == "O":
            svg += f'''  <circle cx="{cx}" cy="{cy}" r="25" stroke="{o_color}" stroke-width="6" fill="none"/>\n'''

    if status_text:
        svg += f'''  <text x="150" y="315" font-family="sans-serif" font-size="14" font-weight="bold" fill="{text_color}" text-anchor="middle">{status_text}</text>\n'''

    svg += '</svg>'
    return svg

def main():
    issue_title = os.environ.get("ISSUE_TITLE", "")
    issue_author = os.environ.get("ISSUE_AUTHOR", "").lower()
    repo_owner = os.environ.get("REPO_OWNER", "").lower()


    board = [""] * 9
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                board = data.get("board", [""] * 9)
        except Exception:
            board = [""] * 9

    status_msg = "Sıra Sizde! (X)"


    if "ttt|reset" in issue_title.lower():
        if issue_author == repo_owner:
            board = [""] * 9
            status_msg = "Game Reset."
        else:
            status_msg = "Unauthorized."
    else:
        match = re.search(r"ttt\|move:\s*([1-9])", issue_title, re.IGNORECASE)
        if match:
            move_idx = int(match.group(1)) - 1
            

            if board[move_idx] == "":
                board[move_idx] = "X"
                winner = check_winner(board)
                
                if winner == "X":
                    status_msg = f"Congrats @{issue_author}, You win! 🎉"
                elif winner == "DRAW":
                    status_msg = "It's a draw!  🤝"
                else:

                    ai_move = get_ai_move(board)
                    if ai_move is not None:
                        board[ai_move] = "O"
                        ai_winner = check_winner(board)
                        if ai_winner == "O":
                            status_msg = "Bot (O) Wins! 🤖"
                        elif ai_winner == "DRAW":
                            status_msg = "It's a draw! 🤝"
                        else:
                            status_msg = "Your turn! (X)"
            else:
                status_msg = "Cell already filled!"

    # Kaydet
    with open(STATE_FILE, "w") as f:
        json.dump({"board": board}, f)

    # SVG Çiz
    svg_out = draw_svg(board, status_msg)
    with open(BOARD_SVG, "w") as f:
        f.write(svg_out)

if __name__ == "__main__":
    main()