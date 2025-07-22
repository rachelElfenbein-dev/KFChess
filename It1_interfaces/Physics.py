from typing import Tuple, Optional
from It1_interfaces.Command import Command
from It1_interfaces.Board import Board
import math


class Physics:
    def __init__(self, start_cell: Tuple[int, int], board: Board, speed_m_s: float = 1.0):
        """Initialize physics with starting cell, board, and speed."""
        self.board = board
        self.speed_m_s = speed_m_s
        self.current_cell = start_cell
        self.current_pos_meters = self._cell_to_meters(start_cell)
        self.target_pos_meters = self.current_pos_meters
        self.is_moving = False
        self.start_time_ms = 0
        self.current_command = None
        
    def _cell_to_meters(self, cell: Tuple[int, int]) -> Tuple[float, float]:
        """Convert cell coordinates to meter coordinates."""
        # Assuming each cell is 1 meter x 1 meter
        return (float(cell[0]), float(cell[1]))
    
    def _meters_to_pixels(self, meters: Tuple[float, float]) -> Tuple[int, int]:
        """Convert meter coordinates to pixel coordinates."""
        # Assuming 64 pixels per meter (can be adjusted based on your game's scale)
        pixels_per_meter = 64
        return (int(meters[0] * pixels_per_meter), int(meters[1] * pixels_per_meter))

    # def reset(self, cmd: Command):
    #     """Reset physics state with a new command."""
    #     self.current_command = cmd
    #     if hasattr(cmd, 'target_cell') and cmd.target_cell is not None:
    #         try:
    #             # Validate that target_cell is a proper coordinate tuple
    #             target_cell = cmd.target_cell
    #             if isinstance(target_cell, (tuple, list)) and len(target_cell) == 2:
    #                 # Try to convert to ensure they're numeric
    #                 int(target_cell[0])
    #                 int(target_cell[1])
    #                 self.target_pos_meters = self._cell_to_meters(target_cell)
    #                 self.is_moving = True
    #                 self.start_time_ms = 0  # Will be set in first update call
    #             else:
    #                 self.is_moving = False
    #         except (TypeError, ValueError, IndexError):
    #             # Invalid target_cell format, don't move
    #             self.is_moving = False
    #     else:
    #         self.is_moving = False
    def reset(self, cmd: Command):
        """Reset physics state with a new command."""
        self.current_command = cmd
    # נסה להוציא יעד מהפקודה
        target_cell = getattr(cmd, 'target_cell', None)
        if target_cell is None and hasattr(cmd, 'params') and len(cmd.params) > 1:
        # params=[src, dst, ...]
            target_cell = cmd.params[1]
        if target_cell is not None:
            try:
                if isinstance(target_cell, (tuple, list)) and len(target_cell) == 2:
                    int(target_cell[0])
                    int(target_cell[1])
                    self.target_pos_meters = self._cell_to_meters(target_cell)
                    self.is_moving = True
                    self.start_time_ms = 0  # Will be set in first update call
                else:
                    self.is_moving = False
            except (TypeError, ValueError, IndexError):
                self.is_moving = False
        else:
            self.is_moving = False

    def update(self, now_ms: int) -> Optional[Command]:
        """Update physics state based on current time."""
        if not self.is_moving:
            return None
            
        if self.start_time_ms == 0:
            self.start_time_ms = now_ms
            
        elapsed_ms = now_ms - self.start_time_ms
        elapsed_s = elapsed_ms / 1000.0
        
        # Calculate distance to travel
        dx = self.target_pos_meters[0] - self.current_pos_meters[0]
        dy = self.target_pos_meters[1] - self.current_pos_meters[1]
        total_distance = math.sqrt(dx**2 + dy**2)
        
        if total_distance == 0:
            self.is_moving = False
            return None
            
        # Calculate how far we should have traveled by now
        distance_traveled = self.speed_m_s * elapsed_s
        
        if distance_traveled >= total_distance:
            # Movement completed
            self.current_pos_meters = self.target_pos_meters
            self.current_cell = (int(self.target_pos_meters[0]), int(self.target_pos_meters[1]))
            self.is_moving = False
            completed_command = self.current_command
            self.current_command = None
            return completed_command
        else:
            # Still moving - interpolate position
            progress = distance_traveled / total_distance
            self.current_pos_meters = (
                self.current_pos_meters[0] + dx * progress,
                self.current_pos_meters[1] + dy * progress
            )
            return None

    def can_be_captured(self) -> bool:
        """Check if this piece can be captured."""
        # Default implementation - can be captured when not moving
        return not self.is_moving

    def can_capture(self) -> bool:
        """Check if this piece can capture other pieces."""
        # Default implementation - can capture when not moving
        return not self.is_moving

    def get_pos(self) -> Tuple[int, int]:
        """
        Current pixel-space upper-left corner of the sprite in world coordinates (in pixels).
        """
        return self._meters_to_pixels(self.current_pos_meters)


class IdlePhysics(Physics):
    """Physics for pieces that don't move - always idle."""
    
    def __init__(self, start_cell: Tuple[int, int], board: Board, speed_m_s: float = 1.0):
        super().__init__(start_cell, board, speed_m_s)
        self.is_moving = False  # Never moves
    
    def reset(self, cmd: Command):
        """Idle physics ignores movement commands."""
        # Don't change state for idle physics
        pass
    
    def update(self, now_ms: int) -> Optional[Command]:
        """Idle physics never moves, so always returns None."""
        return None
    
    def can_be_captured(self) -> bool:
        """Idle pieces can typically be captured."""
        return True
    
    def can_capture(self) -> bool:
        """Idle pieces typically cannot capture."""
        return False


class MovePhysics(Physics):
    """Physics for pieces that can move with enhanced movement capabilities."""
    
    def __init__(self, start_cell: Tuple[int, int], board: Board, speed_m_s: float = 2.0):
        super().__init__(start_cell, board, speed_m_s)
        self.can_move_while_capturing = True
        self.capture_immunity_duration_ms = 500  # Half second immunity after capturing
        self.last_capture_time_ms = 0
    
    def reset(self, cmd: Command):
        """Enhanced reset with capture detection."""
        super().reset(cmd)
        if hasattr(cmd, 'is_capture') and cmd.is_capture:
            self.last_capture_time_ms = 0  # Will be set on next update
    
    def update(self, now_ms: int) -> Optional[Command]:
        """Enhanced update with capture timing."""
        if self.last_capture_time_ms == 0 and hasattr(self.current_command, 'is_capture'):
            if getattr(self.current_command, 'is_capture', False):
                self.last_capture_time_ms = now_ms
        
        return super().update(now_ms)
    
    def can_be_captured(self) -> bool:
        """Move physics pieces have capture immunity period."""
        if self.last_capture_time_ms > 0:
            # Check if still in immunity period
            # Note: This would need current time, so this is a simplified version
            return False  # Assume immunity for now
        return not self.is_moving
    
    def can_capture(self) -> bool:
        """Move physics pieces can capture even while moving if configured."""
        if self.can_move_while_capturing:
            return True
        return not self.is_moving
    
    def set_capture_ability(self, can_capture_while_moving: bool):
        """Configure whether this piece can capture while moving."""
        self.can_move_while_capturing = can_capture_while_moving
