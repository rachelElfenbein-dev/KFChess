# import pathlib
# import json
# from It1_interfaces.img import Img
# from It1_interfaces.Board import Board
# from It1_interfaces.PhysicsFactory import PhysicsFactory
# from It1_interfaces.GraphicsFactory import GraphicsFactory
# from It1_interfaces.Piece import Piece
# from It1_interfaces.State import State  
# from It1_interfaces.Moves import Moves




# class PieceFactory:
#     def __init__(self, board: Board, pieces_root: pathlib.Path):
#         self.board = board
#         self.pieces_root = pieces_root
#         self.physics_factory = PhysicsFactory(board)
#         self.graphics_factory = GraphicsFactory(board)

#     def create_piece(self, piece_id: str,  cell: tuple[int, int]) -> Piece:
#         # נתיב לתיקיית מצב idle (כדוגמה)
#         idle_dir = self.pieces_root / piece_id / "states" / "idle"
#         config_path = idle_dir / "config.json"
#         sprites_dir = idle_dir / "sprites"

#         # קריאת הקובץ config.json
#         with open(config_path, "r") as f:
#             config = json.load(f)

#         # יצירת Physics באמצעות הפקטורי
#         physics_cfg = config.get("physics", {})
#         physics = self.physics_factory.create(cell, physics_cfg)

#         # יצירת Graphics באמצעות הפקטורי
#         graphics_cfg = config.get("graphics", {})
#         cell_size = (self.board.cell_W_pix, self.board.cell_H_pix)
#         graphics = self.graphics_factory.load(sprites_dir, graphics_cfg, cell_size)
#         moves_txt_path =  self.pieces_root / piece_id / "moves.txt"
#         moves = Moves(moves_txt_path, (self.board.H_cells, self.board.W_cells))

#         # צור state
#         state = State(physics=physics, graphics=graphics, moves=moves)

#         # יצירת Piece עם ה-state ההתחלתי
#         return Piece(piece_id=piece_id, init_state=state)
import pathlib
import json
from It1_interfaces.img import Img
from It1_interfaces.Board import Board
from It1_interfaces.PhysicsFactory import PhysicsFactory
from It1_interfaces.GraphicsFactory import GraphicsFactory
from It1_interfaces.Piece import Piece
from It1_interfaces.State import State  
from It1_interfaces.Moves import Moves


class PieceFactory:
    def __init__(self, board: Board, pieces_root: pathlib.Path):
        self.board = board
        self.pieces_root = pieces_root
        self.physics_factory = PhysicsFactory(board)
        self.graphics_factory = GraphicsFactory(board)

    def create_piece(self, piece_id: str, cell: tuple[int, int]) -> Piece:
        # נתיב לתיקיית מצב idle (כברירת מחדל)
        idle_dir = self.pieces_root / piece_id / "states" / "idle"
        config_path = idle_dir / "config.json"
        sprites_dir = idle_dir / "sprites"
        
        print("🔍 יצירת כלי:", piece_id, "במיקום:", cell)
        print("🔍 config_path:", config_path)
        print("🔍 sprites_dir:", sprites_dir)

      
        # קריאת קובץ config.json
        with open(config_path, "r") as f:
            config = json.load(f)

        # --- טיפול בברירות מחדל ל־physics ---
        physics_cfg = config.get("physics", {})
        physics_cfg.setdefault("type", "idle")  # ברירת מחדל אם חסר
        physics = self.physics_factory.create(cell, physics_cfg)

        # --- טיפול בברירות מחדל ל־graphics ---
        graphics_cfg = config.get("graphics", {})
        graphics_cfg.setdefault("dir", "idle")
        graphics_cfg["fps"] = graphics_cfg.get("frames_per_sec", graphics_cfg.get("fps", 6))

        cell_size = (self.board.cell_W_pix, self.board.cell_H_pix)
        graphics = self.graphics_factory.load(sprites_dir, graphics_cfg, cell_size)

        # --- טעינת מהלכים ---
        moves_txt_path = self.pieces_root / piece_id / "moves.txt"
        moves = Moves(moves_txt_path, (self.board.H_cells, self.board.W_cells))

        # יצירת מצב ראשוני
        state = State(physics=physics, graphics=graphics, moves=moves)
        print(f"🔍 sprites_dir: {sprites_dir}")
        # יצירת הכלי
        return Piece(piece_id=piece_id, init_state=state)
