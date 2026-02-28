import sys
import os
import time
from models import Graph, Lesson, Group, Teacher, Classroom, Subject
from algorithms.branch_bound import BranchBoundSolver
from algorithms.independent_sets import IndependentSetSolver
from algorithms.brown import BrownAlgorithm

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    print("КОНСОЛЬНЫЙ ПЛАНИРОВЩИК РАСПИСАНИЯ УНИВЕРСИТЕТА")
    print("1. Загрузить данные из JSON")
    print("2. Метод ветвей и границ")
    print("3. Независимые множества")
    print("4. Алгоритм Брауна")
    print("5. Сравнить все алгоритмы")
    print("6. Сохранить результат")
    print("7. Показать расписание")
    print("0. Выход")

def show_schedule(graph, colors, algo_name):
    if not graph or not colors or -1 in colors:
        print("Расписание не рассчитано")
        return
    
    time_map = {
        0: "ПН 1", 1: "ПН 2", 2: "ПН 3",
        3: "ПН 4", 4: "ПН 5",
        5: "ВТ 1", 6: "ВТ 2", 7: "ВТ 3",
        8: "ВТ 4", 9: "ВТ 5",
        10: "СР 1", 11: "СР 2", 12: "СР 3",
        13: "СР 4", 14: "СР 5",
        15: "ЧТ 1", 16: "ЧТ 2", 17: "ЧТ 3",
        18: "ЧТ 4", 19: "ЧТ 5",
        20: "ПТ 1", 21: "ПТ 2", 22: "ПТ 3",
        23: "ПТ 4", 24: "ПТ 5",
        25: "СБ 1", 26: "СБ 2", 27: "СБ 3"
    }
    
    num_colors = max(colors) + 1
    print(f"\n{algo_name} - всего слотов: {num_colors}")
    
    slots = {}
    for i, lesson in enumerate(graph.lessons):
        slot = colors[i]
        if slot not in slots:
            slots[slot] = []
        slots[slot].append((i, lesson))
    
    for slot in sorted(slots.keys()):
        time_str = time_map.get(slot, f"Слот {slot+1}")
        print(f"\n{time_str}:")
        for idx, lesson in slots[slot]:
            groups_str = ", ".join(lesson.groups)
            teacher = graph.teachers.get(lesson.teacher, lesson.teacher)
            classroom = graph.classrooms.get(lesson.classroom, lesson.classroom)
            subject = graph.subjects.get(lesson.subject, lesson.subject)
            print(f"  [{idx}] {subject} [{lesson.type}] | Группы: {groups_str} | {teacher} | {classroom}")

def main():
    graph = None
    colors = None
    algo_name = ""
    
    while True:
        clear_screen()
        print_menu()
        if graph:
            print(f"Загружено: {len(graph.lessons)} занятий, {len(graph.groups)} групп, {len(graph.teachers)} преподавателей")
        choice = input("Выберите пункт: ")
        
        if choice == '1':
            path = input("Укажите полный путь к JSON: ")
            graph = Graph.load_from_json(path)
            if graph:
                colors = None
                print("Загружено успешно")
            else:
                print("Ошибка загрузки")
            input("Enter...")
            
        elif choice in ['2', '3', '4']:
            if not graph:
                print("Сначала загрузите данные")
                input("Enter...")
                continue
            solvers = {
                '2': ("Branch and Bound", BranchBoundSolver),
                '3': ("Independent Sets", IndependentSetSolver),
                '4': ("Brown Algorithm", BrownAlgorithm)
            }
            algo_name, Solver = solvers[choice]
            solver = Solver(graph)
            start = time.time()
            colors, num = solver.solve()
            elapsed = time.time() - start
            print(f"\n{algo_name}: {num} цветов за {elapsed:.3f} сек")
            stats = solver.get_statistics()
            for k, v in stats.items():
                print(f"{k}: {v}")
            show_schedule(graph, colors, algo_name)
            input("Enter...")
            
        elif choice == '5':
            if not graph:
                print("Сначала загрузите данные")
                input("Enter...")
                continue
            results = {}
            for name, Solver in [("BranchBound", BranchBoundSolver), 
                                ("Independent", IndependentSetSolver),
                                ("Brown", BrownAlgorithm)]:
                solver = Solver(graph)
                start = time.time()
                c, n = solver.solve()
                elapsed = time.time() - start
                results[name] = (n, elapsed)
                print(f"{name}: {n} цветов, {elapsed:.3f} сек")
            input("Enter...")
            
        elif choice == '6':
            if not graph or not colors:
                print("Нет данных для сохранения")
                input("Enter...")
                continue
            path = input("Имя файла: ")
            graph.save_coloring(path, colors)
            input("Enter...")
            
        elif choice == '7':
            if graph and colors:
                show_schedule(graph, colors, algo_name)
            else:
                print("Нет расписания")
            input("Enter...")
            
        elif choice == '0':
            sys.exit(0)

if __name__ == "__main__":
    main()