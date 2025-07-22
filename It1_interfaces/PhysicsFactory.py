from It1_interfaces. Board import Board
from It1_interfaces. Physics import Physics, IdlePhysics, MovePhysics


class PhysicsFactory:
    def __init__(self, board: Board):
        
        self.board = board

    def create(self, start_cell, cfg) -> Physics:
       
        physics_type = cfg.get("type", "base").lower()
        
        if physics_type == "move":
            speed = cfg.get("speed_m_s", 1.0)
            return MovePhysics(start_cell, self.board, speed_m_s=speed)
        
        elif physics_type == "idle":
            return IdlePhysics(start_cell, self.board)
        
        else:
            # ברירת מחדל: מחלקת Physics בסיסית
            speed = cfg.get("speed_m_s", 1.0)
            return Physics(start_cell, self.board, speed_m_s=speed)
