import sys
import os
import unittest
import pytest
from parameterized import parameterized
from hamcrest import assert_that, is_, has_item, contains_string, greater_than
from unittest.mock import Mock, patch, MagicMock
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Group, Teacher, Classroom, Subject, Lesson, Graph
from algorithms.branch_bound import BranchBoundSolver
from algorithms.independent_sets import IndependentSetSolver
from algorithms.brown import BrownAlgorithm



# ТЕХНИКА 1: АНАЛИЗ ГРАНИЧНЫХ ЗНАЧЕНИЙ

class TestBoundaryValueAnalysis(unittest.TestCase):
    """Тестирование граничных значений"""
    
    def setUp(self):
        self.teacher = Teacher("t1", "Teacher", "Math")
        self.classroom = Classroom("c1", "Room", 30)
        self.subject = Subject("s1", "Math", 1)
    
    @parameterized.expand([
        ("empty_graph", [], 0, None),
        ("single_vertex", [{
            "id": "l1_0", "subject": "s1", "type": "lecture",
            "groups": ["g1"], "teacher": "t1", "classroom": "c1",
            "hours_per_week": 1, "instance": 0
        }], 1, 1),
        ("two_vertices_no_conflict", [
            {"id": "l1_0", "subject": "s1", "type": "lecture", "groups": ["g1"], "teacher": "t1", "classroom": "c1", "hours_per_week": 1, "instance": 0},
            {"id": "l2_0", "subject": "s1", "type": "lecture", "groups": ["g2"], "teacher": "t2", "classroom": "c2", "hours_per_week": 1, "instance": 0}
        ], 2, 1),
        ("two_vertices_conflict", [
            {"id": "l1_0", "subject": "s1", "type": "lecture", "groups": ["g1"], "teacher": "t1", "classroom": "c1", "hours_per_week": 1, "instance": 0},
            {"id": "l2_0", "subject": "s1", "type": "lecture", "groups": ["g1"], "teacher": "t2", "classroom": "c2", "hours_per_week": 1, "instance": 0}
        ], 2, 2),
    ])
    def test_graph_boundaries(self, name, lessons_data, expected_vertices, expected_colors_min):
        groups = {"g1": Group("g1", "Group 1"), "g2": Group("g2", "Group 2")}
        teachers = {"t1": Teacher("t1", "Teacher 1"), "t2": Teacher("t2", "Teacher 2")}
        classrooms = {"c1": Classroom("c1", "Room 1"), "c2": Classroom("c2", "Room 2")}
        subjects = {"s1": Subject("s1", "Math")}
        
        lessons = []
        for ld in lessons_data:
            lessons.append(Lesson(**ld))
        
        graph = Graph(lessons, groups, teachers, classrooms, subjects)
        self.assertEqual(len(graph.lessons), expected_vertices)



# ТЕХНИКА 2: ЭКВИВАЛЕНТНОЕ РАЗБИЕНИЕ

class TestEquivalencePartitioning(unittest.TestCase):
    """Разбиение на классы эквивалентности"""
    
    def setUp(self):
        self.teacher = Teacher("t1", "Teacher", "Math")
        self.classroom = Classroom("c1", "Room", 30)
        self.subject = Subject("s1", "Math", 1)
    
    def create_test_graph(self, num_lessons, conflict_probability=0.5):
        """Создание тестового графа"""
        lessons = []
        groups = {}
        teachers = {}
        classrooms = {}
        
        for i in range(num_lessons):
            gid = f"g{i}"
            tid = f"t{i}"
            cid = f"c{i}"
            groups[gid] = Group(gid, f"Group {i}")
            teachers[tid] = Teacher(tid, f"Teacher {i}")
            classrooms[cid] = Classroom(cid, f"Room {i}")
            
            lesson = Lesson(
                id=f"l{i}_0",
                subject="s1",
                type="lecture",
                groups=[gid],
                teacher=tid,
                classroom=cid,
                hours_per_week=1,
                instance=0
            )
            lessons.append(lesson)
        
        return Graph(lessons, groups, teachers, classrooms, {"s1": self.subject})
    
    def test_sparse_graph(self):
        """Класс 1: Разреженный граф"""
        graph = self.create_test_graph(3)
        self.assertGreaterEqual(graph.n, 1)
    
    def test_dense_graph(self):
        """Класс 2: Плотный граф"""
        graph = self.create_test_graph(5)
        self.assertGreaterEqual(graph.n, 1)
    
    def test_complete_graph(self):
        """Класс 3: Полный граф"""
        lessons = []
        for i in range(3):
            lesson = Lesson(
                id=f"l{i}_0",
                subject="s1",
                type="lecture",
                groups=["g1"],
                teacher=f"t{i}",
                classroom=f"c{i}",
                hours_per_week=1,
                instance=0
            )
            lessons.append(lesson)
        
        groups = {"g1": Group("g1", "Group 1")}
        teachers = {f"t{i}": Teacher(f"t{i}", f"Teacher {i}") for i in range(3)}
        classrooms = {f"c{i}": Classroom(f"c{i}", f"Room {i}") for i in range(3)}
        graph = Graph(lessons, groups, teachers, classrooms, {"s1": self.subject})
        
        solver = BranchBoundSolver(graph)
        colors, num = solver.solve()
        self.assertLessEqual(num, len(lessons))



