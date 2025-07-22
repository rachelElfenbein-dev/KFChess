import unittest
import pathlib
from unittest.mock import patch, MagicMock
from It1_interfaces.Graphics import Graphics
from It1_interfaces.Command import Command
from It1_interfaces.Board import Board
from It1_interfaces.mock_img import MockImg

class DummyBoard(Board):
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
        self.last_dest = (0, 0)

    def get_pixel_position(self, cell):
        return (cell[0] * self.cell_W_pix, cell[1] * self.cell_H_pix)

class TestGraphics(unittest.TestCase):

    def setUp(self):
        self.sprites_folder = pathlib.Path("tests/sprites")
        self.board = DummyBoard()
        self.graphics = Graphics(
            sprites_folder=self.sprites_folder,
            board=self.board,
            loop=True,
            fps=10,
            ImgClass=MockImg
        )
        MockImg.reset()

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.is_dir", return_value=True)
    @patch("pathlib.Path.iterdir")
    def test_reset_loads_frames_and_initializes_image(self, mock_iterdir, mock_is_dir, mock_exists):
        mock_iterdir.return_value = [
            pathlib.Path("frame1.png"),
            pathlib.Path("frame2.png"),
        ]
        cmd = Command(timestamp=0, piece_id="knight", type="Move", params=[])
        cmd.piece = "knight"
        cmd.dir = "up"
        cmd.end_cell = (1, 2)
        self.board.last_dest = cmd.end_cell

        self.graphics.reset(cmd)

        self.assertEqual(len(self.graphics.frames), 2)
        self.assertIsNotNone(self.graphics.img)
        self.assertEqual(self.graphics.current_frame_index, 0)
        expected_pos = self.board.get_pixel_position(cmd.end_cell)
        self.assertIn(expected_pos, MockImg.traj)

    @patch("pathlib.Path.exists", return_value=False)
    def test_reset_with_missing_directory_does_not_crash(self, mock_exists):
        cmd = Command(timestamp=0, piece_id="pawn", type="Move", params=[])
        cmd.piece = "pawn"
        cmd.dir = "down"
        cmd.end_cell = (0, 0)
        self.board.last_dest = cmd.end_cell

        self.graphics.reset(cmd)

        self.assertIsNone(self.graphics.img)
        self.assertEqual(self.graphics.frames, [])
        self.assertEqual(self.graphics.current_frame_index, 0)

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.is_dir", return_value=True)
    @patch("pathlib.Path.iterdir")
    def test_reset_with_no_png_files_raises(self, mock_iterdir, mock_is_dir, mock_exists):
        mock_iterdir.return_value = [
            pathlib.Path("frame1.txt"),
            pathlib.Path("frame2.doc"),
        ]
        cmd = Command(timestamp=0, piece_id="knight", type="Move", params=[])
        cmd.piece = "knight"
        cmd.dir = "up"
        cmd.end_cell = (1, 2)
        self.board.last_dest = cmd.end_cell

        with self.assertRaises(ValueError):
            self.graphics.reset(cmd)

    def test_update_without_frames_does_nothing(self):
        self.graphics.frames = []
        self.graphics.img = None
        self.graphics.last_frame_time = None
        self.graphics.current_frame_index = 0
        self.graphics.update(1000)
        self.assertIsNone(self.graphics.img)
        self.assertEqual(self.graphics.current_frame_index, 0)
        self.assertIsNone(self.graphics.last_frame_time)  # לא שינה כי אין frames

    def test_update_initializes_last_frame_time(self):
        self.graphics.frames = [MockImg()]
        self.graphics.last_frame_time = None
        self.graphics.update(1000)
        self.assertEqual(self.graphics.last_frame_time, 1000)
        self.assertEqual(self.graphics.current_frame_index, 0)  # לא התקדם

    def test_update_advances_frame_and_loops(self):
        img1 = MockImg()
        img2 = MockImg()
        self.graphics.frames = [img1, img2]
        self.graphics.img = img1
        self.graphics.current_frame_index = 0
        self.graphics.last_frame_time = 0
        self.board.last_dest = (1, 1)

        # פחות מ-frame_duration_ms - לא מתקדם
        self.graphics.update(50)
        self.assertEqual(self.graphics.current_frame_index, 0)

        # יותר מ-frame_duration_ms - מתקדם לפריים הבא
        self.graphics.update(110)
        self.assertEqual(self.graphics.current_frame_index, 1)

        # מתקדם לפריים הבא (הלולאה תחזור להתחלה)
        self.graphics.update(220)
        self.assertEqual(self.graphics.current_frame_index, 0)

    def test_update_advances_frame_without_looping(self):
        img1 = MockImg()
        img2 = MockImg()
        self.graphics.frames = [img1, img2]
        self.graphics.img = img1
        self.graphics.current_frame_index = 0
        self.graphics.last_frame_time = 0
        self.graphics.loop = False
        self.board.last_dest = (1, 1)

        self.graphics.update(110)
        self.assertEqual(self.graphics.current_frame_index, 1)

        self.graphics.update(220)
        self.assertEqual(self.graphics.current_frame_index, 1)  # לא חזר להתחלה

    def test_get_img_returns_current_img(self):
        img = MockImg()
        self.graphics.img = img
        self.assertIs(self.graphics.get_img(), img)

    def test_copy_creates_independent_copy(self):
        img = MockImg()
        self.graphics.frames = [img]
        self.graphics.img = img
        self.graphics.current_frame_index = 3
        self.graphics.last_frame_time = 123

        copy_gfx = self.graphics.copy()
        self.assertIsNot(copy_gfx, self.graphics)
        self.assertEqual(copy_gfx.current_frame_index, 3)
        self.assertEqual(copy_gfx.last_frame_time, 123)
        self.assertIs(copy_gfx.img, img)
        self.assertIs(copy_gfx.frames, self.graphics.frames)

if __name__ == "__main__":
    unittest.main()
