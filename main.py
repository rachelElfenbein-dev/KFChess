# import pathlib
# import time
# import keyboard  # pip install keyboard
# from It1_interfaces.img import Img
# from It1_interfaces.Board import Board
# from It1_interfaces.PieceFactory import PieceFactory
# from It1_interfaces.Player import Player
# from It1_interfaces.Command import Command
# import cv2

# def execute_command(cmd, board_size):
#     if cmd.type == "Move":
#         cmd.player.move(cmd.direction, board_size)

# def main():
#     base_dir = pathlib.Path(__file__).parent

#     # טען את תמונת הלוח
#     board_img = Img().read(str(base_dir / "board.png"))

#     # צור את הלוח
#     board = Board(
#         cell_H_pix=103,
#         cell_W_pix=102,
#         cell_H_m=1,
#         cell_W_m=1,
#         W_cells=8,
#         H_cells=8,
#         img=board_img
#     )

#     # הגדרת הנתיב לתמונות הכלים
#     pieces_root = base_dir / "pieces"

#     piece_factory = PieceFactory(board=board, pieces_root=pieces_root)




#    # קריאת הקובץ עם מיקום הכלים
#     positions_file = base_dir / "board.txt"
#     pieces_positions = []
#     with open(positions_file, "r", encoding="utf-8") as f:
#         for line in f:
#             line = line.strip()
#             if not line or line.startswith("#"):
#                 continue
#             parts = line.split()
#             if len(parts) == 3:
#                 piece_id, row_str, col_str = parts
#                 row, col = int(row_str), int(col_str)
#                 pieces_positions.append((piece_id, row, col))

#     # יצירת כל הכלים בלוח והדפסת ציור
#     for piece_id, row, col in pieces_positions:
#         piece = piece_factory.create_piece(piece_id, (row, col))
#         img_piece = piece._state._graphics.get_img()
#         x, y = board.get_pixel_position((row, col))
#         img_piece.draw_on(board.img, x, y)

#     # הצגת הלוח עם כל הכלים
#     # הגדרת שחקנים
#     player1 = {"id": "P1", "controls": {"up": "w", "down": "s", "left": "a", "right": "d", "select": "space"}, "pos": [0, 0], "color": (255, 0, 0, 255),}
#     player2 = {"id": "P2", "controls": {"up": "i", "down": "k", "left": "j", "right": "l", "select": "tab"}, "pos": [7, 7], "color": (0, 255, 0, 255)}
#     players = [player1, player2]

#     print("התחל לשחק! לחצו ESC כדי לצאת.")
#     cv2.namedWindow("Image", cv2.WINDOW_AUTOSIZE)
    
#     #base_img = Img().read(str(base_dir / "board.png"))

#     while True:
#         # רענון הלוח מהבסיס
#         board.img = board_img.copy()

#         # ציור מסגרות של שחקנים
#         for player in players:
#             row, col = player["pos"]
#             x, y = board.get_pixel_position((row, col))
#             board.img.draw_rect(x, y, board.cell_W_pix, board.cell_H_pix, player["color"], thickness=5)

#         board.img.show(wait_ms=1)

#         # קלט והפעלת פקודות
#         for player in players:
#             row, col = player["pos"]
#             controls = player["controls"]
#             if keyboard.is_pressed(controls["up"]) and row > 0:
#                 player["pos"][0] -= 1
#             if keyboard.is_pressed(controls["down"]) and row < board.H_cells - 1:
#                 player["pos"][0] += 1
#             if keyboard.is_pressed(controls["left"]) and col > 0:
#                 player["pos"][1] -= 1
#             if keyboard.is_pressed(controls["right"]) and col < board.W_cells - 1:
#                 player["pos"][1] += 1

#         # יציאה
#         if keyboard.is_pressed("esc"):
#             cv2.destroyAllWindows()
#             break

#         # שליטה על קצב הרענון (20 FPS)
#         cv2.waitKey(1)
    
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()





import pathlib
import time
import keyboard  # pip install keyboard
from It1_interfaces.img import Img
from It1_interfaces.Board import Board
from It1_interfaces.PieceFactory import PieceFactory
from It1_interfaces.Player import Player
from It1_interfaces.Command import Command
import cv2

