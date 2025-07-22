from dataclasses import dataclass
from typing import List

@dataclass
class Command:
    """
    מייצגת פקודה בזמן המשחק – פעולה שמתבצעת ע״י שחקן או ע״י המערכת.

    Attributes:
    ----------
    timestamp : int
        הזמן במילישניות מאז תחילת המשחק.
        לדוגמה, 0 הוא הזמן בתחילת המשחק, 1500 הוא אחרי 1.5 שניות.

    piece_id : str
        מזהה הכלי שמבצע את הפקודה, למשל "P1" או "Knight3".

    type : str
        סוג הפקודה:
        - "Move": תזוזה רגילה
        - "Jump": ניתור מעל כלי אחר
        - "Attack": התקפה
        - "Die": השמדה של הכלי (הוצאה מהלוח)
        - ניתן להוסיף סוגים נוספים בהתאם למשחק

    params : List
        רשימת פרמטרים בהתאם לסוג הפקודה:
        - ל־"Move": ["e2", "e4"]
        - ל־"Jump": ["b1", "c3"]
        - ל־"Attack": ["d5"]
        - ל־"Die": ["f6"]
    """
    timestamp: int
    piece_id: str
    type: str
    params: List

class Command:
    def __init__(self, cmd_type, player, direction=None):
        self.type = cmd_type  # "Move"
        self.player = player
        self.direction = direction
