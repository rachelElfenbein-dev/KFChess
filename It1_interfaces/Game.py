import inspect
import pathlib
import queue, threading, time, cv2, math
from typing import List, Dict, Tuple, Optional
from It1_interfaces.Board import Board
from It1_interfaces.Command import Command
from It1_interfaces.Piece import Piece
from It1_interfaces. img import Img


class InvalidBoard(Exception): ...
# ────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self, pieces: List[Piece], board: Board):
        """Initialize the game with pieces, board, and optional event bus."""
        self.pieces = {p.piece_id: p for p in pieces}
        self.board = board
        self.user_input_queue = queue.Queue()
        self.running = True

    # ─── helpers ─────────────────────────────────────────────────────────────
    def game_time_ms(self) -> int:
        """Return the current game time in milliseconds."""
        return int(time.monotonic() * 1000)

    def clone_board(self) -> Board:
        """
        Return a **brand-new** Board wrapping a copy of the background pixels
        so we can paint sprites without touching the pristine board.
        """
        return self.board.clone()

    def start_user_input_thread(self):
        """Start the user input thread for mouse handling."""
        def user_input_listener():
            while self.running:
                # Simulate user input (replace with actual input handling)
                time.sleep(0.1)
                # Example: Add a dummy command to the queue
                cmd = Command(piece_id="example_piece", type="Move", params=[])
                self.user_input_queue.put(cmd)

        threading.Thread(target=user_input_listener, daemon=True).start()

    # ─── main public entrypoint ──────────────────────────────────────────────
    def run(self):
        """Main game loop."""
        self.start_user_input_thread()

        start_ms = self.game_time_ms()
        for p in self.pieces.values():
            p.reset(start_ms)

        # ─────── main loop ──────────────────────────────────────────────────
        while not self._is_win():
            now = self.game_time_ms()  # monotonic time ! not computer time.

            # (1) update physics & animations
            for p in self.pieces.values():
                p.update(now)

            # (2) handle queued Commands from mouse thread
            while not self.user_input_queue.empty():
                cmd: Command = self.user_input_queue.get()
                self._process_input(cmd)

            # (3) draw current position
            self._draw()
            if not self._show():  # returns False if user closed window
                break

            # (4) detect captures
            self._resolve_collisions()

        self._announce_win()
        cv2.destroyAllWindows()

    # ─── drawing helpers ────────────────────────────────────────────────────
    def _process_input(self, cmd: Command):
        """Process user input commands."""
        if cmd.piece_id in self.pieces:
            self.pieces[cmd.piece_id].on_command(cmd)

    def _draw(self):
        """Draw the current game state."""
        board_img = self.clone_board().get_image()
        for p in self.pieces.values():
            p.draw(board_img)
        cv2.imshow("Game", board_img)

    def _show(self) -> bool:
        """Show the current frame and handle window events."""
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC key
            self.running = False
            return False
        return True

    # ─── capture resolution ────────────────────────────────────────────────
    def _resolve_collisions(self):
        """Resolve piece collisions and captures."""
        for piece1 in self.pieces.values():
            for piece2 in self.pieces.values():
                if piece1 != piece2 and piece1.can_capture(piece2):
                    if piece2.can_be_captured():
                        piece2.capture()

    # ─── board validation & win detection ───────────────────────────────────
    def _is_win(self) -> bool:
        """Check if the game has ended."""
        # Example: Check if only one piece remains
        remaining_pieces = [p for p in self.pieces.values() if not p.is_captured()]
        return len(remaining_pieces) <= 1

    def _announce_win(self):
        """Announce the winner."""
        remaining_pieces = [p for p in self.pieces.values() if not p.is_captured()]
        if remaining_pieces:
            print(f"The winner is: {remaining_pieces[0].piece_id}")
        else:
            print("No winner!")