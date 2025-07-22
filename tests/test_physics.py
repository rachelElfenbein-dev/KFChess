import unittest
from unittest.mock import Mock, MagicMock
import math
from It1_interfaces.Physics import Physics, IdlePhysics, MovePhysics


class MockCommand:
    def __init__(self, target_cell=None, is_capture=False):
        self.target_cell = target_cell
        self.is_capture = is_capture


class MockBoard:
    def __init__(self, width=8, height=8):
        self.width = width
        self.height = height


class TestPhysicsBase(unittest.TestCase):
    """Test cases for the base Physics class"""
    
    def setUp(self):
        self.board = MockBoard()
        self.start_cell = (2, 3)
        self.physics = Physics(self.start_cell, self.board, speed_m_s=1.0)
    
    def test_initialization(self):
        """Test proper initialization of Physics object"""
        self.assertEqual(self.physics.current_cell, (2, 3))
        self.assertEqual(self.physics.current_pos_meters, (2.0, 3.0))
        self.assertEqual(self.physics.target_pos_meters, (2.0, 3.0))
        self.assertFalse(self.physics.is_moving)
        self.assertEqual(self.physics.speed_m_s, 1.0)
        self.assertEqual(self.physics.start_time_ms, 0)
        self.assertIsNone(self.physics.current_command)
    
    def test_cell_to_meters_conversion(self):
        """Test cell to meters conversion"""
        result = self.physics._cell_to_meters((5, 7))
        self.assertEqual(result, (5.0, 7.0))
    
    def test_meters_to_pixels_conversion(self):
        """Test meters to pixels conversion"""
        result = self.physics._meters_to_pixels((2.5, 3.5))
        self.assertEqual(result, (160, 224))  # 2.5*64, 3.5*64
    
    def test_get_pos_initial(self):
        """Test get_pos returns correct initial pixel position"""
        pos = self.physics.get_pos()
        self.assertEqual(pos, (128, 192))  # 2*64, 3*64
    
    def test_reset_with_valid_command(self):
        """Test reset with valid movement command"""
        cmd = MockCommand(target_cell=(4, 5))
        self.physics.reset(cmd)
        
        self.assertTrue(self.physics.is_moving)
        self.assertEqual(self.physics.target_pos_meters, (4.0, 5.0))
        self.assertEqual(self.physics.current_command, cmd)
    
    def test_reset_with_no_target_command(self):
        """Test reset with command that has no target"""
        cmd = MockCommand(target_cell=None)
        self.physics.reset(cmd)
        
        self.assertFalse(self.physics.is_moving)
        self.assertEqual(self.physics.current_command, cmd)
    
    def test_reset_with_command_without_target_attribute(self):
        """Test reset with command that doesn't have target_cell attribute"""
        cmd = Mock()
        del cmd.target_cell  # Remove the attribute
        self.physics.reset(cmd)
        
        self.assertFalse(self.physics.is_moving)
    
    def test_update_when_not_moving(self):
        """Test update when piece is not moving"""
        result = self.physics.update(1000)
        self.assertIsNone(result)
    
    def test_update_movement_completion(self):
        """Test update when movement is completed"""
        cmd = MockCommand(target_cell=(3, 3))  # Move 1 cell right
        self.physics.reset(cmd)
        
        # First update sets start time
        result = self.physics.update(1000)
        self.assertIsNone(result)
        self.assertTrue(self.physics.is_moving)
        
        # Second update after enough time should complete movement
        result = self.physics.update(2000)  # 1 second later, should complete 1-meter move
        self.assertEqual(result, cmd)
        self.assertFalse(self.physics.is_moving)
        self.assertEqual(self.physics.current_cell, (3, 3))
        self.assertEqual(self.physics.current_pos_meters, (3.0, 3.0))
    
    def test_update_movement_in_progress(self):
        """Test update during movement progression"""
        cmd = MockCommand(target_cell=(4, 3))  # Move 2 cells right
        self.physics.reset(cmd)
        
        # Start movement
        self.physics.update(1000)
        
        # Check position after half the required time
        self.physics.update(2000)  # 1 second later, should be halfway through 2-meter move
        
        # Should be at position (3.0, 3.0) - halfway
        expected_x = 2.0 + (2.0 * 0.5)  # start + (distance * progress)
        self.assertAlmostEqual(self.physics.current_pos_meters[0], expected_x, places=5)
        self.assertEqual(self.physics.current_pos_meters[1], 3.0)
        self.assertTrue(self.physics.is_moving)
    
    def test_update_zero_distance_movement(self):
        """Test update when target is same as current position"""
        cmd = MockCommand(target_cell=(2, 3))  # Same as start position
        self.physics.reset(cmd)
        
        result = self.physics.update(1000)
        self.assertFalse(self.physics.is_moving)
        self.assertIsNone(result)
    
    def test_diagonal_movement(self):
        """Test diagonal movement calculation"""
        cmd = MockCommand(target_cell=(3, 4))  # Diagonal move
        self.physics.reset(cmd)
        
        # Start movement
        self.physics.update(1000)
        
        # Move for exactly the time needed for sqrt(2) distance at 1 m/s
        diagonal_distance = math.sqrt(2)
        time_needed = diagonal_distance * 1000  # Convert to ms
        
        result = self.physics.update(1000 + int(time_needed) + 1)
        self.assertEqual(result, cmd)
        self.assertFalse(self.physics.is_moving)
        self.assertEqual(self.physics.current_cell, (3, 4))
    
    def test_can_be_captured_states(self):
        """Test can_be_captured in different states"""
        # Not moving
        self.assertTrue(self.physics.can_be_captured())
        
        # Moving
        cmd = MockCommand(target_cell=(3, 3))
        self.physics.reset(cmd)
        self.assertFalse(self.physics.can_be_captured())
    
    def test_can_capture_states(self):
        """Test can_capture in different states"""
        # Not moving
        self.assertTrue(self.physics.can_capture())
        
        # Moving
        cmd = MockCommand(target_cell=(3, 3))
        self.physics.reset(cmd)
        self.assertFalse(self.physics.can_capture())
    
    def test_multiple_consecutive_movements(self):
        """Test multiple movements in sequence"""
        # First movement
        cmd1 = MockCommand(target_cell=(3, 3))
        self.physics.reset(cmd1)
        self.physics.update(1000)
        result = self.physics.update(2000)
        self.assertEqual(result, cmd1)
        
        # Second movement from new position
        cmd2 = MockCommand(target_cell=(3, 5))
        self.physics.reset(cmd2)
        self.physics.update(3000)
        result = self.physics.update(5000)
        self.assertEqual(result, cmd2)
        self.assertEqual(self.physics.current_cell, (3, 5))


