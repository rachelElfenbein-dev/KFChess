from pathlib import Path
from It1_interfaces.Graphics import Graphics
from It1_interfaces.Board import Board
from It1_interfaces.Command import Command

class GraphicsFactory:
    def __init__(self, board: Board):
        self.board = board

    def load(self,
         sprites_dir: Path,
         cfg: dict,
         cell_size: tuple[int, int]) -> Graphics:
        print(f"[DEBUG] Loading sprites from: {sprites_dir}")
        fps = cfg.get("frames_per_sec", 6.0)
        loop = cfg.get("is_loop", True)

        gfx = Graphics(sprites_folder=sprites_dir,
                   board=self.board,
                   loop=loop,
                   fps=fps)

        if "ImgClass" in cfg:
            gfx.Img = cfg["ImgClass"]

        return gfx
