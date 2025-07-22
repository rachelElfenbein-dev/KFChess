import inspect
import pathlib
import queue, threading, time, cv2, math
from typing import List, Dict, Tuple, Optional
from It1_interfaces.Board import Board
from It1_interfaces.Command import Command
from It1_interfaces.Piece import Piece
from It1_interfaces.img import Img


class InvalidBoard(Exception): ...
# ────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self, pieces: List[Piece], board: Board):
        """Initialize the game with pieces, board, and optional event bus."""
        self.pieces = {p.piece_id: p for p in pieces}
        self.board = board
        self.user_input_queue = queue.Queue()
        self.running = True
        
        # מצב המשחק
        self.cursor_pos = [0, 0]  # מיקום הקורסור
        self.selected_piece = None  # הכלי הנבחר
        self.current_player = "W"  # שחקן נוכחי - W או B
        
        # הגדרת בעלות חיילים
        for piece_id, piece in self.pieces.items():
            if piece_id.endswith('W'):
                piece.owner = "W"
            elif piece_id.endswith('B'):
                piece.owner = "B"

    # ─── helpers ─────────────────────────────────────────────────────────────
    def game_time_ms(self) -> int:
        """Return the current game time in milliseconds."""
        return int(time.monotonic() * 1000)

    def clone_board(self) -> Board:
        """Return a brand-new Board wrapping a copy of the background pixels."""
        return self.board.clone()

    def get_piece_at(self, pos: Tuple[int, int]) -> Optional[Piece]:
        """מחזיר את הכלי במיקום נתון"""
        for piece in self.pieces.values():
            if piece._state._physics.current_cell == pos:
                return piece
        return None

    def is_valid_move(self, piece: Piece, target_pos: Tuple[int, int]) -> bool:
        """בודק אם תנועה חוקית"""
        current_pos = piece._state._physics.current_cell
        legal_moves = piece._state._moves.get_moves(*current_pos)
        return target_pos in legal_moves

    def can_capture(self, attacker: Piece, target: Piece) -> bool:
        """בודק אם חייל יכול לאכול חייל אחר"""
        if not attacker or not target:
            return False
        if getattr(attacker, 'owner', None) == getattr(target, 'owner', None):
            return False  # לא יכול לאכול חייל של אותו צד
        return True

    def execute_move(self, piece: Piece, target_pos: Tuple[int, int]):
        """מבצע תנועה של חייל"""
        if not self.is_valid_move(piece, target_pos):
            return False

        # בדוק אם יש חייל ביעד
        target_piece = self.get_piece_at(target_pos)
        if target_piece and self.can_capture(piece, target_piece):
            # אכול את החייל היריב
            self.pieces.pop(target_piece.piece_id, None)
            print(f"{piece.piece_id} אכל את {target_piece.piece_id}!")

        # צור פקודה להזיז את החייל
        cmd = Command(
            timestamp=self.game_time_ms(),
            piece_id=piece.piece_id,
            type="Move",
            params=[piece._state._physics.current_cell, target_pos],
            target_cell=target_pos
        )
        
        piece.on_command(cmd, self.game_time_ms())
        return True

    def handle_input(self):
        """טיפול בקלט מהמשתמש באמצעות OpenCV"""
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('w') and self.cursor_pos[0] > 0:
            self.cursor_pos[0] -= 1
            time.sleep(0.1)
        elif key == ord('s') and self.cursor_pos[0] < self.board.H_cells - 1:
            self.cursor_pos[0] += 1
            time.sleep(0.1)
        elif key == ord('a') and self.cursor_pos[1] > 0:
            self.cursor_pos[1] -= 1
            time.sleep(0.1)
        elif key == ord('d') and self.cursor_pos[1] < self.board.W_cells - 1:
            self.cursor_pos[1] += 1
            time.sleep(0.1)
        elif key == ord(' '):  # space
            if self.selected_piece is None:
                # בחר חייל
                piece = self.get_piece_at(tuple(self.cursor_pos))
                if piece and getattr(piece, 'owner', None) == self.current_player:
                    self.selected_piece = piece
                    print(f"נבחר: {piece.piece_id}")
            else:
                # הזז חייל או בטל בחירה
                if tuple(self.cursor_pos) == self.selected_piece._state._physics.current_cell:
                    # בטל בחירה
                    self.selected_piece = None
                    print("בוטלה הבחירה")
                else:
                    # נסה להזיז
                    if self.execute_move(self.selected_piece, tuple(self.cursor_pos)):
                        self.selected_piece = None
                        self.current_player = "B" if self.current_player == "W" else "W"
                        print(f"תור של שחקן {self.current_player}")
                    else:
                        print("תנועה לא חוקית!")
            time.sleep(0.2)
        elif key == 27:  # ESC
            self.running = False

    # ─── main public entrypoint ──────────────────────────────────────────────
    def run(self):
        """Main game loop."""
        start_ms = self.game_time_ms()
        for p in self.pieces.values():
            p.reset(start_ms)

        print("המשחק התחיל! השתמש ב-WASD לתזוזה, SPACE לבחירה/הזזזה, ESC ליציאה")
        cv2.namedWindow("Chess Game", cv2.WINDOW_AUTOSIZE)

        # ─────── main loop ──────────────────────────────────────────────────
        while not self._is_win() and self.running:
            now = self.game_time_ms()

            # (1) update physics & animations
            for p in self.pieces.values():
                p.update(now)

            # (2) handle user input
            self.handle_input()

            # (3) draw current position
            self._draw()
            
            # (4) show and check for exit
            if not self._show():
                break

        self._announce_win()
        cv2.destroyAllWindows()

    # ─── drawing helpers ────────────────────────────────────────────────────
    def _draw(self):
        """Draw the current game state."""
        # התחל עם לוח נקי
        board_copy = self.clone_board()
        
        # צייר חיילים
        for piece in self.pieces.values():
            img_piece = piece._state._graphics.get_img()
            if img_piece is not None:
                row, col = piece._state._physics.current_cell
                x, y = board_copy.get_pixel_position((row, col))
                img_piece.draw_on(board_copy.img, x, y)

        # צייר קורסור
        cursor_x, cursor_y = board_copy.get_pixel_position(tuple(self.cursor_pos))
        cursor_color = (0, 255, 255, 255)  # ציאן
        if self.current_player == "B":
            cursor_color = (255, 255, 0, 255)  # צהוב
        board_copy.img.draw_rect(cursor_x, cursor_y, board_copy.cell_W_pix, 
                                board_copy.cell_H_pix, cursor_color, thickness=3)

        # צייר חייל נבחר
        if self.selected_piece:
            piece_row, piece_col = self.selected_piece._state._physics.current_cell
            piece_x, piece_y = board_copy.get_pixel_position((piece_row, piece_col))
            board_copy.img.draw_rect(piece_x, piece_y, board_copy.cell_W_pix, 
                                   board_copy.cell_H_pix, (0, 255, 0, 255), thickness=5)

        board_copy.img.show(wait_ms=1)

    def _show(self) -> bool:
        """Show the current frame and handle window events."""
        return self.running

    # ─── win detection ───────────────────────────────────────────────────────
    def _is_win(self) -> bool:
        """Check if the game has ended."""
        white_pieces = [p for p in self.pieces.values() if getattr(p, 'owner', None) == 'W']
        black_pieces = [p for p in self.pieces.values() if getattr(p, 'owner', None) == 'B']
        
        return len(white_pieces) == 0 or len(black_pieces) == 0

    def _announce_win(self):
        """Announce the winner."""
        white_pieces = [p for p in self.pieces.values() if getattr(p, 'owner', None) == 'W']
        black_pieces = [p for p in self.pieces.values() if getattr(p, 'owner', None) == 'B']
        
        if len(white_pieces) == 0:
            print("השחורים ניצחו!")
        elif len(black_pieces) == 0:
            print("הלבנים ניצחו!")
        else:
            print("המשחק הסתיים!")