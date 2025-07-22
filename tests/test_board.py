import pytest
from It1_interfaces.Board import Board
from It1_interfaces.mock_img import MockImg

@pytest.fixture
def base_board():
    # יוצר מופע לוח בסיסי לבדיקה עם תמונת דמה
    img = MockImg()
    return Board(
        cell_H_pix=32,
        cell_W_pix=32,
        cell_H_m=1,
        cell_W_m=1,
        W_cells=10,
        H_cells=10,
        img=img
    )

def test_clone_returns_equal_values(base_board):
    """
    בודק שכל השדות (פיקסלים, מטרים, גובה ורוחב, תאים) מועתקים בצורה זהה בלוח החדש.
    """
    clone = base_board.clone()

    # בודק שכל השדות זהים
    assert clone.cell_H_pix == base_board.cell_H_pix
    assert clone.cell_W_pix == base_board.cell_W_pix
    assert clone.cell_H_m == base_board.cell_H_m
    assert clone.cell_W_m == base_board.cell_W_m
    assert clone.W_cells == base_board.W_cells
    assert clone.H_cells == base_board.H_cells

def test_clone_img_is_different_instance(base_board):
    """
    בודק שהשדה img שוכפל לאובייקט חדש – כלומר זה לא אותו מצביע בזיכרון.
    """
    clone = base_board.clone()

    # לוודא שזה לא אותו אובייקט בדיוק (כתובת בזיכרון שונה)
    assert clone.img is not base_board.img, "img צריך להיות מופע חדש ונפרד"

def test_clone_is_independent_from_original(base_board):
    """
    בודק שאם משנים את העותק, זה לא משפיע על הלוח המקורי.
    כולל גם img וגם פרמטר רגיל.
    """
    clone = base_board.clone()

    # משנים ערכים בעותק
    clone.cell_H_pix = 64
    clone.img.img = "CHANGED"

    # מוודאים שהמקור לא השתנה
    assert base_board.cell_H_pix == 32
    assert base_board.img.img != "CHANGED"

def test_clone_multiple_times(base_board):
    """
    בודק ששכפול מספר פעמים יוצר מופעים שונים (ולא החזרה של אותו אובייקט)
    כולל השוואה של שדות img.
    """
    clone1 = base_board.clone()
    clone2 = base_board.clone()

    # כל עותק צריך להיות שונה
    assert clone1 is not clone2
    assert clone1.img is not clone2.img
    assert clone1.img is not base_board.img

def test_clone_with_modified_img_object():
    """
    בודק מקרה גבול שבו ל־img יש תוכן פנימי משתנה.
    משנה את התוכן בעותק ומוודא שהמקור לא משתנה.
    """
    img1 = MockImg()
    img1.img = "PIXELS-ORIGINAL"

    # בונה לוח עם תמונה מותאמת
    board = Board(
        cell_H_pix=10,
        cell_W_pix=10,
        cell_H_m=1,
        cell_W_m=1,
        W_cells=5,
        H_cells=5,
        img=img1
    )

    # משכפל
    clone = board.clone()

    # משנה את התמונה בעותק
    clone.img.img = "PIXELS-CLONE"

    # מוודא שהמקור נשאר כמו שהיה
    assert board.img.img == "PIXELS-ORIGINAL"
    assert clone.img.img == "PIXELS-CLONE"
