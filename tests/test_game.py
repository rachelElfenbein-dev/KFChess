import unittest
from unittest.mock import MagicMock, patch
from It1_interfaces.Game import Game
from It1_interfaces.Board import Board
from It1_interfaces.Piece import Piece
from It1_interfaces.Command import Command


class MockPiece(Piece):
    def __init__(self, piece_id, can_capture_flag=False, captured=False):
        self.piece_id = piece_id
        self.can_capture_flag = can_capture_flag
        self.captured = captured

    def reset(self, start_ms):
        self.reset_called = True

    def update(self, now):
        self.update_called = True

    def draw(self, board_img):
        self.draw_called = True

    def on_command(self, cmd):
        self.command_received = cmd

    def can_capture(self, other_piece):
        return self.can_capture_flag

    def can_be_captured(self):
        return not self.captured

    def capture(self):
        self.captured = True

    def is_captured(self):
        return self.captured


class MockBoard(Board):
    def __init__(self):
        super().__init__(
            cell_H_pix=32,
            cell_W_pix=32,
            cell_H_m=1.0,
            cell_W_m=1.0,
            W_cells=8,
            H_cells=8,
            img=None
        )

    def clone(self):
        return self

    def get_image(self):
        return "mock_image"


class TestGame(unittest.TestCase):
    def setUp(self):
        self.board = MockBoard()
        self.piece1 = MockPiece("piece1")
        self.piece2 = MockPiece("piece2", can_capture_flag=True)
        self.piece3 = MockPiece("piece3", captured=True)
        self.pieces = [self.piece1, self.piece2, self.piece3]
        self.game = Game(self.pieces, self.board)

    def test_game_initialization(self):
        self.assertEqual(len(self.game.pieces), 3)
        self.assertEqual(self.game.board, self.board)
        self.assertTrue(self.game.running)

    def test_game_time_ms(self):
        with patch("time.monotonic", return_value=123.456):
            self.assertEqual(self.game.game_time_ms(), 123456)

    def test_clone_board(self):
        cloned_board = self.game.clone_board()
        self.assertEqual(cloned_board, self.board)

    def test_start_user_input_thread(self):
        with patch("threading.Thread") as mock_thread:
            self.game.start_user_input_thread()
            mock_thread.assert_called_once()

    def test_run_updates_pieces(self):
        with patch.object(self.game, "_is_win", side_effect=[False, True]):
            with patch.object(self.game, "_draw"), patch.object(self.game, "_show", return_value=True):
                self.game.run()
                self.assertTrue(self.piece1.update_called)
                self.assertTrue(self.piece2.update_called)

    def test_process_input(self):
        cmd = Command(timestamp=0, piece_id="piece1", type="Move", params=[])
        self.game._process_input(cmd)
        self.assertEqual(self.piece1.command_received, cmd)

    def test_draw(self):
        with patch("cv2.imshow") as mock_imshow:
            self.game._draw()
            self.assertTrue(self.piece1.draw_called)
            self.assertTrue(self.piece2.draw_called)
            mock_imshow.assert_called_once_with("Game", "mock_image")

    def test_show_esc_key(self):
        with patch("cv2.waitKey", return_value=27):
            self.assertFalse(self.game._show())
            self.assertFalse(self.game.running)

    def test_resolve_collisions(self):
        self.game._resolve_collisions()
        self.assertTrue(self.piece3.captured)

    def test_is_win(self):
    # סימון כל הכלים מלבד אחד כ"נלכדים"
        self.piece1.captured = True
        self.piece2.captured = True
        self.piece3.captured = False  # רק piece3 נשאר במשחק
    # עכשיו _is_win אמורה להחזיר True
        self.assertTrue(self.game._is_win())

    def test_announce_win(self):
        with patch("builtins.print") as mock_print:
            self.game._announce_win()
            mock_print.assert_called_once_with("The winner is: piece1")


if __name__ == "__main__":
    unittest.main()