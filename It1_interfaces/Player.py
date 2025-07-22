# # ...existing Player class...
# class Player:
#     def __init__(self, player_id, controls, start_pos, color):
#         self.player_id = player_id
#         self.controls = controls
#         self.position = start_pos
#         self.color = color
#         self.selected_piece = None  # הכלי שנבחר

#     def select_or_move(self, board, pieces):
#         row, col = self.position
#         if self.selected_piece is None:
#             # בחירה: בדוק אם יש כלי שלי במיקום
#             for piece in pieces:
#                 if piece.position == (row, col) and piece.owner == self.player_id:
#                     self.selected_piece = piece
#                     break
#         else:
#             # ניסיון להזיז: בדוק אם מותר, ואם יש כלי ביעד – אכול אותו
#             target_piece = next((p for p in pieces if p.position == (row, col)), None)
#             if target_piece and target_piece.owner != self.player_id:
#                 pieces.remove(target_piece)  # אכילה
#             self.selected_piece.position = (row, col)
#             self.selected_piece = None

#     def move(self, direction, board_size):
#         row, col = self.position
#         if direction == "up" and row > 0:
#             self.position = (row - 1, col)
#         elif direction == "down" and row < board_size[0] - 1:
#             self.position = (row + 1, col)
#         elif direction == "left" and col > 0:
#             self.position = (row, col - 1)
#         elif direction == "right" and col < board_size[1] - 1:
#             self.position = (row, col + 1)
import time

class Player:
    def __init__(self, player_id, controls, start_pos, color):
        self.player_id = player_id
        self.controls = controls
        self.position = start_pos
        self.color = color
        self.selected_piece = None
        self.select_source = None  # מיקום המקור שנבחר

    def move_cursor(self, direction, board_size):
        row, col = self.position
        if direction == "up" and row > 0:
            self.position = (row - 1, col)
        elif direction == "down" and row < board_size[0] - 1:
            self.position = (row + 1, col)
        elif direction == "left" and col > 0:
            self.position = (row, col - 1)
        elif direction == "right" and col < board_size[1] - 1:
            self.position = (row, col + 1)

    def try_select_or_command(self, pieces, commands_queue):
        row, col = self.position
        if self.selected_piece is None:
            # בחירה ראשונה: בחר כלי שלך
            for piece in pieces:
                if hasattr(piece, "owner") and piece.owner == self.player_id and piece._state._physics.current_cell == (row, col):
                    self.selected_piece = piece
                    self.select_source = (row, col)
                    break
        else:
            # בחירה שנייה: יעד – צור Command ושלח
            src = self.select_source
            dst = (row, col)
            move_type = "J" if abs(src[0] - dst[0]) > 1 or abs(src[1] - dst[1]) > 1 else "M"
            # פורמט: QBMe5e8 (דוגמה)
            piece_id = self.selected_piece.piece_id
            src_str = f"{chr(ord('a')+src[1])}{src[0]+1}"
            dst_str = f"{chr(ord('a')+dst[1])}{dst[0]+1}"
            cmd_str = f"{piece_id}{move_type}{src_str}{dst_str}"
            # צור Command אמיתי
            from It1_interfaces.Command import Command
            cmd = Command(
                timestamp=int(time.time()*1000),
                piece_id=piece_id,
                type="Move" if move_type == "M" else "Jump",
                params=[src, dst, cmd_str]
            )
            commands_queue.append(cmd)
            self.selected_piece = None
            self.select_source = None