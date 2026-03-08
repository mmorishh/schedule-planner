import time
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Dict, List
from models import Graph
from algorithms.branch_bound import BranchBoundSolver
from algorithms.independent_sets import IndependentSetSolver
from algorithms.brown import BrownAlgorithm

class PerformanceTester:
    def __init__(self):
        self.results = []
        
    def test_algorithm(self, graph, algorithm_name: str) -> Dict:
        """Тестирование одного алгоритма"""
        if algorithm_name == "BranchBound":
            solver = BranchBoundSolver(graph)
        elif algorithm_name == "Independent":
            solver = IndependentSetSolver(graph)
        elif algorithm_name == "Brown":
            solver = BrownAlgorithm(graph)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm_name}")
        
        start_time = time.time()
        colors, num_colors = solver.solve()
        elapsed = time.time() - start_time
        
        return {
            "algorithm": algorithm_name,
            "num_vertices": graph.n,
            "num_colors": num_colors,
            "time": elapsed,
            "stats": solver.get_statistics()
        }
    
    def test_graph_family(self, sizes: List[int], densities: List[float], 
                         algorithms: List[str], runs: int = 3):
        """Тестирование на семействе графов"""
        from generate_test_data import TestDataGenerator
        generator = TestDataGenerator()
        
        for size in sizes:
            for density in densities:
                print(f"\nТестирование: размер={size}, плотность={density}")
                
                for run in range(runs):
                    # Генерируем граф с заданными параметрами
                    graph = self._generate_random_graph(size, density)
                    
                    for algo in algorithms:
                        try:
                            result = self.test_algorithm(graph, algo)
                            result["size"] = size
                            result["density"] = density
                            result["run"] = run
                            self.results.append(result)
                            print(f"  {algo}: {result['time']:.3f} сек, {result['num_colors']} цветов")
                        except Exception as e:
                            print(f"  {algo} ошибка: {e}")
    
    def _generate_random_graph(self, n: int, density: float):
        """Генерация случайного графа с заданной плотностью"""
        import random
        from models import Graph, Lesson
        
        lessons = []
        for i in range(n):
            lesson = Lesson(
                id=f"v{i}",
                subject=f"S{i}",
                type="lecture",
                groups=[f"G{i%5}"],
                teacher=f"T{i%10}",
                classroom=f"R{i%8}",
                hours_per_week=1,
                instance=0
            )
            lessons.append(lesson)
        
        graph = Graph(lessons)
        
        # Создаем матрицу смежности с заданной плотностью
        random.seed(42 + n * int(density * 100))
        adj = [[False]*n for _ in range(n)]
        for i in range(n):
            for j in range(i+1, n):
                if random.random() < density:
                    adj[i][j] = adj[j][i] = True
        graph.adj = adj
        
        return graph
    
    def analyze_results(self):
        """Анализ результатов тестирования"""
        df = pd.DataFrame(self.results)
        
        if df.empty:
            print("Нет данных для анализа")
            return
        
        print("\n=== АНАЛИЗ РЕЗУЛЬТАТОВ ===")
        
        # Сводная статистика
        summary = df.groupby(['algorithm', 'size', 'density']).agg({
            'time': ['mean', 'std'],
            'num_colors': 'mean'
        }).round(3)
        
        print("\nСводная статистика:")
        print(summary)
        
        # Построение графиков
        self._plot_time_vs_size(df)
        self._plot_time_vs_density(df)
        
        return df
    
    def _plot_time_vs_size(self, df):
        """График зависимости времени от размера"""
        plt.figure(figsize=(12, 5))
        
        # Для разных плотностей
        densities = df['density'].unique()
        colors = ['blue', 'red', 'green']
        
        for i, density in enumerate(sorted(densities)):
            plt.subplot(1, len(densities), i+1)
            
            subset = df[df['density'] == density]
            for algo in subset['algorithm'].unique():
                algo_data = subset[subset['algorithm'] == algo]
                sizes = sorted(algo_data['size'].unique())
                times = [algo_data[algo_data['size'] == s]['time'].mean() for s in sizes]
                
                plt.plot(sizes, times, 'o-', label=algo, color=colors[i])
            
            plt.xlabel('Размер графа (вершин)')
            plt.ylabel('Время (сек)')
            plt.title(f'Плотность = {density}')
            plt.legend()
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('performance_analysis.png', dpi=150)
        plt.show()
    
    def _plot_time_vs_density(self, df):
        """График зависимости времени от плотности"""
        plt.figure(figsize=(10, 6))
        
        sizes = sorted(df['size'].unique())
        markers = ['o', 's', '^', 'D']
        
        for i, size in enumerate(sizes):
            subset = df[df['size'] == size]
            for algo in subset['algorithm'].unique():
                algo_data = subset[subset['algorithm'] == algo]
                densities = sorted(algo_data['density'].unique())
                times = [algo_data[algo_data['density'] == d]['time'].mean() for d in densities]
                
                plt.plot(densities, times, marker=markers[i % len(markers)], 
                        label=f'{algo} (size={size})')
        
        plt.xlabel('Плотность графа')
        plt.ylabel('Время (сек)')
        plt.title('Зависимость времени от плотности графа')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('density_analysis.png', dpi=150)
        plt.show()

def main():
    # Создаем тестер
    tester = PerformanceTester()
    
    # Проводим предварительный эксперимент для определения t1
    print("=== ПРЕДВАРИТЕЛЬНЫЙ ЭКСПЕРИМЕНТ ===")
    prelim_sizes = [10, 20, 30, 40, 50]
    prelim_densities = [0.3]
    
    for size in prelim_sizes:
        graph = tester._generate_random_graph(size, 0.3)
        result = tester.test_algorithm(graph, "BranchBound")
        print(f"Размер {size}: {result['time']:.3f} сек")
        
        if result['time'] > 2.0:  # t1 = 2 секунды
            print(f"Максимальный размер для t1: {size}")
            break
    
    # Основные тесты
    print("\n=== ОСНОВНЫЕ ТЕСТЫ ===")
    tester.test_graph_family(
        sizes=[10, 20, 50, 100],
        densities=[0.1, 0.3, 0.5, 0.8],
        algorithms=["BranchBound", "Independent", "Brown"],
        runs=2
    )
    
    # Анализ результатов
    df = tester.analyze_results()
    
    # Сохраняем результаты
    with open('performance_results.json', 'w', encoding='utf-8') as f:
        json.dump(tester.results, f, indent=2, default=str)

if __name__ == "__main__":
    main()