import pathlib
from typing import List, Tuple

class Moves:
    """
    מנהל חוקי תנועה לכלי במשחק.
    
    טוען תנועות מתוך קובץ טקסט ומסנן תנועות מחוץ לגבולות הלוח.

    כל שורה בקובץ צריכה להכיל שני מספרים שלמים מופרדים בפסיק,
    עם אפשרות להערות שמתחילות ב-#.

    דוגמה לשורה תקינה:
        1, 0
    """
    def __init__(self, txt_path: pathlib.Path, dims: Tuple[int, int]):
        """
        טוען חוקי תנועה מתוך קובץ טקסט לפי מימדי הלוח.

        פרמטרים:
        -----------
        txt_path : pathlib.Path
            נתיב לקובץ הטקסט עם חוקי התנועה.
        dims : Tuple[int, int]
            מימדי הלוח (שורות, עמודות).
        """
        self.dims = dims
        self.moves: List[Tuple[int, int]] = []

        with open(txt_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # הסרת הערות בתוך שורה
                if '#' in line:
                    line = line[:line.index('#')].strip()
                parts = line.split(',')
                if len(parts) < 2:
                    continue
                try:
                    dr = int(parts[0].strip())
                    # תמיכה בשורות כמו 1,0:non_capture
                    dc_part = parts[1].strip()
                    if ':' in dc_part:
                        dc_part = dc_part.split(':')[0]
                    dc = int(dc_part)
                except ValueError:
                    continue
                # מסננים תנועות שמוציאות את הכלי מחוץ ללוח
                if not self._is_in_bounds(dr, dc):
                    continue
                self.moves.append((dr, dc))

    def _is_in_bounds(self, dr: int, dc: int) -> bool:
        """
        בודק אם תנועה נתונה נמצאת בתחום הלוח.

        כאן אנו מניחים שהתנועה היא הזזה יחסית ולא מיקום מוחלט,
        לכן בדיקה פשוטה לפי מימדי הלוח.

        אם תרצה להרחיב, תוכל להוסיף מיקום התחלתי לבדיקה.

        מחזיר True אם התנועה אפשרית בתוך הגבולות.
        """
        rows, cols = self.dims
        # במקרה זה פשוט בודקים שהתזוזה לא גדולה מדי (למשל בתוך ±rows/cols)
        # ניתן להתאים את זה לפי הצורך המדויק במשחק שלך
        return -rows < dr < rows and -cols < dc < cols

    def get_moves(self, r: int, c: int) -> List[Tuple[int, int]]:
        """
        מחזיר את רשימת התנועות האפשריות מנקודה (r, c) על הלוח.

        כאן התנועות הן הזזות יחסיות, לכן מחזירים רק את תנועות ה- delta
        שנשמרו בקונסטרקטור, המסוננות לפי גבולות הלוח.

        ניתן להרחיב לפונקציה שמחזירה מיקומים מוחלטים אם תרצה.
        """
        valid_moves = []
        rows, cols = self.dims
        for dr, dc in self.moves:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                valid_moves.append((nr, nc))
        return valid_moves
