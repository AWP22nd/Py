#Simple Tic Tac Toe game with Minimax AI.

# Features:
# - Player vs Player mode.
# - Player vs AI mode (AI uses Minimax and plays optimally).
# - Console interface.

import sys
from typing import List, Optional


def print_board(board: List[str]) -> None:
    """Print the current board state to the console."""
    print("\n")
    print(f" {board[0]} | {board[1]} | {board[2]} ")
    print("---+---+---")
    print(f" {board[3]} | {board[4]} | {board[5]} ")
    print("---+---+---")
    print(f" {board[6]} | {board[7]} | {board[8]} ")
    print("\n")


def check_winner(board: List[str], player: str) -> bool:
    """Check if *player* has won on the given board."""
    winning_combos = [
        (0, 1, 2),  # top row
        (3, 4, 5),  # middle row
        (6, 7, 8),  # bottom row
        (0, 3, 6),  # left column
        (1, 4, 7),  # middle column
        (2, 5, 8),  # right column
        (0, 4, 8),  # diagonal \
        (2, 4, 6),  # diagonal /
    ]
    for a, b, c in winning_combos:
        if board[a] == player and board[b] == player and board[c] == player:
            return True
    return False


def check_tie(board: List[str]) -> bool:
    """Return True if the board is full (no empty spots)."""
    return all(spot != " " for spot in board)


def available_moves(board: List[str]) -> List[int]:
    """Return a list of indices where the spot is empty."""
    return [i for i, spot in enumerate(board) if spot == " "]


def minimax(board: List[str], depth: int, is_maximizing: bool) -> int:
    # Minimax algorithm to evaluate the best move.

    # Returns:
        # +1 if AI (O) wins, -1 if human (X) wins, 0 for tie.
        
    if check_winner(board, "O"):
        return 1
    if check_winner(board, "X"):
        return -1
    if check_tie(board):
        return 0

    if is_maximizing:
        best_score = -float("inf")
        for move in available_moves(board):
            board[move] = "O"
            score = minimax(board, depth + 1, False)
            board[move] = " "  # undo move
            best_score = max(score, best_score)
        return best_score
    else:
        best_score = float("inf")
        for move in available_moves(board):
            board[move] = "X"
            score = minimax(board, depth + 1, True)
            board[move] = " "  # undo move
            best_score = min(score, best_score)
        return best_score


def find_best_move(board: List[str]) -> Optional[int]:
    """Find the best move for the AI using Minimax."""
    best_score = -float("inf")
    move_choice: Optional[int] = None

    for move in available_moves(board):
        board[move] = "O"
        score = minimax(board, 0, False)
        board[move] = " "
        if score > best_score:
            best_score = score
            move_choice = move
    return move_choice


def play_game(mode: str = "pvp") -> None:
    """Main game loop.

    Args:
        mode: "pvp" for Player vs Player, "pve" for Player vs AI.
    """
    board: List[str] = [" "] * 9
    current_player: str = "X"  # Human starts

    while True:
        print_board(board)

        # Human input
        if mode == "pvp" or (mode == "pve" and current_player == "X"):
            try:
                choice = int(input(f"Player {current_player}, choose a position (1-9): ")) - 1
                if choice not in available_moves(board):
                    print("Invalid spot, try again.")
                    continue
            except (ValueError, KeyboardInterrupt):
                print("\nExiting game.")
                sys.exit(0)
        else:
            # AI move
            print("AI is thinking...")
            choice = find_best_move(board) if current_player == "O" else int(
                input(f"Player {current_player}, choose a position (1-9): ")) - 1
            if choice not in available_moves(board):
                # fallback to random empty spot
                choice = available_moves(board)[0]

        # Make the move
        board[choice] = current_player

        # Check for win
        if check_winner(board, current_player):
            print_board(board)
            print(f"🎉 Player {current_player} wins! 🎉")
            break

        # Check for tie
        if check_tie(board):
            print_board(board)
            print("It's a tie!")
            break

        # Switch player
        current_player = "O" if current_player == "X" else "X"


def main() -> None:
    """Entry point: ask for mode and start the game."""
    print("=== Tic Tac Toe ===")
    print("1. Player vs Player")
    print("2. Player vs AI (Minimax)")
    choice = input("Select mode (1 or 2): ").strip()
    if choice == "1":
        play_game(mode="pvp")
    elif choice == "2":
        play_game(mode="pve")
    else:
        print("Invalid choice, exiting.")
        sys.exit(1)


if __name__ == "__main__":
    main()
