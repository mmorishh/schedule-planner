import json

class Group:
    def __init__(self, id, name, students=0):
        self.id = id
        self.name = name
        self.students = students

    def __repr__(self):
        return self.name
    

class Teacher:
    def __init__(self, id, name, department=""):
        self.id = id
        self.name = name
        self.department = department

    def __repr__(self):
        return self.name


class Classroom:
    def __init__(self, id, name, capacity=0, room_type="lecture"):
        self.id = id
        self.name = name
        self.capacity = capacity
        self.room_type = room_type

    def __repr__(self):
        return self.name
    

class Subject:
    def __init__(self, id, name, hours=0):
        self.id = id
        self.name = name
        self.hours = hours
    
    def __repr__(self):
        return self.name
    

class Lesson:
    def __init__(self, id, subject, type, groups, teacher, classroom, hours_per_week, instance=0):
        self.id = id
        self.subject = subject
        self.type = type
        self.groups = groups if isinstance(groups, list) else [groups]
        self.teacher = teacher
        self.classroom = classroom
        self.hours_per_week = hours_per_week
        self.instance = instance
        self.color = -1

    def conflicts_with(self, other):
        if self.id == other.id and self.instance == other.instance:
            return False
        
        for my_group in self.groups:
            for other_group in other.groups:
                if my_group == other_group:
                    return True
                
        if self.teacher == other.teacher:
            return True
        
        if self.classroom == other.classroom:
            return True
        
        return False
    
    def __repr__(self):
        groups_str = ",".join(self.groups)
        return f"{self.subject} [{self.type}] гр:{groups_str} {self.teacher}/{self.classroom} #{self.instance}"
    
    def expand_lessons(lessons_data):
        expanded = []
        for lesson in lessons_data:
            hours = lesson.get('hours_per_week', 1)
            for i in range(hours):
                new_lesson = Lesson(
                    id=f"{lesson['id']}_{i}",
                    subject=lesson['subject'],
                    type=lesson.get('type', 'lecture'),
                    groups=lesson['groups'],
                    teacher=lesson['teacher'],
                    classroom=lesson['classroom'],
                    hours_per_week=hours,
                    instance=i
                )
                expanded.append(new_lesson)
        return expanded

def expand_lessons(lessons_data):
    """Размножение занятий по часам"""
    expanded = []
    for lesson in lessons_data:
        hours = lesson.get('hours_per_week', 1)
        for i in range(hours):
            new_lesson = Lesson(
                id=f"{lesson['id']}_{i}",
                subject=lesson['subject'],
                type=lesson.get('type', 'lecture'),
                groups=lesson['groups'],
                teacher=lesson['teacher'],
                classroom=lesson['classroom'],
                hours_per_week=hours,
                instance=i
            )
            expanded.append(new_lesson)
    return expanded


class Graph:
    def __init__(self, lessons, groups=None, teachers=None, classrooms=None, subjects=None):
        self.lessons = lessons
        self.groups = groups or {}
        self.teachers = teachers or {}
        self.classrooms = classrooms or {}
        self.subjects = subjects or {}
        self.n = len(lessons)
        self.adj = self._build_adj()
        self._neighbors_cache = {}

    def _build_adj(self):
        adj = [[False]*self.n for _ in range(self.n)]
        for i in range(self.n):
            for j in range(i+1, self.n):
                if self.lessons[i].conflicts_with(self.lessons[j]):
                    adj[i][j] = adj[j][i] = True
        return adj

    def neighbors(self, v):
        if v in self._neighbors_cache:
            return self._neighbors_cache[v]
        res = [i for i in range(self.n) if self.adj[v][i]]
        self._neighbors_cache[v] = res
        return res

    def degree(self, v):
        return len(self.neighbors(v))

    def is_safe(self, v, c, colors):
        for u in self.neighbors(v):
            if colors[u] == c:
                return False
        return True

    @staticmethod
    def load_from_json(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            groups = {}
            for g in data.get('groups', []):
                groups[g['id']] = Group(**g)
            
            teachers = {}
            for t in data.get('teachers', []):
                teachers[t['id']] = Teacher(**t)
            
            classrooms = {}
            for c in data.get('classrooms', []):
                classrooms[c['id']] = Classroom(**c)
            
            subjects = {}
            for s in data.get('subjects', []):
                subjects[s['id']] = Subject(**s)
            
            lessons_data = data.get('lessons', [])
            expanded = expand_lessons(lessons_data)
            
            if not expanded:
                print("Нет занятий")
                return None
            
            return Graph(expanded, groups, teachers, classrooms, subjects)
            
        except FileNotFoundError:
            print(f"Файл не найден: {path}")
            return None
        except json.JSONDecodeError:
            print(f"Ошибка формата JSON")
            return None
        except Exception as e:
            print(f"Ошибка: {e}")
            return None

    def save_coloring(self, path, colors):
        try:
            data = {
                "num_colors": max(colors)+1,
                "schedule": []
            }
            for i, lesson in enumerate(self.lessons):
                slot_data = {
                    "lesson_id": lesson.id,
                    "subject": self.subjects.get(lesson.subject, lesson.subject).name if lesson.subject in self.subjects else lesson.subject,
                    "type": lesson.type,
                    "groups": [self.groups.get(g, g).name if g in self.groups else g for g in lesson.groups],
                    "teacher": self.teachers.get(lesson.teacher, lesson.teacher).name if lesson.teacher in self.teachers else lesson.teacher,
                    "classroom": self.classrooms.get(lesson.classroom, lesson.classroom).name if lesson.classroom in self.classrooms else lesson.classroom,
                    "time_slot": colors[i]
                }
                data["schedule"].append(slot_data)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False