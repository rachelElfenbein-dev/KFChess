import pathlib
from It1_interfaces.img import Img
from It1_interfaces.Board import Board
from It1_interfaces.PieceFactory import PieceFactory
from It1_interfaces.Game import Game


def main():
    """הפונקציה הראשית של המשחק"""
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
        img=board_img
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

    # יצירת כל הכלים
    pieces = []
    for piece_id, row, col in pieces_positions:
        piece = piece_factory.create_piece(piece_id, (row, col))
        pieces.append(piece)

    # יצירת והרצת המשחק
    game = Game(pieces=pieces, board=board)
    game.run()


if __name__ == "__main__":
    main()