class TestIdlePhysics(unittest.TestCase):
    """Test cases for IdlePhysics class"""
    
    def setUp(self):
        self.board = MockBoard()
        self.start_cell = (1, 1)
        self.physics = IdlePhysics(self.start_cell, self.board)
    
    def test_initialization(self):
        """Test IdlePhysics initialization"""
        self.assertEqual(self.physics.current_cell, (1, 1))
        self.assertFalse(self.physics.is_moving)
    
    def test_reset_ignores_commands(self):
        """Test that reset ignores movement commands"""
        cmd = MockCommand(target_cell=(2, 2))
        initial_pos = self.physics.current_pos_meters
        
        self.physics.reset(cmd)
        
        self.assertEqual(self.physics.current_pos_meters, initial_pos)
        self.assertFalse(self.physics.is_moving)
    
    def test_update_always_returns_none(self):
        """Test that update always returns None"""
        result = self.physics.update(1000)
        self.assertIsNone(result)
        
        # Even after reset with command
        cmd = MockCommand(target_cell=(2, 2))
        self.physics.reset(cmd)
        result = self.physics.update(2000)
        self.assertIsNone(result)
    
    def test_capture_abilities(self):
        """Test IdlePhysics capture abilities"""
        self.assertTrue(self.physics.can_be_captured())
        self.assertFalse(self.physics.can_capture())
    
    def test_position_never_changes(self):
        """Test that position never changes regardless of commands"""
        initial_pos = self.physics.get_pos()
        
        cmd = MockCommand(target_cell=(5, 5))
        self.physics.reset(cmd)
        self.physics.update(1000)
        self.physics.update(5000)
        
        self.assertEqual(self.physics.get_pos(), initial_pos)