# ТЕХНИКА 3: ТЕСТИРОВАНИЕ ВЕТВЛЕНИЙ


class TestBranchTesting(unittest.TestCase):
    """Тестирование всех ветвлений в коде"""
    
    def setUp(self):
        self.lesson1 = Lesson(
            id="l1_0", subject="s1", type="lecture",
            groups=["g1"], teacher="t1", classroom="c1",
            hours_per_week=1, instance=0
        )
        self.lesson2 = Lesson(
            id="l2_0", subject="s1", type="lecture",
            groups=["g1"], teacher="t2", classroom="c2",
            hours_per_week=1, instance=0
        )
        groups = {"g1": Group("g1", "Group 1")}
        teachers = {"t1": Teacher("t1", "Teacher 1"), "t2": Teacher("t2", "Teacher 2")}
        classrooms = {"c1": Classroom("c1", "Room 1"), "c2": Classroom("c2", "Room 2")}
        self.graph = Graph([self.lesson1, self.lesson2], groups, teachers, classrooms, {"s1": Subject("s1", "Math")})
        self.solver = BranchBoundSolver(self.graph)
    
    def test_is_safe_true_branch(self):
        """Ветка: is_safe = True"""
        colors = [-1, -1]
        result = self.graph.is_safe(0, 0, colors)
        self.assertTrue(result)
    
    def test_is_safe_false_branch(self):
        """Ветка: is_safe = False"""
        colors = [0, -1]
        result = self.graph.is_safe(1, 0, colors)
        self.assertFalse(result)
    
    def test_select_vertex_with_colored_neighbors(self):
        """Ветка: выбор вершины с окрашенными соседями"""
        colors = [0, -1]
        v = self.solver._select(colors)
        self.assertEqual(v, 1)
    
    def test_select_vertex_no_colored_neighbors(self):
        """Ветка: выбор вершины без окрашенных соседей"""
        colors = [-1, -1]
        v = self.solver._select(colors)
        self.assertIn(v, [0, 1])



# ТЕХНИКА 4: ТЕСТИРОВАНИЕ ОПЕРАТОРОВ