def main():
    base_dir = pathlib.Path(__file__).parent

    # טען את תמונת הלוח
    board_img = Img().read(str(base_dir / "board.png"))

    # צור את הלוח
    board = Board(
        cell_H_pix=103,
        cell_W_pix=102,
        cell_H_m=1,
        cell_W_m=1,
        W_cells=8,
        H_cells=8,
        img=board_img.copy()
    )

    # הגדרת הנתיב לתמונות הכלים
    pieces_root = base_dir / "pieces"
    piece_factory = PieceFactory(board=board, pieces_root=pieces_root)

    # קריאת הקובץ עם מיקום הכלים
    positions_file = base_dir / "board.txt"
    pieces_positions = []
    with open(positions_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) == 3:
                piece_id, row_str, col_str = parts
                row, col = int(row_str), int(col_str)
                pieces_positions.append((piece_id, row, col))

    # יצירת כל הכלים בלוח
    pieces = []
    for piece_id, row, col in pieces_positions:
        piece = piece_factory.create_piece(piece_id, (row, col))
        pieces.append(piece)

    # הגדרת שחקנים
    player1 = {
        "id": "P1",
        "controls": {"up": "w", "down": "s", "left": "a", "right": "d", "select": "space"},
        "pos": [0, 0],
        "color": (255, 0, 0, 255),
        "selected_piece": None,
        "select_source": None
    }
    player2 = {
        "id": "P2",
        "controls": {"up": "i", "down": "k", "left": "j", "right": "l", "select": "tab"},
        "pos": [7, 7],
        "color": (0, 255, 0, 255),
        "selected_piece": None,
        "select_source": None
    }
    players = [player1, player2]

    print("התחל לשחק! לחצו ESC כדי לצאת.")
    cv2.namedWindow("Image", cv2.WINDOW_AUTOSIZE)

    while True:
        # רענון הלוח מהבסיס
        board.img = board_img.copy()

        # ציור הכלים
        for piece in pieces:
            img_piece = piece._state._graphics.get_img()
            row, col = piece._state._physics.current_cell
            x, y = board.get_pixel_position((row, col))
            img_piece.draw_on(board.img, x, y)

        # ציור מסגרות של שחקנים
        for player in players:
            row, col = player["pos"]
            x, y = board.get_pixel_position((row, col))
            board.img.draw_rect(x, y, board.cell_W_pix, board.cell_H_pix, player["color"], thickness=5)
            # אם יש כלי נבחר, צייר עיגול קטן בפינה
            if player["selected_piece"] is not None:
                board.img.put_text("✓", x + 10, y + 30, font_size=1.5, color=(0,0,255,255), thickness=2)

        board.img.show(wait_ms=1)

        # קלט והפעלת פקודות
        for player in players:
            row, col = player["pos"]
            controls = player["controls"]
            # תזוזה של הסמן
            if keyboard.is_pressed(controls["up"]) and row > 0:
                player["pos"][0] -= 1
                time.sleep(0.1)
            if keyboard.is_pressed(controls["down"]) and row < board.H_cells - 1:
                player["pos"][0] += 1
                time.sleep(0.1)
            if keyboard.is_pressed(controls["left"]) and col > 0:
                player["pos"][1] -= 1
                time.sleep(0.1)
            if keyboard.is_pressed(controls["right"]) and col < board.W_cells - 1:
                player["pos"][1] += 1
                time.sleep(0.1)
            # בחירה/הזזה
            if keyboard.is_pressed(controls["select"]):
                # לחיצה ראשונה: בחירת כלי
                if player["selected_piece"] is None:
                    for piece in pieces:
                        if hasattr(piece, "owner") and piece.owner == player["id"] and piece._state._physics.current_cell == tuple(player["pos"]):
                            player["selected_piece"] = piece
                            player["select_source"] = tuple(player["pos"])
                            break
                else:
                    src = player["select_source"]
                    dst = tuple(player["pos"])
                    move_type = "J" if abs(src[0] - dst[0]) > 1 or abs(src[1] - dst[1]) > 1 else "M"
                    piece_id = player["selected_piece"].piece_id
                    src_str = f"{chr(ord('a')+src[1])}{src[0]+1}"
                    dst_str = f"{chr(ord('a')+dst[1])}{dst[0]+1}"
                    cmd_str = f"{piece_id}{move_type}{src_str}{dst_str}"
                    cmd = Command(
                        timestamp=int(time.time()*1000),
                        piece_id=piece_id,
                        type="Move" if move_type == "M" else "Jump",
                        params=[src, dst, cmd_str]
                    )
                     # בדוק אם יש כלי ביעד – אכול אותו
                    target_piece = None
                    for other in pieces:
                        if other._state._physics.current_cell == dst and other != player["selected_piece"]:
                            target_piece = other
                            break
                    if target_piece and getattr(target_piece, "owner", None) != player["id"]:
                        pieces.remove(target_piece)
                    # הזז את הכלי דרך on_command
                    now_ms = int(time.time() * 1000)
                    player["selected_piece"].on_command(cmd, now_ms)
                    player["selected_piece"] = None
                    player["select_source"] = None
                    print(f"Command: {cmd_str}")
                    time.sleep(0.2)

        # יציאה
        if keyboard.is_pressed("esc"):
            cv2.destroyAllWindows()
            break

        cv2.waitKey(1)

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()