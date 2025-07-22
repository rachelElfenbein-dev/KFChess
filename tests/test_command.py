import pytest
from It1_interfaces.Command import Command  # שנה בהתאם למיקום הקוד שלך

@pytest.mark.parametrize("timestamp,piece_id,cmd_type,params", [
    (0, "QB", "MOVE", ["e2", "e4"]),          # פקודת תזוזה תקינה בתחילת המשחק
    (1500, "KW", "JUMP", ["b1", "c3"]),       # קפיצה לאחר זמן
    (3000, "KB", "IDLE", []),                  # פקודת IDLE ללא פרמטרים
    (4500, "Qw", "LONG_REST", []),             # פקודת מנוחה ארוכה ללא פרמטרים
    (5000, "KB", "SHORT_REST", [])             # פקודת מנוחה קצרה ללא פרמטרים
])
def test_command_creation_valid(timestamp, piece_id, cmd_type, params):
    """
    בודק יצירת אובייקט Command עם ערכים תקינים מכל סוגי הפקודות.
    """
    cmd = Command(timestamp=timestamp, piece_id=piece_id, type=cmd_type, params=params)
    assert cmd.timestamp == timestamp
    assert cmd.piece_id == piece_id
    assert cmd.type == cmd_type
    assert cmd.params == params

def test_command_empty_piece_id():
    """
    בודק התנהגות כאשר piece_id הוא מחרוזת ריקה.
    """
    cmd = Command(timestamp=1000, piece_id="", type="MOVE", params=["a1", "a2"])
    assert cmd.piece_id == ""
    # בהתאם ללוגיקה אפשר להוסיף בדיקה אם מותר או לא

def test_command_invalid_type():
    """
    בודק יצירת פקודה עם סוג לא מוכר - אמור להתקבל (אין ולידציה במחלקה).
    אם תרצה אפשר להוסיף ולידציה בהמשך.
    """
    cmd = Command(timestamp=1000, piece_id="KB", type="FLY", params=["a1", "a3"])
    assert cmd.type == "FLY"

def test_command_params_variability():
    """
    בודק שקיימת גמישות בפרמטרים - רשימה ריקה, רשימה ארוכה, סוגים שונים.
    """
    # רשימת פרמטרים ריקה
    cmd1 = Command(timestamp=0, piece_id="Qw", type="IDLE", params=[])
    assert cmd1.params == []

    # רשימת פרמטרים ארוכה
    long_params = ["a1", "a2", "a3", "a4", "extra"]
    cmd2 = Command(timestamp=0, piece_id="KB", type="MOVE", params=long_params)
    assert cmd2.params == long_params

def test_command_timestamp_edge_cases():
    """
    בודק התנהגות עם ערכי timestamp קיצוניים.
    """
    # timestamp שלילי (למשל, שגיאה)
    cmd_neg = Command(timestamp=-10, piece_id="KB", type="MOVE", params=["a1", "a2"])
    assert cmd_neg.timestamp == -10

    # timestamp מאוד גדול (סביבות ה-INT_MAX)
    big_timestamp = 2**31 - 1
    cmd_big = Command(timestamp=big_timestamp, piece_id="Qw", type="JUMP", params=["b1", "c3"])
    assert cmd_big.timestamp == big_timestamp
