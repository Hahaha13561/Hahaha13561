import os
import json
import re
import chess
import chess.svg

STATE_FILE = "chess_state.json"
BOARD_SVG = "chess_board.svg"

def main():
    issue_title = os.environ.get("ISSUE_TITLE", "")
    issue_author = os.environ.get("ISSUE_AUTHOR", "").lower()
    repo_owner = os.environ.get("REPO_OWNER", "").lower()
    print(f"Processing issue by {issue_author}: {issue_title}")
    
    # 1. Load table status or start a game
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                board = chess.Board(data.get("fen", chess.STARTING_FEN))
        except Exception:
            board = chess.Board()
    else:
        board = chess.Board()

    # 2. If reset
    if "chess|reset" in issue_title.lower():
        if issue_author == repo_owner:
            board = chess.Board()
            print("Board reset.")
        else:
            print(f"Reset rejected: {issue_author} is not authorized.")
        board = chess.Board()
    else:
        # Catch the move
        match = re.search(r"chess\|move:\s*([a-h][1-8][a-h][1-8]|[a-zA-Z0-9+#=]+)", issue_title, re.IGNORECASE)
        if match:
            move_str = match.group(1).strip()
            move = None
            
            # try UCI format
            try:
                move = chess.Move.from_uci(move_str)
                if move not in board.legal_moves:
                    move = None
            except ValueError:
                pass

            # try SAN formatı
            if not move:
                try:
                    move = board.parse_san(move_str)
                except ValueError:
                    pass

            # Apply if valid
            if move and move in board.legal_moves:
                board.push(move)
                print(f"Move made: {move}")
            else:
                print(f"Illegal move: {move_str}")

    # 3. If game is over reset automatically
    if board.is_game_over():
        print(f"Game over. {board.result()}")

    # 4. Save last state
    with open(STATE_FILE, "w") as f:
        json.dump({"fen": board.fen()}, f)

    # 5. Write SVG and save
    svg_content = chess.svg.board(board=board, size=450)
    with open(BOARD_SVG, "w") as f:
        f.write(svg_content)

if __name__ == "__main__":
    main()