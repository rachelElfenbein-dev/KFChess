import pytest
from pathlib import Path
from It1_interfaces.Moves import Moves

import tempfile

def write_temp_file(contents: str) -> Path:
    """עוזר לכתוב קובץ זמני עם תוכן."""
    tmp = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
    tmp.write(contents)
    tmp.flush()
    return Path(tmp.name)

def test_moves_loads_valid_file_and_filters_out_of_bounds():
    # חוקי תנועה פשוטים
    content = """
    1, 0
    0, 1
    -1, 0
    0, -1
    10, 0  # מעבר לגבולות הלוח
    """

    file_path = write_temp_file(content)
    dims = (5, 5)
    moves = Moves(file_path, dims)

    # מיקום מרכז הלוח
    r, c = 2, 2
    valid = moves.get_moves(r, c)

    # התנועה (10,0) היא מחוץ לגבולות, לא תיכלל
    expected = [(3, 2), (2, 3), (1, 2), (2, 1)]
    assert sorted(valid) == sorted(expected)

def test_moves_empty_file_results_in_no_moves():
    file_path = write_temp_file("")
    dims = (3, 3)
    moves = Moves(file_path, dims)

    assert moves.get_moves(1, 1) == []

def test_moves_file_with_comments_and_empty_lines():
    content = """
    # זהו קובץ חוקי עם הערות
    1, 1

    -1, -1
    """

    file_path = write_temp_file(content)
    dims = (4, 4)
    moves = Moves(file_path, dims)

    valid = moves.get_moves(1, 1)
    expected = [(2, 2), (0, 0)]
    assert sorted(valid) == sorted(expected)

def test_get_moves_no_valid_moves_when_out_of_bounds():
    content = """
    1, 0
    0, 1
    """

    file_path = write_temp_file(content)
    dims = (3, 3)
    moves = Moves(file_path, dims)

    # נקודה בפינה על הגבול
    r, c = 2, 2
    valid = moves.get_moves(r, c)
    # תנועות (3,2) ו(2,3) מחוץ ללוח -> לא יחזרו
    assert valid == []

def test_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        Moves(Path("non_existent_file.txt"), (5,5))

