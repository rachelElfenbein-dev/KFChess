from dataclasses import dataclass
from It1_interfaces.img import Img
import copy  # לשכפול אובייקטים (אם צריך)

@dataclass
class Board:
    cell_H_pix: int  # גובה תא בפיקסלים
    cell_W_pix: int  # רוחב תא בפיקסלים
    cell_H_m: int    # גובה תא במטרים (או יחידה אחרת)
    cell_W_m: int    # רוחב תא במטרים (או יחידה אחרת)
    W_cells: int     # מספר התאים לרוחב בלוח
    H_cells: int     # מספר התאים לגובה בלוח
    img: Img         # האובייקט שמייצג את תמונת הלוח

    def clone(self) -> "Board":
      
        img_copy = self.img.clone()  
       
        return Board(
            cell_H_pix=self.cell_H_pix,
            cell_W_pix=self.cell_W_pix,
            cell_H_m=self.cell_H_m,
            cell_W_m=self.cell_W_m,
            W_cells=self.W_cells,
            H_cells=self.H_cells,
            img=img_copy
        )
    def get_pixel_position(self, cell: tuple[int, int]) -> tuple[int, int]:
        row, col = cell
        x = col * self.cell_W_pix
        y = row * self.cell_H_pix
        return (x, y)
