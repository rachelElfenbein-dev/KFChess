import pathlib
import copy
import os

from typing import List, Optional
from It1_interfaces.img import Img
from It1_interfaces.Command import Command
from It1_interfaces.Board import Board


class Graphics:
    def __init__(self,
                 sprites_folder: pathlib.Path,
                 board: Board,
                 loop: bool = True,
                 fps: float = 6.0):
        self.sprites_folder = sprites_folder
        self.board = board
        self.loop = loop
        self.fps = fps

        self.frames: List[Img] = []
        self.frame_paths: List[pathlib.Path] = []
        self.cur_frame_idx: int = 0
        self.last_update_ms: int = 0
        self.img: Optional[Img] = None
        self.current_cmd: Optional[Command] = None
        self.Img = Img  # ניתן להחלפה מבחוץ

        self._load_idle(sprites_folder)

    def _load_idle(self, subdir: str):
   
        path = self.sprites_folder
        if not path.exists():
            print(f"⚠️ תיקיית idle לא קיימת: {path}")
            return

        pngs = sorted(
            [p for p in path.iterdir()
            if p.suffix.lower() == ".png" and p.stem.isdigit()],
                key=lambda p: int(p.stem)
        )
        self.frame_paths = pngs

        for png_path in pngs:
            frame = self.Img()
            frame.read(str(png_path), size=(self.board.cell_W_pix, self.board.cell_H_pix))  # קריאה של התמונה לתוך אובייקט Img
            self.frames.append(frame)

        if self.frames:
            self.cur_frame_idx = 0
            self.img = self.frames[0]
        else:
            print("⚠️ לא נטענו פריימים ב־idle.")

    def reset(self, cmd: Command):
        self.current_cmd = cmd
        self.frames = []
        self.frame_paths = []
        self.cur_frame_idx = 0
        self.last_update_ms = 0
        self.img = None

        subdir = f"{cmd.piece}_{cmd.dir}"
        path = self.sprites_folder / subdir
        if not path.exists():
            print(f"⚠️ לא נמצאה תיקייה עבור: {subdir}")
            return

        pngs = sorted(
            [p for p in path.iterdir()
             if p.suffix.lower() == ".png" and p.stem.isdigit()],
            key=lambda p: int(p.stem)
        )
        self.frame_paths = pngs

        for _ in pngs:
            frame = self.Img()
            self.frames.append(frame)

        if self.frames:
            self.cur_frame_idx = 0
            self.img = self.frames[0]
            x, y = self.board.get_pixel_position(cmd.end_cell)
            self.img.reset((x, y))

    def update(self, now_ms: int):
        if not self.frames:
            return
        elapsed = now_ms - self.last_update_ms
        ms_per_frame = int(1000 / self.fps)
        if elapsed < ms_per_frame:
            return

        if self.cur_frame_idx < len(self.frames) - 1:
            self.cur_frame_idx += 1
            self.img = self.frames[self.cur_frame_idx]
            x, y = self.board.get_pixel_position(self.current_cmd.end_cell)
            self.img.reset((x, y))
        self.last_update_ms = now_ms

    def get_img(self) -> Optional[Img]:
        return self.img

    def copy(self):
        g = Graphics(self.sprites_folder, self.board, self.loop, self.fps)
        g.frames = self.frames
        g.frame_paths = self.frame_paths
        g.cur_frame_idx = self.cur_frame_idx
        g.last_update_ms = self.last_update_ms
        g.current_cmd = self.current_cmd
        g.img = copy.copy(self.img) if self.img is not None else None
        return g
