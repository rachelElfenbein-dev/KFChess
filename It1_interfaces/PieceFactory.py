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
from It1_interfaces.StateMachine import StateMachine
from It1_interfaces.Physics import IdlePhysics, MovePhysics


class PieceFactory:
    def __init__(self, board: Board, pieces_root: pathlib.Path):
        self.board = board
        self.pieces_root = pieces_root
        self.physics_factory = PhysicsFactory(board)
        self.graphics_factory = GraphicsFactory(board)

# ...existing code...

    def create_piece(self, piece_id: str, cell: tuple[int, int]) -> Piece:
        idle_dir = self.pieces_root / piece_id / "states" / "idle"
        config_path = idle_dir / "config.json"
        sprites_dir = self.pieces_root / piece_id  # במקום idle_dir / "sprites"

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        graphics_cfg = config.get("graphics", {})
        cell_size = (self.board.cell_W_pix, self.board.cell_H_pix)
        graphics = self.graphics_factory.load(sprites_dir, graphics_cfg, cell_size)
        moves_txt_path = self.pieces_root / piece_id / "moves.txt"
        moves = Moves(moves_txt_path, (self.board.H_cells, self.board.W_cells))

        # צור את כל המצבים
        idle_state = State(moves, graphics, IdlePhysics(cell, self.board))
        move_state = State(moves, graphics, MovePhysics(cell, self.board))
        longrest_state = State(moves, graphics, IdlePhysics(cell, self.board))
        jump_state = State(moves, graphics, MovePhysics(cell, self.board))
        shortrest_state = State(moves, graphics, IdlePhysics(cell, self.board))

        states = {
            "Idle": idle_state,
            "Move": move_state,
            "LongRest": longrest_state,
            "Jump": jump_state,
            "ShortRest": shortrest_state,
        }
        state_machine = StateMachine(states, initial="Idle")

        piece = Piece(piece_id=piece_id, state_machine=state_machine)
        print(f"🔍 Physics class for {piece_id} is {type(move_state._physics).__name__}")
        return piece
