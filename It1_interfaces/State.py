from It1_interfaces.Command import Command
from It1_interfaces.Moves import Moves
from It1_interfaces.Graphics import Graphics
from It1_interfaces.Physics import Physics
from typing import Dict, Optional
from typing import Tuple



class State:
    def __init__(self, moves: Moves, graphics: Graphics, physics: Physics):
        """
        אתחול מצב עם רכיבי תנועה, גרפיקה ופיזיקה.
        """
        self._moves = moves
        self._graphics = graphics
        self._physics = physics
        self.transitions: Dict[str, State] = {}  # מילון טרנזישנים: אירוע -> מצב יעד
        self._current_command: Optional[Command] = None

    def set_transition(self, event: str, target: 'State'):
        """
        הגדרת מעבר ממצב זה למצב יעד על אירוע מסוים.
        :param event: מחרוזת שמייצגת את סוג האירוע (לדוגמה "Move", "Jump" וכו')
        :param target: אובייקט State אליו עוברים
        """
        self.transitions[event] = target

    def reset(self, cmd: Command):
        """
        איפוס המצב עם פקודה חדשה.
        מאתחל את הגרפיקה, הפיזיקה ושומר את הפקודה הנוכחית.
        :param cmd: הפקודה שעל פיה מאתחלים
        """
        self._graphics.reset()
        self._physics.reset(cmd)
        self._current_command = cmd

    def update(self, now_ms: int) -> 'State':
        """
        עדכון המצב בזמן נתון.
        מפעיל עדכון גרפיקה ופיזיקה, ומעביר למצב הבא במידה ויש פקודה חדשה.
        :param now_ms: זמן נוכחי במילישניות
        :return: המצב החדש (יכול להיות אותו מצב אם לא מתבצע מעבר)
        """
        self._graphics.reset(now_ms)
        cmd = self._physics.update(now_ms)
        if cmd is not None:
            return self.process_command(cmd, now_ms)
        return self

    def process_command(self, cmd: Command, now_ms: int) -> Optional['State']:
        """
        טיפול בפקודה שמגיעה מהפיזיקה ומעבר למצב הבא לפי המפה.
        :param cmd: פקודה שהתקבלה
        :param now_ms: זמן נוכחי (יכול לשמש לאיפוס מצב הבא)
        :return: מצב הבא, או None אם לא ניתן לעבור
        """
        res = self.transitions.get(cmd.type)
        if res is None:
            return None

        res.reset(cmd)
        return res

    def can_transition(self, now_ms: int) -> bool:
        """
        בדיקה האם המצב יכול לעבור למצב הבא ברגע זה.
        אפשר לממש לוגיקה מותאמת לפי מצב ספציפי.
        כרגע מחזיר True כברירת מחדל.
        """
        return True

    def get_command(self) -> Optional[Command]:
        """
        מחזיר את הפקודה הנוכחית במצב.
        """
        return self._current_command

    def get_position_pixels(self) -> Tuple[int, int]:
        return self._physics.get_pos()

