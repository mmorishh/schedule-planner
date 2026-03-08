#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Генератор тестовых данных для BDD-тестирования планировщика расписания.
Создает JSON файлы различных размеров и характеристик для нагрузочного тестирования.
"""

import json
import os
import random
import time
from typing import Dict, List, Any

class TestDataGenerator:
    """Генератор тестовых данных с различными характеристиками"""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        
    def generate_group(self, id: str, name: str, students: int = None) -> Dict:
        """Генерация одной группы"""
        if students is None:
            students = random.randint(15, 30)
        return {
            "id": id,
            "name": name,
            "students": students
        }
    
    def generate_teacher(self, id: str, name: str = None, department: str = None) -> Dict:
        """Генерация одного преподавателя"""
        if name is None:
            first_names = ["Иван", "Петр", "Сергей", "Анна", "Елена", "Дмитрий", "Ольга"]
            last_names = ["Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов", "Попов"]
            name = f"{random.choice(last_names)} {random.choice(first_names)[0]}."
        
        if department is None:
            departments = ["Математика", "Физика", "Информатика", "Химия", "Биология", "История"]
            department = random.choice(departments)
            
        return {
            "id": id,
            "name": name,
            "department": department
        }
    
    def generate_classroom(self, id: str, name: str = None, capacity: int = None, room_type: str = None) -> Dict:
        """Генерация одной аудитории"""
        if name is None:
            name = str(random.randint(100, 500))
        
        if capacity is None:
            capacity = random.choice([20, 30, 40, 50, 100])
        
        if room_type is None:
            room_type = random.choice(["lecture", "lab", "seminar"])
            
        return {
            "id": id,
            "name": name,
            "capacity": capacity,
            "room_type": room_type
        }
    
    def generate_subject(self, id: str, name: str = None, hours: int = None) -> Dict:
        """Генерация одного предмета"""
        subjects_names = [
            "Математика", "Физика", "Информатика", "Химия", "Биология",
            "История", "Литература", "Английский язык", "Физкультура",
            "Философия", "Экономика", "Психология"
        ]
        
        if name is None:
            name = random.choice(subjects_names)
        
        if hours is None:
            hours = random.choice([36, 48, 72, 108])
            
        return {
            "id": id,
            "name": name,
            "hours": hours
        }
    
    def generate_lesson(self, id: str, groups: List[str], teachers: List[str], 
                       classrooms: List[str], subjects: List[str], 
                       hours_per_week: int = None) -> Dict:
        """Генерация одного занятия"""
        if hours_per_week is None:
            hours_per_week = random.choice([1, 2])
            
        return {
            "id": id,
            "subject": random.choice(subjects),
            "type": random.choice(["lecture", "lab", "seminar"]),
            "groups": [random.choice(groups)],
            "teacher": random.choice(teachers),
            "classroom": random.choice(classrooms),
            "hours_per_week": hours_per_week
        }
    
    def generate_correct_data(self) -> Dict:
        """Генерация корректных данных для базовых тестов"""
        return {
            "groups": [
                self.generate_group("g1", "101", 25),
                self.generate_group("g2", "102", 30)
            ],
            "teachers": [
                self.generate_teacher("t1", "Иванов И.И.", "Математика"),
                self.generate_teacher("t2", "Петров П.П.", "Физика")
            ],
            "classrooms": [
                self.generate_classroom("c1", "301", 30, "lecture"),
                self.generate_classroom("c2", "302", 20, "lab")
            ],
            "subjects": [
                self.generate_subject("s1", "Математика", 72),
                self.generate_subject("s2", "Физика", 64)
            ],
            "lessons": [
                self.generate_lesson("l1", ["g1"], ["t1"], ["c1"], ["s1"], 2),
                self.generate_lesson("l2", ["g2"], ["t2"], ["c2"], ["s2"], 1)
            ]
        }
    
    def generate_medium_data(self) -> Dict:
        """Генерация данных среднего размера для тестов качества"""
        groups = [self.generate_group(f"g{i}", f"Группа-{100+i}", 20 + i) for i in range(5)]
        teachers = [self.generate_teacher(f"t{i}") for i in range(5)]
        classrooms = [self.generate_classroom(f"c{i}") for i in range(4)]
        subjects = [self.generate_subject(f"s{i}") for i in range(4)]
        
        lessons = []
        for i in range(8):
            lesson = self.generate_lesson(
                f"l{i}",
                [random.choice([g["id"] for g in groups])],
                [random.choice([t["id"] for t in teachers])],
                [random.choice([c["id"] for c in classrooms])],
                [random.choice([s["id"] for s in subjects])],
                1 + i % 2
            )
            lessons.append(lesson)
        
        return {
            "groups": groups,
            "teachers": teachers,
            "classrooms": classrooms,
            "subjects": subjects,
            "lessons": lessons
        }
    
    def generate_large_data(self) -> Dict:
        """Генерация больших данных для нагрузочного тестирования"""
        groups = [self.generate_group(f"g{i}", f"Группа-{100+i}") for i in range(20)]
        teachers = [self.generate_teacher(f"t{i}") for i in range(30)]
        classrooms = [self.generate_classroom(f"c{i}") for i in range(15)]
        subjects = [self.generate_subject(f"s{i}") for i in range(10)]
        
        lessons = []
        for i in range(50):
            lesson = self.generate_lesson(
                f"l{i}",
                [random.choice([g["id"] for g in groups])],
                [random.choice([t["id"] for t in teachers])],
                [random.choice([c["id"] for c in classrooms])],
                [random.choice([s["id"] for s in subjects])]
            )
            lessons.append(lesson)
        
        return {
            "groups": groups,
            "teachers": teachers,
            "classrooms": classrooms,
            "subjects": subjects,
            "lessons": lessons
        }
    
    def generate_sparse_graph_data(self) -> Dict:
        """Генерация данных с разреженным графом конфликтов"""
        groups = [self.generate_group(f"g{i}", f"Группа-{100+i}") for i in range(10)]
        teachers = [self.generate_teacher(f"t{i}") for i in range(20)]
        classrooms = [self.generate_classroom(f"c{i}") for i in range(15)]
        subjects = [self.generate_subject(f"s{i}") for i in range(8)]
        
        # Создаем занятия так, чтобы было мало конфликтов
        lessons = []
        for i in range(30):
            # Каждое занятие использует уникальные комбинации
            group_id = groups[i % 10]["id"]
            teacher_id = teachers[i % 20]["id"]
            classroom_id = classrooms[i % 15]["id"]
            
            lessons.append({
                "id": f"l{i}",
                "subject": subjects[i % 8]["id"],
                "type": "lecture",
                "groups": [group_id],
                "teacher": teacher_id,
                "classroom": classroom_id,
                "hours_per_week": 1
            })
        
        return {
            "groups": groups,
            "teachers": teachers,
            "classrooms": classrooms,
            "subjects": subjects,
            "lessons": lessons
        }
    
    def generate_dense_graph_data(self) -> Dict:
        """Генерация данных с плотным графом конфликтов"""
        groups = [self.generate_group(f"g{i}", f"Группа-{100+i}") for i in range(5)]
        teachers = [self.generate_teacher(f"t{i}") for i in range(5)]
        classrooms = [self.generate_classroom(f"c{i}") for i in range(3)]
        subjects = [self.generate_subject(f"s{i}") for i in range(4)]
        
        # Создаем занятия так, чтобы было много конфликтов
        lessons = []
        for i in range(20):
            # Все занятия используют одни и те же ресурсы
            group_id = groups[i % 3]["id"]
            teacher_id = teachers[i % 2]["id"]
            classroom_id = classrooms[i % 2]["id"]
            
            lessons.append({
                "id": f"l{i}",
                "subject": subjects[i % 4]["id"],
                "type": "lecture",
                "groups": [group_id],
                "teacher": teacher_id,
                "classroom": classroom_id,
                "hours_per_week": 2
            })
        
        return {
            "groups": groups,
            "teachers": teachers,
            "classrooms": classrooms,
            "subjects": subjects,
            "lessons": lessons
        }
    
    def generate_invalid_json(self) -> str:
        """Генерация некорректного JSON"""
        return '{"groups": [{"id": "g1", "name": "101", "students": 25]}}'  # Не хватает закрывающей скобки
    
    def generate_missing_fields_data(self) -> Dict:
        """Генерация данных с пропущенными полями"""
        return {
            "groups": [{"id": "g1", "name": "101", "students": 25}],
            "teachers": [{"id": "t1", "name": "Иванов И.И."}],  # пропущен department
            "classrooms": [{"id": "c1", "name": "301", "capacity": 30}],  # пропущен room_type
            "subjects": [{"id": "s1", "name": "Математика", "hours": 72}],
            "lessons": [
                {
                    "id": "l1",
                    "subject": "s1",
                    "type": "lecture",
                    # пропущены groups
                    "teacher": "t1",
                    "classroom": "c1",
                    "hours_per_week": 2
                }
            ]
        }
    
    def save_data(self, data: Dict, filename: str):
        """Сохранение данных в JSON файл"""
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  ✅ {filename} - {self._count_lessons(data)} занятий")
    
    def save_text(self, content: str, filename: str):
        """Сохранение текстовых данных"""
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ {filename}")
    
    def _count_lessons(self, data: Dict) -> int:
        """Подсчет количества занятий с учетом размножения"""
        lessons = data.get('lessons', [])
        total = 0
        for lesson in lessons:
            total += lesson.get('hours_per_week', 1)
        return total
    
    def generate_all(self):
        """Генерация всех тестовых данных"""
        print("\n" + "="*60)
        print("ГЕНЕРАТОР ТЕСТОВЫХ ДАННЫХ ДЛЯ BDD-ТЕСТИРОВАНИЯ")
        print("="*60)
        
        print(f"\n📁 Директория: {os.path.abspath(self.data_dir)}")
        print(f"🔄 Seed: {self.seed}")
        print("\n⏳ Генерация файлов...\n")
        
        # 1. Корректные данные для базовых тестов
        print("📄 Базовые тесты:")
        self.save_data(self.generate_correct_data(), "test.json")
        
        # 2. Данные среднего размера
        print("\n📊 Тесты качества:")
        self.save_data(self.generate_medium_data(), "medium_schedule.json")
        
        # 3. Большие данные для нагрузочного тестирования
        print("\n🔥 Нагрузочное тестирование:")
        self.save_data(self.generate_large_data(), "large_schedule.json")
        
        # 4. Данные с разреженным графом
        print("\n🕸️ Разреженный граф:")
        self.save_data(self.generate_sparse_graph_data(), "sparse_graph.json")
        
        # 5. Данные с плотным графом
        print("\n🌲 Плотный граф:")
        self.save_data(self.generate_dense_graph_data(), "dense_graph.json")
        
        # 6. Некорректный JSON
        print("\n⚠️  Ошибочные данные:")
        self.save_text(self.generate_invalid_json(), "invalid.json")
        
        # 7. Данные с пропущенными полями
        self.save_data(self.generate_missing_fields_data(), "missing_fields.json")
        
        # 8. Дополнительные данные для тестов конфликтов
        print("\n⚔️  Тесты конфликтов:")
        small_conflict = {
            "groups": [self.generate_group("g1", "101")],
            "teachers": [self.generate_teacher("t1", "Иванов И.И.")],
            "classrooms": [self.generate_classroom("c1", "301")],
            "subjects": [self.generate_subject("s1", "Математика")],
            "lessons": [
                self.generate_lesson("l1", ["g1"], ["t1"], ["c1"], ["s1"], 1),
                self.generate_lesson("l2", ["g1"], ["t1"], ["c1"], ["s1"], 1)
            ]
        }
        self.save_data(small_conflict, "conflict_test.json")
        
        print("\n" + "="*60)
        print("✅ ГЕНЕРАЦИЯ ЗАВЕРШЕНА")
        print("="*60)
        
        # Вывод статистики
        print("\n📊 СТАТИСТИКА:")
        stats = {
            "test.json": "Базовые тесты",
            "medium_schedule.json": "Тесты качества",
            "large_schedule.json": "Нагрузочное тестирование",
            "sparse_graph.json": "Разреженный граф",
            "dense_graph.json": "Плотный граф",
            "invalid.json": "Некорректный JSON",
            "missing_fields.json": "Пропущенные поля",
            "conflict_test.json": "Тесты конфликтов"
        }
        
        for filename, description in stats.items():
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"  • {filename:25} - {description:25} - {size:6d} байт")
        
        print("\n📌 Всего файлов: 8")
        print("📌 Общий размер: {} байт".format(
            sum(os.path.getsize(os.path.join(self.data_dir, f)) 
                for f in os.listdir(self.data_dir) 
                if os.path.isfile(os.path.join(self.data_dir, f)))
        ))

def generate_datasets_for_performance():
    """Генерация датасетов для нагрузочного тестирования"""
    generator = TestDataGenerator()
    
    print("\n📈 ГЕНЕРАЦИЯ ДАННЫХ ДЛЯ НАГРУЗОЧНОГО ТЕСТИРОВАНИЯ")
    print("-" * 50)
    
    # Генерируем датасеты разных размеров
    sizes = [10, 20, 30, 40, 50]
    densities = [0.2, 0.5, 0.8]
    
    for size in sizes:
        for density in densities:
            # Создаем граф с заданными параметрами
            import random
            random.seed(size * 100 + int(density * 10))
            
            groups = [generator.generate_group(f"g{i}", f"Группа-{i}") for i in range(size // 5 + 1)]
            teachers = [generator.generate_teacher(f"t{i}") for i in range(size // 3 + 1)]
            classrooms = [generator.generate_classroom(f"c{i}") for i in range(size // 4 + 1)]
            subjects = [generator.generate_subject(f"s{i}") for i in range(size // 5 + 1)]
            
            lessons = []
            for i in range(size):
                # Создаем занятия с учетом плотности конфликтов
                if random.random() < density:
                    # Конфликтующее занятие (общие ресурсы)
                    group_id = groups[i % len(groups)]["id"]
                    teacher_id = teachers[i % len(teachers)]["id"]
                    classroom_id = classrooms[i % len(classrooms)]["id"]
                else:
                    # Неконфликтующее занятие (уникальные ресурсы)
                    group_id = groups[i % len(groups)]["id"]
                    teacher_id = teachers[(i + size) % len(teachers)]["id"]
                    classroom_id = classrooms[(i + size*2) % len(classrooms)]["id"]
                
                lessons.append({
                    "id": f"l_{size}_{i}",
                    "subject": subjects[i % len(subjects)]["id"],
                    "type": "lecture",
                    "groups": [group_id],
                    "teacher": teacher_id,
                    "classroom": classroom_id,
                    "hours_per_week": 1
                })
            
            data = {
                "groups": groups,
                "teachers": teachers,
                "classrooms": classrooms,
                "subjects": subjects,
                "lessons": lessons
            }
            
            filename = f"perf_size{size}_density{density:.1f}.json"
            generator.save_data(data, filename)
    
    print("\n✅ Генерация данных для нагрузочного тестирования завершена")

def main():
    """Основная функция"""
    print("\n" + "🚀" * 30)
    print("🚀  ЗАПУСК ГЕНЕРАТОРА ТЕСТОВЫХ ДАННЫХ  🚀")
    print("🚀" * 30)
    
    start_time = time.time()
    
    # Создаем директорию data
    os.makedirs("data", exist_ok=True)
    
    # Генерируем основные данные
    generator = TestDataGenerator()
    generator.generate_all()
    
    # Генерируем данные для нагрузочного тестирования
    generate_datasets_for_performance()
    
    elapsed = time.time() - start_time
    
    print("\n" + "✨" * 30)
    print(f"✨  ГЕНЕРАЦИЯ ЗАВЕРШЕНА ЗА {elapsed:.2f} СЕКУНД  ✨")
    print("✨" * 30)
    
    print("\n📂 Содержимое директории data/:")
    for filename in sorted(os.listdir("data")):
        filepath = os.path.join("data", filename)
        size = os.path.getsize(filepath)
        mod_time = time.ctime(os.path.getmtime(filepath))
        print(f"  • {filename:35} - {size:6d} байт - {mod_time}")

if __name__ == "__main__":
    main()