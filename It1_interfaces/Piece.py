from It1_interfaces.Board import Board
from It1_interfaces.Command import Command
from It1_interfaces.State import State
from typing import Optional


class Piece:
    def __init__(self, piece_id: str, init_state: State):
        """
        אתחול כלי במשחק עם מזהה ומצב התחלתי.

        :param piece_id: מזהה ייחודי לכלי (למשל "P1", "Knight3")
        :param init_state: אובייקט State שמייצג את המצב ההתחלתי של הכלי
        """
        self.piece_id = piece_id
        self._state = init_state

    def is_command_possible(self, cmd: Command) -> bool:
        """
        בדיקה האם הפקודה אפשרית עבור הכלי.
        לדוגמה, פקודות שמיועדות לכלי אחר לא יתקבלו.

        :param cmd: פקודה לבדיקה
        :return: True אם הפקודה תקפה עבור כלי זה, False אחרת
        """
        return cmd.piece_id == self.piece_id

    def on_command(self, cmd: Command, now_ms: int):
        """
        טיפול בפקודה שהגיעה לכלי.

        אם הפקודה תקפה, מעבירים אותה למצב הנוכחי של הכלי,
        ומעדכנים את המצב בזמן הנוכחי.

        :param cmd: פקודה לטיפול
        :param now_ms: זמן נוכחי במילישניות
        """
        if self.is_command_possible(cmd):
            next_state = self._state.process_command(cmd, now_ms)
            if next_state is not None:
                self._state = next_state
            self._state.update(now_ms)

    def reset(self, start_ms: int):
        """
        איפוס הכלי למצב ההתחלתי שלו.

        מאפס את המצב הנוכחי (State).

        :param start_ms: זמן התחלה במילישניות (יכול לשמש לאיפוס פנימי)
        """
        self._state.reset(None)  # אפס ללא פקודה ספציפית (אפשר להתאים אם רוצים)
        self._state.update(start_ms)

    # def update(self, now_ms: int):
    #     """
    #     עדכון מצב הכלי בזמן נתון.

    #     מעביר את הזמן למצב הנוכחי ומבצע עדכונים פנימיים.

    #     :param now_ms: זמן נוכחי במילישניות
    #     """
    #     self._state.update(now_ms)

    def update(self, now_ms: int):
        """
        עדכון מצב הכלי בזמן נתון.
        """
        new_state = self._state.update(now_ms)
        if new_state is not self._state:
            self._state = new_state

    def draw_on_board(self, board: Board, now_ms: int):
     
        # נניח שהרכיב גרפיקה יודע לצייר על הלוח
        self._state._graphics.get_img().draw_on(board, 4,7)
