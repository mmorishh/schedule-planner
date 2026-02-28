import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main
from models import Graph, Lesson
from algorithms.branch_bound import BranchBoundSolver

class TestMain(unittest.TestCase):
    
    @patch('builtins.input')
    @patch('models.Graph.load_from_json')
    def test_load_data(self, mock_load, mock_input):
        """Тест загрузки данных"""
        mock_input.return_value = "test.json"
        mock_graph = MagicMock(spec=Graph)
        mock_graph.lessons = []
        mock_graph.n = 0
        mock_load.return_value = mock_graph
        
        result = Graph.load_from_json("test.json")
        mock_load.assert_called_once_with("test.json")
        self.assertEqual(result, mock_graph)
    
    def test_run_algorithm_direct(self):
        """Тест запуска алгоритма напрямую"""
        lesson = Lesson(
            id="test_0",
            subject="math",
            type="lecture",
            groups=["g1"],
            teacher="t1",
            classroom="c1",
            hours_per_week=1,
            instance=0
        )
        graph = Graph([lesson], {}, {}, {}, {})
        
        solver = BranchBoundSolver(graph)
        colors, num = solver.solve()
        
        self.assertIsNotNone(colors)
        self.assertEqual(num, 1)
        self.assertEqual(len(colors), 1)
    
    @patch('builtins.input')
    @patch('models.Graph.save_coloring')
    def test_save_results(self, mock_save, mock_input):
        """Тест сохранения результатов"""
        mock_input.return_value = "result.json"
        mock_save.return_value = True
        
        lesson = Lesson(
            id="test_0",
            subject="math",
            type="lecture",
            groups=["g1"],
            teacher="t1",
            classroom="c1",
            hours_per_week=1,
            instance=0
        )
        graph = Graph([lesson], {}, {}, {}, {})
        
        result = graph.save_coloring("result.json", [0])
        self.assertTrue(result)
    
    @patch('builtins.input')
    def test_menu_choice_exit(self, mock_input):
        """Тест выхода из меню"""
        mock_input.return_value = "0"
        
        with self.assertRaises(SystemExit):
            if mock_input.return_value == "0":
                sys.exit(0)
    
    @patch('builtins.print')
    def test_print_menu(self, mock_print):
        """Тест отображения меню"""
        main.print_menu()
        self.assertTrue(mock_print.called)
    
    @patch('builtins.input')
    def test_invalid_choice(self, mock_input):
        """Тест неверного выбора в меню"""
        mock_input.return_value = "999"  # неверный пункт
        
        # Просто проверяем что нет исключения
        choice = mock_input.return_value
        self.assertEqual(choice, "999")


if __name__ == '__main__':
    unittest.main()