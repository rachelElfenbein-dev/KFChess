

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
   # קריאת הקובץ עם מיקום הכלים והגדרת owner
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
                # קבע owner לפי סוג הכלי או השורה
                if piece_id.endswith("W") or row >= 6:
                    owner = "P1"
                elif piece_id.endswith("B") or row <= 1:
                    owner = "P2"
                else:
                    owner = None
                pieces_positions.append((piece_id, row, col, owner))
                

    # יצירת כל הכלים בלוח
    pieces = []
    for piece_id, row, col, owner in pieces_positions:
        piece = piece_factory.create_piece(piece_id, (row, col))
        piece.owner = owner  # הוסף את הבעלים לכל כלי
        pieces.append(piece)

    # הגדרת שחקנים
    player1 = Player(
        id="P1",
        controls={"up": "w", "down": "s", "left": "a", "right": "d",
                    "select_piece": "space",   # בחירת כלי
                     "move_piece": "enter"      # בחירת יעד/הזזה
        },
        pos=[6, 0],
        color=(255, 0, 0, 255),
        # selected_piece=None,
        # select_source=None
    )
    player2 = Player(
        id= "P2",
        controls= {"up": "i", "down": "k", "left": "j", "right": "l",
                    "select_piece": "tab",   # בחירת כלי
                     "move_piece": "p"      # בחירת יעד/הזזה
        },
        pos= [1,0],
        color= (0, 255, 0, 255),
        # selected_piece= None,
        # select_source= None
    )
    players = [player1, player2]

    print("התחל לשחק! לחצו ESC כדי לצאת.")
    cv2.namedWindow("Image", cv2.WINDOW_AUTOSIZE)

    key_states = {}
    for player in players:
        for action in ["select_piece", "move_piece"]:
            key = player.controls[action]
            key_states[key] = False

    while True:
        # רענון הלוח מהבסיס
        board.img = board_img.copy()
        now_ms = int(time.time() * 1000)
        for piece in pieces:
            piece.update(now_ms)
        # ציור הכלים
        for piece in pieces:
            img_piece = piece.state_machine.current._graphics.get_img()
            print(f"[DEBUG] {piece.piece_id} get_img() -> {img_piece}")
            print(f"img_piece.img: {getattr(img_piece, 'img', None)}")
            print(f"board.img: {board.img}, board.img.img: {getattr(board.img, 'img', None)}")
            row, col = piece.state_machine.current._physics.current_cell
            x, y = board.get_pixel_position((row, col))
            if img_piece is not None:
                img_piece.draw_on(board.img, x, y)
            else:
                print(f"[ERROR] לא נטענה תמונה עבור {piece.piece_id} (state={type(piece.state_machine.current).__name__})")

        # ציור מסגרות של שחקנים
        for player in players:
            row, col = player.pos
            x, y = board.get_pixel_position((row, col))
            board.img.draw_rect(x, y, board.cell_W_pix, board.cell_H_pix, player.color, thickness=5)
            # אם יש כלי נבחר, צייר עיגול טן בפינה
            if player.selected_piece is not None:
                board.img.put_text("✓", x + 10, y + 30, font_size=1.5, color=(0,0,255,255), thickness=2)

        board.img.show(wait_ms=1)

        
        
        #קלט והפעלת פקודות
        for player in players:
            row, col = player.pos
            controls = player.controls
            # תזוזה של הסמן
            if keyboard.is_pressed(controls["up"]) and row > 0:
                player.pos[0] -= 1
                time.sleep(0.1)
            if keyboard.is_pressed(controls["down"]) and row < board.H_cells - 1:
                player.pos[0] += 1
                time.sleep(0.1)
            if keyboard.is_pressed(controls["left"]) and col > 0:
                player.pos[1] -= 1
                time.sleep(0.1)
            if keyboard.is_pressed(controls["right"]) and col < board.W_cells - 1:
                player.pos[1] += 1
                time.sleep(0.1)
    
      
    
        # בחירת כלי (מקש ייעודי, רק בלחיצה טרייה)
            select_key = controls["select_piece"]
            if keyboard.is_pressed(select_key) and not key_states[select_key] and player.selected_piece is None:
                print(f"נלחץ: {select_key}")
                for piece in pieces:
                    print("בודק כלי:", piece.piece_id)
                    print("owner:", getattr(piece, "owner", None), "player.id:", player.id)
                    print("מיקום הכלי:", piece.state_machine.current._physics.current_cell, "מיקום הסמן:", tuple(player.pos))
                    if hasattr(piece, "owner") and piece.owner == player.id and piece.state_machine.current._physics.current_cell == tuple(player.pos):
                        player.selected_piece = piece
                        player.select_source = tuple(player.pos)
                        print(f"נבחר כלי: {piece.piece_id}")
                        break
     
            move_key = controls["move_piece"]
            if keyboard.is_pressed(move_key) and not key_states[move_key] and player.selected_piece is not None:
                print(f"נלחץ: {move_key}")
                src = player.select_source
                dst = tuple(player.pos)
                piece = player.selected_piece
                legal_moves = piece.state_machine.current._moves.get_moves(*src)
                if dst not in legal_moves:
                    print("תנועה לא חוקית!")
                else:
                    move_type = "J" if abs(src[0] - dst[0]) > 1 or abs(src[1] - dst[1]) > 1 else "M"
                    piece_id = piece.piece_id
                    src_str = f"{chr(ord('a')+src[1])}{src[0]+1}"
                    dst_str = f"{chr(ord('a')+dst[1])}{dst[0]+1}"
                    cmd_str = f"{piece_id}{move_type}{src_str}{dst_str}"
                    print("commmmmd_str:", cmd_str)
                    cmd = Command(
                        timestamp=int(time.time()*1000),
                        piece_id=piece_id,
                        type="Move" if move_type == "M" else "Jump",
                        params=[src, dst, cmd_str],
                        target_cell=dst
                    )
                    target_piece = None
                    for other in pieces:
                        if other.state_machine.current._physics.current_cell == dst and other != piece:
                            target_piece = other
                            break
                    if target_piece and getattr(target_piece, "owner", None) != player.id:
                        pieces.remove(target_piece)
                    now_ms = int(time.time() * 1000)
                    piece.on_command(cmd, now_ms)
                    player.selected_piece = None
                    player.select_source = None
                    print(f"Command: {cmd_str}")
                key_states[move_key] = True
            elif not keyboard.is_pressed(move_key):
                key_states[move_key] = False




       
      

        cv2.waitKey(1)

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()