import unittest
from unittest.mock import MagicMock
from It1_interfaces.PhysicsFactory import PhysicsFactory
from It1_interfaces.Physics import IdlePhysics, MovePhysics
from It1_interfaces.Board import Board

class TestPhysicsFactory(unittest.TestCase):
    def setUp(self):
        self.board = MagicMock(spec=Board)
        self.factory = PhysicsFactory(self.board)

    def test_create_idle_physics(self):
        cfg = {'type': 'idle'}
        physics_obj = self.factory.create((1, 1), cfg)
        self.assertIsInstance(physics_obj, IdlePhysics)
        self.assertEqual(physics_obj.current_cell, (1, 1))

    def test_create_move_physics(self):
        cfg = {'type': 'move'}
        physics_obj = self.factory.create((2, 3), cfg)
        self.assertIsInstance(physics_obj, MovePhysics)
        self.assertEqual(physics_obj.current_cell, (2, 3))

    def test_create_default_physics(self):
        # במידה ולא מועבר 'type' או סוג לא מוכר, מחזיר אובייקט Physics רגיל
        cfg = {}
        physics_obj = self.factory.create((0, 0), cfg)
        self.assertTrue(hasattr(physics_obj, 'update'))  # Physics בסיסית אמורה להכיל update
        self.assertEqual(physics_obj.current_cell, (0, 0))

    def test_create_with_unknown_type(self):
        cfg = {'type': 'unknown_type'}
        physics_obj = self.factory.create((5, 5), cfg)
        # נניח שהפקטורי מחזיר Physics רגיל במקרה לא מוכר
        self.assertTrue(hasattr(physics_obj, 'update'))
        self.assertEqual(physics_obj.current_cell, (5, 5))