class TestStatementTesting(unittest.TestCase):
    """Покрытие всех операторов"""
    
    def test_lesson_conflicts_all_cases(self):
        """Проверка всех операторов в Lesson.conflicts_with"""
        lesson1 = Lesson("l1_0", "s1", "lecture", ["g1"], "t1", "c1", 1, 0)
        
        # Случай 1: одно и то же занятие
        self.assertFalse(lesson1.conflicts_with(lesson1))
        
        # Случай 2: конфликт по группе
        lesson2 = Lesson("l2_0", "s1", "lecture", ["g1"], "t2", "c2", 1, 0)
        self.assertTrue(lesson1.conflicts_with(lesson2))
        
        # Случай 3: конфликт по преподавателю
        lesson3 = Lesson("l3_0", "s1", "lecture", ["g2"], "t1", "c3", 1, 0)
        self.assertTrue(lesson1.conflicts_with(lesson3))
        
        # Случай 4: конфликт по аудитории
        lesson4 = Lesson("l4_0", "s1", "lecture", ["g2"], "t2", "c1", 1, 0)
        self.assertTrue(lesson1.conflicts_with(lesson4))
        
        # Случай 5: нет конфликта
        lesson5 = Lesson("l5_0", "s1", "lecture", ["g2"], "t2", "c2", 1, 0)
        self.assertFalse(lesson1.conflicts_with(lesson5))
    
    def test_graph_build_adj_all_cases(self):
        """Проверка построения матрицы смежности"""
        lesson1 = Lesson("l1_0", "s1", "lecture", ["g1"], "t1", "c1", 1, 0)
        lesson2 = Lesson("l2_0", "s1", "lecture", ["g1"], "t2", "c2", 1, 0)
        lesson3 = Lesson("l3_0", "s1", "lecture", ["g2"], "t3", "c3", 1, 0)
        
        groups = {"g1": Group("g1", "G1"), "g2": Group("g2", "G2")}
        teachers = {"t1": Teacher("t1", "T1"), "t2": Teacher("t2", "T2"), "t3": Teacher("t3", "T3")}
        classrooms = {"c1": Classroom("c1", "C1"), "c2": Classroom("c2", "C2"), "c3": Classroom("c3", "C3")}
        graph = Graph([lesson1, lesson2, lesson3], groups, teachers, classrooms, {"s1": Subject("s1", "S1")})
        
        self.assertTrue(graph.adj[0][1])
        self.assertFalse(graph.adj[0][2])
        self.assertFalse(graph.adj[1][2])



# МОКИРОВАНИЕ


class TestMocking(unittest.TestCase):
    """Тестирование с использованием моков"""
    
    @patch('models.Graph.load_from_json')
    def test_mock_1_json_loading(self, mock_load):
        mock_graph = MagicMock()
        mock_graph.lessons = []
        mock_graph.n = 0
        mock_load.return_value = mock_graph
        
        result = Graph.load_from_json("fake_path.json")
        mock_load.assert_called_once_with("fake_path.json")
        self.assertEqual(result, mock_graph)
    
    @patch('algorithms.branch_bound.BranchBoundSolver._upper_bound')
    def test_mock_2_upper_bound(self, mock_upper):
        mock_upper.return_value = [0, 1, 0]
        lesson = Lesson("l1_0", "s1", "lecture", ["g1"], "t1", "c1", 1, 0)
        graph = Graph([lesson], {}, {}, {}, {})
        solver = BranchBoundSolver(graph)
        result = solver._upper_bound()
        self.assertEqual(result, [0, 1, 0])
    
    def test_mock_3_context_manager(self):
        with patch('builtins.open', unittest.mock.mock_open(read_data='{"lessons": []}')):
            data = json.loads('{"lessons": []}')
            self.assertEqual(data, {"lessons": []})



# ПАРАМЕТРИЗИРОВАННЫЕ ТЕСТЫ


class TestParameterized(unittest.TestCase):
    """Параметризированные тесты"""
    
    @parameterized.expand([
        (0, 0, True),   # вершина 0, цвет 0 - можно
        (1, 0, False),  # вершина 1, цвет 0 - нельзя (конфликт)
        (1, 1, True),   # вершина 1, цвет 1 - можно
    ])
    def test_is_safe_parameterized(self, vertex, color, expected):
        lesson1 = Lesson("l1_0", "s1", "lecture", ["g1"], "t1", "c1", 1, 0)
        lesson2 = Lesson("l2_0", "s1", "lecture", ["g1"], "t2", "c2", 1, 0)
        graph = Graph([lesson1, lesson2], {}, {}, {}, {})
        colors = [0, -1]
        result = graph.is_safe(vertex, color, colors)
        self.assertEqual(result, expected)



# МАТЧЕРЫ HAMCREST


class TestMatchers(unittest.TestCase):
    """Использование матчеров Hamcrest"""
    
    def test_hamcrest_matchers(self):
        assert_that(5, is_(5))
        assert_that("test", is_("test"))
        test_list = [1, 2, 3, 4, 5]
        assert_that(test_list, has_item(3))
        test_str = "Hello world"
        assert_that(test_str, contains_string("world"))



