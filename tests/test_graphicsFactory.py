import unittest
import pathlib
from unittest.mock import MagicMock
from It1_interfaces.GraphicsFactory import GraphicsFactory
from It1_interfaces. Graphics import Graphics
from It1_interfaces.mock_img import MockImg
from It1_interfaces.Board import Board

class DummyBoard(Board):
    """
    מחלקת לוח דמה לפישוט הטסטים,
    מחזיקה מימדים קבועים ומממשת מתודת מיקום פיקסלים פשוטה.
    """
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
        # מחשב מיקום פיקסלים פשוט לפי תא בלוח
        return (cell[0] * self.cell_W_pix, cell[1] * self.cell_H_pix)

class TestGraphicsFactoryAndGraphics(unittest.TestCase):
    """
    סדרת טסטים מקיפה למחלקות GraphicsFactory ו-Graphics,
    כולל בדיקות טעינת גרפיקה, אתחול אנימציות, עדכון פריימים ויצירת עותקים.
    """

    def setUp(self):
        """
        מתבצע לפני כל טסט - אתחול נתוני בסיס משותפים:
        תיקיית sprites דמה, לוח דמה, ואובייקט Factory.
        """
        self.sprites_dir = pathlib.Path("tests/sprites")
        self.board = DummyBoard()
        self.factory = GraphicsFactory()

    def test_load_returns_graphics_instance_with_defaults(self):
        """
        בדיקה שהפונקציה load מחזירה אובייקט Graphics עם פרמטרים ברירת מחדל,
        כאשר cfg ריק.
        """
        gfx = self.factory.load(
            sprites_dir=self.sprites_dir,
            cfg={},
            cell_size=(32, 32)
        )
        self.assertIsInstance(gfx, Graphics)
        self.assertEqual(gfx.sprites_folder, self.sprites_dir)
        self.assertEqual(gfx.loop, True)   # ברירת מחדל ל־loop
        self.assertEqual(gfx.fps, 6.0)    # ברירת מחדל ל־fps

    def test_load_with_custom_cfg_parameters(self):
        """
        בדיקה שהפרמטרים המותאמים ב-cfg מועברים כראוי לאובייקט Graphics.
        """
        cfg = {
            "loop": False,
            "fps": 12.5,
            "ImgClass": MockImg
        }
        gfx = self.factory.load(
            sprites_dir=self.sprites_dir,
            cfg=cfg,
            cell_size=(64, 64)
        )
        self.assertFalse(gfx.loop)
        self.assertEqual(gfx.fps, 12.5)
        self.assertEqual(gfx.ImgClass, MockImg)

    def test_graphics_reset_loads_frames_correctly(self):
        """
        בדיקה ש־reset טוען את הפריימים כראוי מהתיקייה,
        מאתחל את הפריים הנוכחי, מצייר במיקום הנכון,
        וממלא את frames ברשימה.
        """
        gfx = Graphics(
            sprites_folder=self.sprites_dir,
            board=self.board,
            loop=True,
            fps=10,
            ImgClass=MockImg
        )
        # מוקאינג ל־pathlib לקריאות תיקייה וקבצים
        with unittest.mock.patch("pathlib.Path.exists", return_value=True), \
             unittest.mock.patch("pathlib.Path.is_dir", return_value=True), \
             unittest.mock.patch("pathlib.Path.iterdir", return_value=[
                 pathlib.Path("frame1.png"),
                 pathlib.Path("frame2.png")
             ]):
            
            cmd = MagicMock()
            cmd.piece = "knight"
            cmd.dir = "up"
            cmd.end_cell = (2, 3)
            self.board.last_dest = cmd.end_cell

            gfx.reset(cmd)

            self.assertEqual(len(gfx.frames), 2)            # טוען 2 פריימים
            self.assertIsNotNone(gfx.img)                    # התמונה הנוכחית מוגדרת
            self.assertEqual(gfx.current_frame_index, 0)    # מתחיל בפריים ראשון
            
            # מיקום הציור צריך להופיע ב-MockImg.traj (עקבות הציור)
            expected_pos = self.board.get_pixel_position(cmd.end_cell)
            self.assertIn(expected_pos, MockImg.traj)

    def test_reset_raises_value_error_if_no_frames(self):
        """
        בדיקה ש־reset זורק שגיאה במקרה שאין פריימים בתיקיית הגרפיקה.
        """
        gfx = Graphics(
            sprites_folder=self.sprites_dir,
            board=self.board,
            loop=True,
            fps=10,
            ImgClass=MockImg
        )
        with unittest.mock.patch("pathlib.Path.exists", return_value=True), \
             unittest.mock.patch("pathlib.Path.is_dir", return_value=True), \
             unittest.mock.patch("pathlib.Path.iterdir", return_value=[]):  # תיקיה ריקה

            cmd = MagicMock()
            cmd.piece = "knight"
            cmd.dir = "up"
            cmd.end_cell = (0, 0)
            self.board.last_dest = cmd.end_cell

            with self.assertRaises(ValueError):
                gfx.reset(cmd)

    def test_update_advances_frames_and_loops_correctly(self):
        """
        בדיקה שהפונקציה update מתקדמת לפריים הבא אחרי הזמן המתאים,
        ושמתרחשת לולאה חזרה לפריים ראשון כאשר loop=True.
        """
        gfx = Graphics(
            sprites_folder=self.sprites_dir,
            board=self.board,
            loop=True,
            fps=10,
            ImgClass=MockImg
        )
        frame1 = MockImg()
        frame2 = MockImg()
        gfx.frames = [frame1, frame2]
        gfx.img = frame1
        gfx.current_frame_index = 0
        gfx.last_frame_time = 0

        gfx.update(50)  # פחות מ־100ms, לא מתקדם
        self.assertEqual(gfx.current_frame_index, 0)

        gfx.update(110)  # עבר 110ms, מתקדם לפריים 1
        self.assertEqual(gfx.current_frame_index, 1)

        gfx.update(210)  # עבר שוב 100ms, מתחדש ללולאה לפריים 0
        self.assertEqual(gfx.current_frame_index, 0)

    def test_update_stops_at_last_frame_if_loop_false(self):
        """
        בדיקה ש־update לא ממשיך מעבר לפריים האחרון אם loop=False.
        """
        gfx = Graphics(
            sprites_folder=self.sprites_dir,
            board=self.board,
            loop=False,
            fps=10,
            ImgClass=MockImg
        )
        frame1 = MockImg()
        frame2 = MockImg()
        gfx.frames = [frame1, frame2]
        gfx.img = frame1
        gfx.current_frame_index = 0
        gfx.last_frame_time = 0

        gfx.update(110)  # מתקדם לפריים 1
        self.assertEqual(gfx.current_frame_index, 1)

        gfx.update(220)  # מנסה להתקדם מעבר לפריים האחרון, נשאר בפריים 1
        self.assertEqual(gfx.current_frame_index, 1)

    def test_copy_creates_independent_graphics(self):
        """
        בדיקה שהפונקציה copy מחזירה אובייקט Graphics חדש,
        עם אותו מצב (פריימים, פריים נוכחי וזמן אחרון) אך אובייקט נפרד.
        """
        gfx = Graphics(
            sprites_folder=self.sprites_dir,
            board=self.board,
            loop=True,
            fps=10,
            ImgClass=MockImg
        )
        frame = MockImg()
        gfx.frames = [frame]
        gfx.img = frame
        gfx.current_frame_index = 5
        gfx.last_frame_time = 123

        copy_gfx = gfx.copy()
        self.assertIsNot(copy_gfx, gfx)                    # לא אותו אובייקט
        self.assertEqual(copy_gfx.current_frame_index, 5) # מצב זהה
        self.assertEqual(copy_gfx.last_frame_time, 123)
        self.assertEqual(copy_gfx.frames, gfx.frames)     # מצביעים לאותו רשימת פריימים (לפי מימוש)
        self.assertEqual(copy_gfx.img, gfx.img)           # אותו פריים נוכחי

if __name__ == "__main__":
    unittest.main()
