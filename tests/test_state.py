import unittest
from unittest.mock import MagicMock
from It1_interfaces.Command import Command
from It1_interfaces.State import State


class DummyState(State):
    """
    מחלקת דמה שמרחיבה State,
    משמשת לבדיקת מעבר בין מצבים (טרנזישנים)
    ומאפשרת לבדוק אם פונקציית reset נקראה עם הפקודה הנכונה.
    """
    def __init__(self):
        super().__init__(None, None, None)
        self.reset_called = False
        self.received_cmd = None

    def reset(self, cmd):
        """
        מאפס את המצב ומסמן שהפונקציה נקראה,
        שומר את הפקודה שהתקבלה לשם בדיקה בטסט.
        """
        self.reset_called = True
        self.received_cmd = cmd

    def update(self, now_ms: int):
        """
        מעדכן את המצב - כאן פשוט מחזיר את עצמו.
        """
        return self


class TestState(unittest.TestCase):
    def setUp(self):
        """
        יצירת אובייקטים דמה לרכיבים
        הגרפיקה, הפיזיקה, והמובס.
        """
        self.moves = MagicMock()
        self.graphics = MagicMock()
        self.physics = MagicMock()

        self.state = State(self.moves, self.graphics, self.physics)

    def test_set_and_get_transitions(self):
        """
        בודק שהטרנזישנים נשמרים נכון ומוחזרים,
        כאשר מגדירים מעבר על אירוע מסוים.
        """
        next_state = DummyState()
        self.state.set_transition("Move", next_state)
        self.assertIn("Move", self.state.transitions)
        self.assertIs(self.state.transitions["Move"], next_state)

    def test_reset_calls_graphics_and_physics_reset(self):
        """
        מאמת שהקריאה ל-reset ב-State מפעילה reset
        גם על רכיבי הגרפיקה וגם על הפיזיקה,
        ומעבירה את הפקודה הנכונה לפיזיקה.
        """
        cmd = MagicMock(spec=Command)
        self.state.reset(cmd)
        self.graphics.reset.assert_called_once()
        self.physics.reset.assert_called_once_with(cmd)

    def test_update_no_command_returns_self(self):
        """
        כאשר update בפיזיקה מחזיר None (אין פקודה חדשה),
        הפונקציה update ב-State מחזירה את המצב הנוכחי (self).
        בנוסף, וידוא שקריאות reset ו-update על הגרפיקה והפיזיקה בוצעו עם הפרמטרים הנכונים.
        """
        self.physics.update.return_value = None
        self.graphics.reset.return_value = None

        result = self.state.update(1000)
        self.assertIs(result, self.state)
        self.graphics.reset.assert_called_once_with(1000)
        self.physics.update.assert_called_once_with(1000)

    def test_update_with_command_transitions_to_next_state(self):
        """
        כאשר update בפיזיקה מחזיר פקודה (Command),
        יש מעבר למצב הבא המתאים לפי הטרנזישנים.
        ווידוא שהמצב הבא קיבל קריאה ל-reset עם הפקודה.
        """
        cmd = MagicMock(spec=Command)
        cmd.type = "Move"
        cmd.timestamp = 1234

        next_state = DummyState()
        self.state.set_transition("Move", next_state)

        self.physics.update.return_value = cmd
        self.graphics.reset.return_value = None

        result = self.state.update(1500)

        self.assertIs(result, next_state)
        self.assertTrue(next_state.reset_called)
        self.assertIs(next_state.received_cmd, cmd)

    def test_update_with_command_no_transition_returns_none(self):
        """
        במקרה שהפקודה שהתקבלה אינה נמצאת בטרנזישנים,
        update מחזיר None.
        """
        cmd = MagicMock(spec=Command)
        cmd.type = "NonExisting"
        self.physics.update.return_value = cmd
        self.graphics.reset.return_value = None

        result = self.state.update(1500)
        self.assertIsNone(result)

    def test_process_command_with_valid_transition(self):
        """
        בדיקה ישירה של process_command עם פקודה תקינה,
        מוודאת שהמעבר מתבצע למצב הנכון,
        שהפונקציה reset נקראה עם הפקודה.
        """
        cmd = MagicMock(spec=Command)
        cmd.type = "Jump"
        next_state = DummyState()
        self.state.set_transition("Jump", next_state)

        result = self.state.process_command(cmd, 0)
        self.assertIs(result, next_state)
        self.assertTrue(next_state.reset_called)
        self.assertIs(next_state.received_cmd, cmd)

    def test_process_command_with_invalid_transition_returns_none(self):
        """
        בדיקה של process_command עם פקודה שאין לה מצב יעד בטרנזישנים,
        מחזיר None.
        """
        cmd = MagicMock(spec=Command)
        cmd.type = "UnknownEvent"

        result = self.state.process_command(cmd, 0)
        self.assertIsNone(result)

    def test_can_transition_default_true(self):
        """
        בדיקת ברירת מחדל של can_transition - מחזיר True תמיד.
        """
        self.assertTrue(self.state.can_transition(0))

    def test_get_command_returns_current_command(self):
        """
        בדיקה ש-get_command מחזיר את הפקודה הנוכחית, אם קיימת.
        """
        cmd = MagicMock(spec=Command)
        self.state._current_command = cmd
        self.assertIs(self.state.get_command(), cmd)

    def test_get_command_when_none(self):
        """
        בדיקה ש-get_command מחזיר None אם אין פקודה נוכחית.
        """
        self.state._current_command = None
        self.assertIsNone(self.state.get_command())


if __name__ == "__main__":
    unittest.main()
