import pytest
from unittest.mock import MagicMock
from It1_interfaces.Piece import Piece
from It1_interfaces.Command import Command
from It1_interfaces.State import State
from It1_interfaces.Board import Board


@pytest.fixture
def dummy_state():
    state = MagicMock(spec=State)
    return state

@pytest.fixture
def piece(dummy_state):
    return Piece(piece_id="P1", init_state=dummy_state)

def make_cmd(piece_id="P1"):
    cmd = MagicMock(spec=Command)
    cmd.piece_id = piece_id
    return cmd

def test_is_command_possible_true(piece):
    cmd = make_cmd("P1")
    assert piece.is_command_possible(cmd) is True

def test_is_command_possible_false(piece):
    cmd = make_cmd("P2")  # מזהה שונה
    assert piece.is_command_possible(cmd) is False

def test_on_command_runs_process_and_update(piece, dummy_state):
    cmd = make_cmd("P1")
    new_state = MagicMock(spec=State)
    dummy_state.process_command.return_value = new_state

    piece.on_command(cmd, now_ms=123)

    dummy_state.process_command.assert_called_once_with(cmd, 123)
    new_state.update.assert_called_once_with(123)
    # עדכן את ה־state
    assert piece._state == new_state

def test_on_command_invalid_command_does_nothing(piece, dummy_state):
    cmd = make_cmd("P2")  # לא תואם לכלי
    piece.on_command(cmd, now_ms=456)

    dummy_state.process_command.assert_not_called()
    dummy_state.update.assert_not_called()
    assert piece._state == dummy_state

def test_on_command_process_returns_none_keeps_state(piece, dummy_state):
    cmd = make_cmd("P1")
    dummy_state.process_command.return_value = None

    piece.on_command(cmd, now_ms=789)

    dummy_state.process_command.assert_called_once_with(cmd, 789)
    dummy_state.update.assert_called_once_with(789)
    assert piece._state == dummy_state  # לא השתנה

def test_reset_calls_reset_and_update(piece, dummy_state):
    piece.reset(start_ms=1000)

    dummy_state.reset.assert_called_once_with(None)
    dummy_state.update.assert_called_once_with(1000)

def test_update_calls_state_update(piece, dummy_state):
    piece.update(now_ms=1500)
    dummy_state.update.assert_called_once_with(1500)

def test_draw_on_board_calls_graphics_draw(piece, dummy_state):
    dummy_graphics = MagicMock()
    dummy_state._graphics = dummy_graphics
    board = MagicMock(spec=Board)

    piece.draw_on_board(board, now_ms=2000)
    dummy_graphics.draw.assert_called_once_with(board, 2000)