# СРАВНЕНИЕ АЛГОРИТМОВ


class TestAlgorithmComparison(unittest.TestCase):
    """Сравнение результатов разных алгоритмов"""
    
    def setUp(self):
        lessons = []
        groups = {}
        teachers = {}
        classrooms = {}
        
        for i in range(3):
            gid = f"g{i}"
            tid = f"t{i}"
            cid = f"c{i}"
            groups[gid] = Group(gid, f"G{i}")
            teachers[tid] = Teacher(tid, f"T{i}")
            classrooms[cid] = Classroom(cid, f"C{i}")
            
            lesson = Lesson(
                id=f"l{i}_0",
                subject="s1",
                type="lecture",
                groups=[gid],
                teacher=tid,
                classroom=cid,
                hours_per_week=1,
                instance=0
            )
            lessons.append(lesson)
        
        self.graph = Graph(lessons, groups, teachers, classrooms, {"s1": Subject("s1", "Math")})
    
    def test_algorithms_consistency(self):
        solvers = [
            ("BranchBound", BranchBoundSolver),
            ("Independent", IndependentSetSolver),
            ("Brown", BrownAlgorithm)
        ]
        
        for name, Solver in solvers:
            solver = Solver(self.graph)
            colors, num = solver.solve()
            
            self.assertIsNotNone(colors, f"{name} вернул None")
            self.assertNotIn(-1, colors, f"{name} оставил непокрашенные вершины")
            self.assertGreater(num, 0, f"{name} вернул 0 цветов")
            
            for i in range(self.graph.n):
                for j in self.graph.neighbors(i):
                    self.assertNotEqual(colors[i], colors[j], 
                        f"{name}: конфликт между {i} и {j}")



# ТЕСТЫ С ПРЕДПОЛОЖЕНИЯМИ


class TestAssumptions(unittest.TestCase):
    """Тесты с предположениями (assumptions)"""
    
    def test_with_assumptions_soft(self):
        """Мягкие предположения с pytest.assume"""
        # Создаём граф с одним занятием
        lesson = Lesson("l1_0", "s1", "lecture", ["g1"], "t1", "c1", 1, 0)
        graph = Graph([lesson], {}, {}, {}, {})
        
        # МЯГКИЕ ПРЕДПОЛОЖЕНИЯ - не останавливают тест, даже если ложные
        pytest.assume(len(graph.lessons) > 0, "Граф должен содержать занятия")
        pytest.assume(graph.n > 0, "Количество вершин должно быть положительным")
        pytest.assume(graph.lessons[0].color == -1, "Изначально все вершины должны быть непокрашены")
        
        # Основная проверка
        solver = BranchBoundSolver(graph)
        colors, num = solver.solve()
        self.assertEqual(num, 1)
        self.assertEqual(len(colors), 1)
        self.assertEqual(colors[0], 0)
    
    @pytest.mark.skipif(True, reason="Демонстрация пропуска теста - это условие всегда True")
    def test_skipped_demo(self):
        """Демонстрация использования @pytest.mark.skipif (жёсткое предположение)"""
        # Этот тест всегда будет пропущен из-за условия True
        lesson = Lesson("l1_0", "s1", "lecture", ["g1"], "t1", "c1", 1, 0)
        graph = Graph([lesson], {}, {}, {}, {})
        solver = BranchBoundSolver(graph)
        colors, num = solver.solve()
        self.assertEqual(num, 1)
    
    @pytest.mark.skipif(not hasattr(__builtins__, 'print'), 
                       reason="Пропускаем, если нет функции print (никогда не случится)")
    def test_assumptions_hard_print(self):
        """Жёсткое предположение с проверкой наличия функции print"""
        lesson = Lesson("l1_0", "s1", "lecture", ["g1"], "t1", "c1", 1, 0)
        graph = Graph([lesson], {}, {}, {}, {})
        
        # Мягкие предположения внутри
        pytest.assume(graph.n == 1, "Должна быть ровно одна вершина")
        
        # Проверка
        self.assertEqual(len(graph.lessons), 1)

if __name__ == '__main__':
    unittest.main()