class TestMovePhysics(unittest.TestCase):
    """Test cases for MovePhysics class"""
    
    def setUp(self):
        self.board = MockBoard()
        self.start_cell = (2, 2)
        self.physics = MovePhysics(self.start_cell, self.board, speed_m_s=2.0)
    
    def test_initialization(self):
        """Test MovePhysics initialization"""
        self.assertEqual(self.physics.current_cell, (2, 2))
        self.assertEqual(self.physics.speed_m_s, 2.0)
        self.assertTrue(self.physics.can_move_while_capturing)
        self.assertEqual(self.physics.capture_immunity_duration_ms, 500)
        self.assertEqual(self.physics.last_capture_time_ms, 0)
    
    def test_faster_movement(self):
        """Test that MovePhysics moves faster than base Physics"""
        cmd = MockCommand(target_cell=(4, 2))  # 2 meter move
        self.physics.reset(cmd)
        
        # Start movement
        self.physics.update(1000)
        
        # Should complete in 1 second at 2 m/s
        result = self.physics.update(2000)
        self.assertEqual(result, cmd)
        self.assertEqual(self.physics.current_cell, (4, 2))
    
    def test_capture_command_handling(self):
        """Test handling of capture commands"""
        cmd = MockCommand(target_cell=(3, 3), is_capture=True)
        self.physics.reset(cmd)
        
        # Update should set capture time
        self.physics.update(1000)
        # Note: In real implementation, you might want to track this better
        
        self.assertEqual(self.physics.current_command, cmd)
    
    def test_can_capture_while_moving(self):
        """Test capture ability while moving"""
        cmd = MockCommand(target_cell=(3, 3))
        self.physics.reset(cmd)
        
        # Can capture even while moving (default behavior)
        self.assertTrue(self.physics.can_capture())
    
    def test_capture_ability_configuration(self):
        """Test configuring capture ability while moving"""
        self.physics.set_capture_ability(False)
        self.assertFalse(self.physics.can_move_while_capturing)
        
        # Start moving
        cmd = MockCommand(target_cell=(3, 3))
        self.physics.reset(cmd)
        
        # Now should not be able to capture while moving
        self.assertFalse(self.physics.can_capture())
        
        # But should be able to capture when not moving
        self.physics.update(1000)
        result = self.physics.update(2000)  # Complete movement (1 meter at 2 m/s = 0.5s)
        self.assertEqual(result, cmd)  # Verify movement completed
        self.assertFalse(self.physics.is_moving)  # Verify not moving
        self.assertTrue(self.physics.can_capture())
    
    def test_capture_immunity(self):
        """Test capture immunity after capturing"""
        # This is a simplified test since we don't have access to current time
        # In a real scenario, you'd want to pass current time to can_be_captured()
        cmd = MockCommand(target_cell=(3, 3), is_capture=True)
        self.physics.reset(cmd)
        self.physics.update(1000)
        
        # After a capture, should have immunity (simplified check)
        # In real implementation, this would need current time parameter
        result = self.physics.can_be_captured()
        # This will be False due to simplified immunity logic
        self.assertFalse(result)


class TestPhysicsEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        self.board = MockBoard()
        self.physics = Physics((0, 0), self.board)
    
    def test_negative_coordinates(self):
        """Test handling of negative coordinates"""
        self.physics.current_cell = (-1, -2)
        self.physics.current_pos_meters = (-1.0, -2.0)
        
        pos = self.physics.get_pos()
        self.assertEqual(pos, (-64, -128))
    
    def test_zero_speed(self):
        """Test behavior with zero speed"""
        physics = Physics((0, 0), self.board, speed_m_s=0.0)
        cmd = MockCommand(target_cell=(1, 1))
        physics.reset(cmd)
        
        physics.update(1000)
        # With zero speed, movement should never complete naturally
        result = physics.update(999999)  # Very long time
        self.assertIsNone(result)  # Should still be moving (or handle division by zero)
    
    def test_very_high_speed(self):
        """Test behavior with very high speed"""
        physics = Physics((0, 0), self.board, speed_m_s=1000000.0)
        cmd = MockCommand(target_cell=(10, 10))
        physics.reset(cmd)
        
        physics.update(1000)
        result = physics.update(1001)  # Just 1ms later
        self.assertEqual(result, cmd)  # Should complete almost immediately
    
    def test_floating_point_precision(self):
        """Test floating point precision in calculations"""
        physics = Physics((0, 0), self.board, speed_m_s=1.0/3.0)  # Repeating decimal
        cmd = MockCommand(target_cell=(1, 0))
        physics.reset(cmd)
        
        physics.update(1000)
        result = physics.update(4000)  # 3 seconds should complete 1-meter move
        self.assertEqual(result, cmd)
    
    def test_very_large_coordinates(self):
        """Test handling of very large coordinates"""
        large_coord = (999999, 999999)
        physics = Physics(large_coord, self.board)
        
        pos = physics.get_pos()
        self.assertEqual(pos, (999999 * 64, 999999 * 64))
    
    def test_update_with_negative_time(self):
        """Test update with negative time values"""
        cmd = MockCommand(target_cell=(1, 1))
        self.physics.reset(cmd)
        
        # Start with positive time
        self.physics.update(1000)
        
        # Then give negative time (should handle gracefully)
        result = self.physics.update(-500)
        # Should either ignore or handle gracefully, not crash
        self.assertIsNotNone(self.physics)  # Just ensure no crash
    
    def test_rapid_consecutive_updates(self):
        """Test many rapid consecutive updates"""
        cmd = MockCommand(target_cell=(2, 2))
        self.physics.reset(cmd)
        
        # Many rapid updates
        for i in range(1000, 1100):
            result = self.physics.update(i)
            if result is not None:
                break
        
        # Should handle without issues
        self.assertIsNotNone(self.physics)
    
    def test_command_without_required_attributes(self):
        """Test commands that don't have expected attributes"""
        incomplete_cmd = Mock()
        # Don't set any attributes
        
        # Should not crash when trying to access missing attributes
        try:
            self.physics.reset(incomplete_cmd)
        except AttributeError:
            self.fail("Physics.reset() should handle commands without target_cell attribute")


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [TestPhysicsBase, TestIdlePhysics, TestMovePhysics, TestPhysicsEdgeCases]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}")
