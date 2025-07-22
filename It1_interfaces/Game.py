# import pathlib
# import time
# import keyboard
# import cv2
# from typing import List, Dict, Tuple
# from It1_interfaces.img import Img
# from It1_interfaces.Board import Board
# from It1_interfaces.PieceFactory import PieceFactory
# from It1_interfaces.Player import Player
# from It1_interfaces.Command import Command

# class Game:
#     def __init__(self, board: Board, pieces_root: pathlib.Path, positions_file: pathlib.Path, players: List[Player]):
#         self.board = board
#         self.pieces_root = pieces_root
#         self.positions_file = positions_file
#         self.players = players
#         self.pieces: List = []
#         self.key_states = {}
#         self._init_pieces()
#         self._init_key_states()

#     def _init_pieces(self):
#         piece_factory = PieceFactory(self.board, self.pieces_root)
#         pieces_positions = []
#         with open(self.positions_file, "r", encoding="utf-8") as f:
#             for line in f:
#                 line = line.strip()
#                 if not line or line.startswith("#"):
#                     continue
#                 parts = line.split()
#                 if len(parts) == 3:
#                     piece_id, row_str, col_str = parts
#                     row, col = int(row_str), int(col_str)
#                     pieces_positions.append((piece_id, row, col))
#         for piece_id, row, col in pieces_positions:
#             piece = piece_factory.create_piece(piece_id, (row, col))
#             self.pieces.append(piece)

#     def _init_key_states(self):
#         for player in self.players:
#             for action in ["select_piece", "move_piece"]:
#                 key = player.controls[action]
#                 self.key_states[key] = False

#     def run(self):
#         board_img = self.board.img.copy()
#         print("התחל לשחק! לחצו ESC כדי לצאת.")
#         cv2.namedWindow("Image", cv2.WINDOW_AUTOSIZE)

#         while True:
#             # רענון הלוח מהבסיס
#             self.board.img = board_img.copy()

#             # ציור הכלים
#             for piece in self.pieces:
#                 img_piece = piece._state._graphics.get_img()
#                 row, col = piece._state._physics.current_cell
#                 x, y = self.board.get_pixel_position((row, col))
#                 img_piece.draw_on(self.board.img, x, y)

#             # ציור מסגרות של שחקנים
#             for player in self.players:
#                 row, col = player.pos
#                 x, y = self.board.get_pixel_position((row, col))
#                 self.board.img.draw_rect(x, y, self.board.cell_W_pix, self.board.cell_H_pix, player.color, thickness=5)
#                 if player.selected_piece is not None:
#                     self.board.img.put_text("✓", x + 10, y + 30, font_size=1.5, color=(0,0,255,255), thickness=2)

#             self.board.img.show(wait_ms=1)

#             # קלט והפעלת פקודות
#             for player in self.players:
#                 row, col = player.pos
#                 controls = player.controls

#                 # תזוזה של הסמן
#                 if keyboard.is_pressed(controls["up"]) and row > 0:
#                     player.pos[0] -= 1
#                     time.sleep(0.1)
#                 if keyboard.is_pressed(controls["down"]) and row < self.board.H_cells - 1:
#                     player.pos[0] += 1
#                     time.sleep(0.1)
#                 if keyboard.is_pressed(controls["left"]) and col > 0:
#                     player.pos[1] -= 1
#                     time.sleep(0.1)
#                 if keyboard.is_pressed(controls["right"]) and col < self.board.W_cells - 1:
#                     player.pos[1] += 1
#                     time.sleep(0.1)

#                 # בחירת כלי (בלחיצה טרייה)
#                 select_key = controls["select_piece"]
#                 if keyboard.is_pressed(select_key) and not self.key_states[select_key] and player.selected_piece is None:
#                     for piece in self.pieces:
#                         if hasattr(piece, "owner") and piece.owner == player.id and piece._state._physics.current_cell == tuple(player.pos):
#                             player.selected_piece = piece
#                             player.select_source = tuple(player.pos)
#                             print(f"נבחר כלי: {piece.piece_id}")
#                             break
#                     self.key_states[select_key] = True
#                 elif not keyboard.is_pressed(select_key):
#                     self.key_states[select_key] = False

#                 # בחירת יעד/הזזה (בלחיצה טרייה)
#                 move_key = controls["move_piece"]
#                 if keyboard.is_pressed(move_key) and not self.key_states[move_key] and player.selected_piece is not None:
#                     src = player.select_source
#                     dst = tuple(player.pos)
#                     piece = player.selected_piece
#                     legal_moves = piece._state._moves.get_moves(*src)
#                     if dst not in legal_moves:
#                         print("תנועה לא חוקית!")
#                     else:
#                         move_type = "J" if abs(src[0] - dst[0]) > 1 or abs(src[1] - dst[1]) > 1 else "M"
#                         piece_id = piece.piece_id
#                         src_str = f"{chr(ord('a')+src[1])}{src[0]+1}"
#                         dst_str = f"{chr(ord('a')+dst[1])}{dst[0]+1}"
#                         cmd_str = f"{piece_id}{move_type}{src_str}{dst_str}"
#                         cmd = Command(
#                             timestamp=int(time.time()*1000),
#                             piece_id=piece_id,
#                             type="Move" if move_type == "M" else "Jump",
#                             params=[src, dst, cmd_str]
#                         )
#                         # בדוק אם יש כלי ביעד – אכול אותו
#                         target_piece = None
#                         for other in self.pieces:
#                             if other._state._physics.current_cell == dst and other != piece:
#                                 target_piece = other
#                                 break
#                         if target_piece and getattr(target_piece, "owner", None) != player.id:
#                             self.pieces.remove(target_piece)
#                         now_ms = int(time.time() * 1000)
#                         piece.on_command(cmd, now_ms)
#                         player.selected_piece = None
#                         player.select_source = None
#                         print(f"Command: {cmd_str}")
#                     self.key_states[move_key] = True
#                 elif not keyboard.is_pressed(move_key):
#                     self.key_states[move_key] = False

#             if keyboard.is_pressed("esc"):
#                 break

#             cv2.waitKey(1)

#         cv2.destroyAllWindows()