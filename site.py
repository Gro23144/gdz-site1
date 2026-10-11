# site.py
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote, unquote
from email.parser import BytesParser
from email.policy import default as email_policy
import json
import random
import os
import uuid
from datetime import datetime

# ============================================================
#  PHOTOS_DIR, DATA_FILE
# ============================================================
PHOTOS_DIR = "photos"
DATA_FILE = "photos_data.json"
os.makedirs(PHOTOS_DIR, exist_ok=True)

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 МБ

# ============================================================
#  homework_db — база заданий
# ============================================================
homework_db = {
    "Математика": {
        5: {
            "1.1": {"task": "Сложите 2 + 2", "answer": "4", "solution": "2 + 2 = 4"},
            "1.2": {"task": "Вычислите 5 × 6", "answer": "30", "solution": "5 × 6 = 30"},
            "1.3": {"task": "Найдите периметр квадрата со стороной 4 см", "answer": "16 см",
                    "solution": "P = 4 × a = 4 × 4 = 16 см"},
            "2.1": {"task": "Сократите дробь 8/12", "answer": "2/3",
                    "solution": "НОД(8,12) = 4 → 8÷4 / 12÷4 = 2/3"},
        },
        6: {
            "1.1": {"task": "Решите уравнение x + 3 = 7", "answer": "x = 4",
                    "solution": "x = 7 − 3 = 4"},
            "1.2": {"task": "Найдите 25% от числа 80", "answer": "20",
                    "solution": "80 × 25 ÷ 100 = 20"},
            "2.1": {"task": "Вычислите (−5) + (−3)", "answer": "−8",
                    "solution": "−5 − 3 = −8"},
        },
        7: {
            "1.1": {"task": "Решите уравнение 2x − 5 = 9", "answer": "x = 7",
                    "solution": "2x = 9 + 5 = 14 → x = 7"},
            "1.2": {"task": "Упростите: 3a + 5a − 2a", "answer": "6a",
                    "solution": "3a + 5a − 2a = 6a"},
        },
        8: {
            "1.1": {"task": "Решите квадратное уравнение x² − 5x + 6 = 0",
                    "answer": "x₁ = 2, x₂ = 3",
                    "solution": "D = 25 − 24 = 1 → x = (5 ± 1) / 2"},
        },
    },
    "Русский язык": {
        1: {
            "Стр.41": {"task": "Выдели голосом слово 'мой': 'Это мой дом'",
                       "answer": "Это │ мо́й │ дом!",
                       "solution": "Слово выделяется громче остальных"},
        },
        3: {
            "Упр.24": {"task": "Вставь буквы: Лоша_ь, М_сква, б_рё_ка",
                       "answer": "Лошадь, Москва, берёзка",
                       "solution": "Лошадь (3 скл.), Москва (словарное), берёзка (берёза)"},
        },
        5: {
            "Упр.12": {"task": "Разберите слово 'пришкольный' по составу",
                       "answer": "при-школь-н-ый",
                       "solution": "Приставка: при-, корень: -школь-, суффикс: -н-, окончание: -ый"},
            "Упр.17": {"task": "Отредактируй: 'На крыльцо вышла девочка с собакой в платке'",
                       "answer": "На крыльцо вышла девочка в платке и с собакой",
                       "solution": "Нарушен порядок слов — непонятно, кто в платке"},
            "Упр.25": {"task": "Вставьте пропущенную букву: в_сна", "answer": "весна",
                       "solution": "Проверочное слово — вёсны"},
            "Упр.30": {"task": "Определите род слова 'пальто'", "answer": "средний род",
                       "solution": "Слово 'пальто' — несклоняемое существительное среднего рода"},
        },
        6: {
            "Упр.45": {"task": "Найдите причастие: 'Летящий самолёт скрылся за облаками'",
                       "answer": "летящий",
                       "solution": "Летящий — причастие, отвечает на вопрос 'какой?'"},
            "Упр.60": {"task": "Поставьте ударение в слове 'звонит'", "answer": "звонИт",
                       "solution": "Ударение на второй слог: звонИт"},
        },
        7: {
            "Упр.88": {"task": "Определите вид причастия: 'прочитанная книга'",
                       "answer": "страдательное, совершенный вид, прошедшее время",
                       "solution": "Книга прочитана кем-то → страдательное"},
        },
        9: {
            "Номер 411": {"task": "Расставьте знаки: 'Он сказал что придёт поздно'",
                          "answer": "Он сказал, что придёт поздно.",
                          "solution": "СПП с придаточным изъяснительным → запятая перед 'что'"},
        },
        11: {
            "Упр.200": {"task": "Определите стиль текста: 'Уважаемые граждане!..'",
                        "answer": "официально-деловой",
                        "solution": "Обращение 'граждане', формальность → офиц.-деловой стиль"},
        },
    },
    "Физика": {
        7: {
            "3.1": {"task": "Найдите скорость, если S = 100 м, t = 20 с", "answer": "5 м/с",
                    "solution": "v = S / t = 100 / 20 = 5 м/с"},
            "3.2": {"task": "Найдите плотность тела массой 300 г и объёмом 100 см³",
                    "answer": "3 г/см³",
                    "solution": "ρ = m / V = 300 / 100 = 3 г/см³"},
        },
        8: {
            "5.1": {"task": "Найдите силу тяжести для тела массой 5 кг (g = 10 м/с²)",
                    "answer": "50 Н",
                    "solution": "F = m × g = 5 × 10 = 50 Н"},
        },
    },
    "Химия": {
        8: {
            "1.1": {"task": "Найдите молярную массу воды H₂O",
                    "answer": "18 г/моль",
                    "solution": "M(H₂O) = 2×1 + 16 = 18 г/моль"},
            "1.2": {"task": "Сколько атомов в молекуле CO₂?",
                    "answer": "3 атома",
                    "solution": "1 атом C + 2 атома O = 3 атома"},
        },
    },
    "Английский язык": {
        5: {
            "Unit 1": {"task": "Переведите: 'I have a cat'", "answer": "У меня есть кошка",
                       "solution": "I — я, have — имею, a cat — кошку"},
            "Unit 2": {"task": "Поставьте в Past Simple: 'go'", "answer": "went",
                       "solution": "go → went (неправильный глагол)"},
        },
        6: {
            "Unit 5": {"task": "Образуйте множественное число: 'child'",
                       "answer": "children",
                       "solution": "child → children (исключение)"},
        },
    },
    "Информатика": {
        7: {
            "1.1": {"task": "Переведите число 5 (десятичное) в двоичную",
                    "answer": "101",
                    "solution": "5 = 4 + 1 = 2² + 2⁰ = 101₂"},
            "1.2": {"task": "Сколько бит в одном байте?", "answer": "8 бит",
                    "solution": "1 байт = 8 бит"},
        },
    },
}

# ============================================================
#  SITE_NAME, SITE_EMOJI
# ============================================================
SITE_NAME = "Решебник"
SITE_EMOJI = "📘"

# ============================================================
#  Функции фото
# ============================================================
def load_photos():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

def save_photos(photos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(photos, f, ensure_ascii=False, indent=2)

def add_photo(filename, title, subject, class_num, task_number, description, solution):
    photos = load_photos()
    photo = {
        "id": str(uuid.uuid4())[:8],
        "filename": filename,
        "title": title or "Без названия",
        "subject": subject or "",
        "class_num": class_num or 0,
        "task_number": task_number or "",
        "description": description or "",
        "solution": solution or "",
        "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
    }
    photos.append(photo)
    save_photos(photos)
    return photo

def get_photo(photo_id):
    for p in load_photos():
        if p["id"] == photo_id:
            return p
    return None

def delete_photo(photo_id):
    photos = load_photos()
    photo = next((p for p in photos if p["id"] == photo_id), None)
    if not photo:
        return False
    filepath = os.path.join(PHOTOS_DIR, photo["filename"])
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except OSError:
            pass
    photos = [p for p in photos if p["id"] != photo_id]
    save_photos(photos)
    return True

def update_photo_solution(photo_id, solution):
    photos = load_photos()
    for p in photos:
        if p["id"] == photo_id:
            p["solution"] = solution
            save_photos(photos)
            return True
    return False

# ============================================================
#  Вспомогательные утилиты
# ============================================================
def count_all():
    return sum(len(t) for c in homework_db.values() for t in c.values())

def count_by_subject(subject):
    return sum(len(t) for t in homework_db.get(subject, {}).values())

def all_tasks_flat():
    items = []
    for subject, classes in homework_db.items():
        for class_num, tasks in classes.items():
            for num, t in tasks.items():
                items.append({
                    "subject": subject, "class": class_num,
                    "num": num, "task": t["task"], "answer": t["answer"],
                    "solution": t["solution"]
                })
    return items

def random_task():
    items = all_tasks_flat()
    return random.choice(items) if items else None

def stats_by_class():
    result = {}
    for subject, classes in homework_db.items():
        for class_num, tasks in classes.items():
            result[class_num] = result.get(class_num, 0) + len(tasks)
    return dict(sorted(result.items()))

def all_classes():
    classes = set()
    for subject, cls in homework_db.items():
        classes.update(cls.keys())
    return sorted(classes)

def find_photo_answer(title, description):
    """Ищет похожее задание в базе по названию и описанию."""
    text = f"{title} {description}".lower().strip()
    if not text:
        return None
    best_match = None
    best_score = 0
    for r in all_tasks_flat():
        score = 0
        num = r["num"].lower()
        if num and num in text:
            score += 10
        words = r["task"].lower().split()
        for w in words:
            if len(w) > 3 and w in text:
                score += 1
        if score > best_score:
            best_score = score
            best_match = r
    return best_match if best_score >= 3 else None
# ============================================================
#  STYLE — CSS сайта
# ============================================================
STYLE = """
<style>
* { margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI',Arial,sans-serif; }
body { background:#f4f6f9; color:#333; line-height:1.6; min-height:100vh; display:flex; flex-direction:column; }
header { background:linear-gradient(135deg,#2193b0,#6dd5ed); color:#fff; padding:18px 40px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:20px; box-shadow:0 2px 10px rgba(0,0,0,.1); }
.logo { color:#fff; text-decoration:none; font-size:22px; font-weight:bold; white-space:nowrap; }
.search-form { flex:1; display:flex; max-width:420px; }
.search-form input { flex:1; padding:10px 15px; border:none; border-radius:8px 0 0 8px; font-size:15px; }
.search-form button { padding:10px 18px; border:none; background:#2d3142; color:#fff; border-radius:0 8px 8px 0; cursor:pointer; font-size:15px; }
.search-form button:hover { background:#1a1d2e; }
nav a { color:#fff; text-decoration:none; margin-left:15px; font-weight:500; }
nav a:hover { opacity:.8; }
main { flex:1; max-width:1100px; margin:0 auto; padding:40px 20px; width:100%; }
h1 { color:#2d3142; margin-bottom:20px; font-size:32px; }
h2 { color:#2d3142; margin-bottom:15px; }
.hero { text-align:center; padding:40px 20px; background:#fff; border-radius:16px; margin-bottom:30px; box-shadow:0 4px 15px rgba(0,0,0,.05); }
.hero h1 { font-size:38px; margin-bottom:10px; }
.hero p { color:#666; }
.hero-stats { display:flex; justify-content:center; gap:30px; margin-top:25px; flex-wrap:wrap; }
.stat { text-align:center; }
.stat .num { font-size:32px; font-weight:bold; color:#2193b0; display:block; }
.stat .lbl { font-size:13px; color:#888; text-transform:uppercase; }
.quick-actions { display:flex; gap:12px; justify-content:center; margin-top:25px; flex-wrap:wrap; }
.grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:20px; }
.card { background:#fff; padding:22px; border-radius:12px; box-shadow:0 4px 15px rgba(0,0,0,.05); transition:.3s; text-decoration:none; color:inherit; display:block; }
.card:hover { transform:translateY(-4px); box-shadow:0 8px 25px rgba(33,147,176,.25); }
.card h3 { color:#2193b0; margin-bottom:8px; }
.card p { color:#666; font-size:15px; }
.card .count-badge { display:inline-block; background:#e6f6fb; color:#2193b0; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:600; margin-left:8px; }
.badge { display:inline-block; background:#e6f6fb; color:#2193b0; padding:4px 12px; border-radius:20px; font-size:13px; font-weight:600; margin-bottom:8px; }
.answer-box { background:#d4edda; border-left:5px solid #27ae60; padding:20px; border-radius:12px; margin:20px 0; }
.answer-box b { color:#155724; display:block; font-size:14px; margin-bottom:5px; }
.answer-box .value { font-size:26px; font-weight:bold; color:#155724; white-space:pre-wrap; }
.solution-box { background:#fff; padding:20px; border-radius:12px; margin:20px 0; box-shadow:0 4px 15px rgba(0,0,0,.05); }
.solution-box b { color:#2193b0; display:block; margin-bottom:10px; }
.btn { display:inline-block; padding:12px 24px; background:#2193b0; color:#fff; text-decoration:none; border-radius:8px; font-weight:600; transition:.3s; border:none; cursor:pointer; font-size:15px; }
.btn:hover { background:#1a7a94; transform:translateY(-2px); }
.btn-outline { background:#fff; color:#2193b0; border:2px solid #2193b0; }
.btn-outline:hover { background:#2193b0; color:#fff; }
.btn-purple { background:#764ba2; }
.btn-purple:hover { background:#5f3a85; }
.btn-danger { background:#e74c3c; }
.btn-danger:hover { background:#c0392b; }
.btn-sm { padding:6px 14px; font-size:13px; }
.breadcrumbs { color:#888; margin-bottom:20px; font-size:14px; }
.breadcrumbs a { color:#2193b0; text-decoration:none; }
.breadcrumbs a:hover { text-decoration:underline; }
.actions { display:flex; gap:10px; flex-wrap:wrap; margin-top:20px; }
footer { background:#2d3142; color:#fff; text-align:center; padding:25px; margin-top:40px; }
footer a { color:#6dd5ed; text-decoration:none; }
.photo-card { background:#fff; border-radius:12px; overflow:hidden; box-shadow:0 4px 15px rgba(0,0,0,.05); transition:.3s; text-decoration:none; color:inherit; display:block; }
.photo-card:hover { transform:translateY(-4px); box-shadow:0 8px 25px rgba(33,147,176,.25); }
.photo-card img { width:100%; height:200px; object-fit:cover; display:block; background:#f0f0f0; }
.photo-info { padding:15px; }
.photo-info h3 { color:#2193b0; font-size:16px; margin-bottom:5px; }
.photo-info p { color:#888; font-size:13px; margin-bottom:8px; }
.photo-full { max-width:100%; border-radius:12px; box-shadow:0 4px 15px rgba(0,0,0,.1); margin:20px 0; }
.has-solution { display:inline-block; background:#d4edda; color:#155724; padding:2px 10px; border-radius:10px; font-size:11px; font-weight:600; }
.no-solution { display:inline-block; background:#fff3cd; color:#856404; padding:2px 10px; border-radius:10px; font-size:11px; font-weight:600; }
.form-group { margin-bottom:15px; }
.form-group label { display:block; margin-bottom:5px; color:#555; font-weight:600; font-size:14px; }
.form-group input[type=text], .form-group input[type=number], .form-group textarea, .form-group select {
    width:100%; padding:10px 14px; border:2px solid #e1e5ec; border-radius:8px; font-size:15px; font-family:inherit;
}
.form-group input:focus, .form-group textarea:focus, .form-group select:focus { outline:none; border-color:#2193b0; }
.form-group input[type=file] {
    padding:10px; background:#f4f6f9; border:2px dashed #2193b0; border-radius:8px; width:100%; cursor:pointer;
}
.flash { padding:12px 20px; border-radius:8px; margin-bottom:15px; }
.flash.success { background:#d4edda; color:#155724; }
.flash.error { background:#f8d7da; color:#721c24; }
.flash.info { background:#d1ecf1; color:#0c5460; }
.auto-answer { background:#fff8e1; border-left:5px solid #ffc107; padding:20px; border-radius:12px; margin:20px 0; }
.auto-answer b { color:#856404; display:block; font-size:14px; margin-bottom:5px; }
@media (max-width:768px) {
    header { flex-direction:column; padding:15px; }
    .search-form { max-width:100%; width:100%; }
    nav { display:flex; gap:12px; flex-wrap:wrap; justify-content:center; }
    nav a { margin:0; }
    .hero h1 { font-size:26px; }
    h1 { font-size:24px; }
}
</style>
"""

# ============================================================
#  html_page — базовый шаблон
# ============================================================
def html_page(title, body, flash_msg=None, flash_type="success"):
    flash_html = ""
    if flash_msg:
        flash_html = f'<div class="flash {flash_type}">{flash_msg}</div>'
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | {SITE_NAME}</title>
{STYLE}
</head>
<body>
<header>
    <a href="/" class="logo">{SITE_EMOJI} {SITE_NAME}</a>
    <form class="search-form" action="/search" method="get">
        <input type="text" name="q" placeholder="Поиск задания..." required>
        <button type="submit">🔍</button>
    </form>
    <nav>
        <a href="/">Главная</a>
        <a href="/all">Все</a>
        <a href="/photos">📸 Фото</a>
        <a href="/random">🎲</a>
        <a href="/stats">📊</a>
    </nav>
</header>
<main>{flash_html}{body}</main>
<footer>© 2025 {SITE_NAME}. Сделано на чистом Python 🐍</footer>
</body>
</html>"""

# ============================================================
#  Все page_* функции — страницы
# ============================================================
def page_index():
    total = count_all()
    subjects_count = len(homework_db)
    classes_count = len(all_classes())
    photos_count = len(load_photos())

    cards = ""
    for subject, classes in homework_db.items():
        s_total = count_by_subject(subject)
        c_count = len(classes)
        cards += f"""
        <a class="card" href="/subject/{quote(subject)}">
            <h3>{subject} <span class="count-badge">{s_total}</span></h3>
            <p>{c_count} класс(ов)</p>
        </a>"""

    body = f"""
    <div class="hero">
        <h1>Готовые домашние задания</h1>
        <p>Выбери предмет и класс — получишь готовые решения</p>
        <div class="hero-stats">
            <div class="stat"><span class="num">{subjects_count}</span><span class="lbl">предметов</span></div>
            <div class="stat"><span class="num">{classes_count}</span><span class="lbl">классов</span></div>
            <div class="stat"><span class="num">{total}</span><span class="lbl">заданий</span></div>
            <div class="stat"><span class="num">{photos_count}</span><span class="lbl">фото</span></div>
        </div>
        <div class="quick-actions">
            <a class="btn btn-purple" href="/photos/add">📸 Загрузить фото задания</a>
            <a class="btn" href="/photos">🖼️ Галерея фото</a>
            <a class="btn btn-outline" href="/random">🎲 Случайное</a>
            <a class="btn btn-outline" href="/stats">📊 Статистика</a>
        </div>
    </div>
    <div class="grid">{cards}</div>
    """
    return html_page("Главная", body)


def page_subject(subject):
    if subject not in homework_db:
        return None
    classes = homework_db[subject]
    cards = ""
    for class_num in sorted(classes.keys()):
        tasks = classes[class_num]
        cards += f"""
        <a class="card" href="/subject/{quote(subject)}/class/{class_num}">
            <h3>{class_num} класс <span class="count-badge">{len(tasks)}</span></h3>
            <p>{len(tasks)} заданий</p>
        </a>"""
    body = f"""
    <div class="breadcrumbs"><a href="/">Главная</a> → {subject}</div>
    <h1>{subject} <span class="count-badge">{count_by_subject(subject)}</span></h1>
    <div class="grid">{cards}</div>
    <div class="actions"><a class="btn" href="/">← Назад к предметам</a></div>
    """
    return html_page(subject, body)


def page_class(subject, class_num):
    if subject not in homework_db or class_num not in homework_db[subject]:
        return None
    tasks = homework_db[subject][class_num]
    cards = ""
    for num in sorted(tasks.keys()):
        t = tasks[num]
        cards += f"""
        <a class="card" href="/task/{quote(subject)}/{class_num}/{quote(num)}">
            <span class="badge">№ {num}</span>
            <p>{t['task']}</p>
        </a>"""
    body = f"""
    <div class="breadcrumbs">
        <a href="/">Главная</a> →
        <a href="/subject/{quote(subject)}">{subject}</a> →
        {class_num} класс
    </div>
    <h1>{subject} — {class_num} класс <span class="count-badge">{len(tasks)}</span></h1>
    <div class="grid">{cards}</div>
    <div class="actions">
        <a class="btn" href="/subject/{quote(subject)}">← К классам</a>
        <a class="btn btn-outline" href="/">🏠 На главную</a>
    </div>
    """
    return html_page(f"{subject} {class_num}", body)


def page_task(subject, class_num, task_num):
    try:
        t = homework_db[subject][class_num][task_num]
    except KeyError:
        return None
    body = f"""
    <div class="breadcrumbs">
        <a href="/">Главная</a> →
        <a href="/subject/{quote(subject)}">{subject}</a> →
        <a href="/subject/{quote(subject)}/class/{class_num}">{class_num} класс</a> →
        №{task_num}
    </div>
    <h1>Задание №{task_num}</h1>
    <div class="card"><b>📝 Условие:</b><p style="margin-top:8px;">{t['task']}</p></div>
    <div class="answer-box">
        <b>✅ Ответ</b>
        <div class="value">{t['answer']}</div>
    </div>
    <div class="solution-box">
        <b>📖 Решение</b>
        <p>{t['solution']}</p>
    </div>
    <div class="actions">
        <a class="btn" href="/subject/{quote(subject)}/class/{class_num}">← К заданиям</a>
        <a class="btn btn-purple" href="/random">🎲 Случайное</a>
        <a class="btn btn-outline" href="/">🏠 На главную</a>
    </div>
    """
    return html_page(f"№{task_num}", body)


def page_all():
    items = all_tasks_flat()
    cards = ""
    for r in items:
        cards += f"""
        <a class="card" href="/task/{quote(r['subject'])}/{r['class']}/{quote(r['num'])}">
            <span class="badge">{r['subject']} • {r['class']} класс • №{r['num']}</span>
            <p>{r['task']}</p>
        </a>"""
    body = f"""
    <div class="hero"><h1>📚 Все задания</h1><p>Всего: {len(items)} заданий</p></div>
    <div class="grid">{cards}</div>
    <div class="actions"><a class="btn" href="/">← На главную</a></div>
    """
    return html_page("Все задания", body)


def page_random():
    r = random_task()
    if not r:
        return page_404()
    url = f"/task/{quote(r['subject'])}/{r['class']}/{quote(r['num'])}"
    body = f"""
    <div class="hero"><h1>🎲 Случайное задание</h1></div>
    <div class="card">
        <span class="badge">{r['subject']} • {r['class']} класс • №{r['num']}</span>
        <p style="margin-top:10px; font-size:17px;">{r['task']}</p>
    </div>
    <div class="answer-box"><b>✅ Ответ</b><div class="value">{r['answer']}</div></div>
    <div class="solution-box"><b>📖 Решение</b><p>{r['solution']}</p></div>
    <div class="actions">
        <a class="btn btn-purple" href="/random">🎲 Ещё раз</a>
        <a class="btn" href="{url}">📄 Открыть полностью</a>
        <a class="btn btn-outline" href="/">🏠 На главную</a>
    </div>
    """
    return html_page("Случайное", body)


def page_stats():
    total = count_all()
    by_class = stats_by_class()
    photos_count = len(load_photos())

    rows = ""
    max_val = max(by_class.values()) if by_class else 1
    for class_num, cnt in by_class.items():
        bar_width = int(cnt / max_val * 100)
        rows += f"""
        <tr>
            <td style="padding:10px;"><b>{class_num} класс</b></td>
            <td style="padding:10px;">{cnt}</td>
            <td style="padding:10px;"><div style="background:#e6f6fb; border-radius:6px; height:20px;">
                <div style="background:#2193b0; height:100%; width:{bar_width}%; border-radius:6px;"></div>
            </div></td>
        </tr>"""

    subj_cards = ""
    for subject in homework_db:
        cnt = count_by_subject(subject)
        c_count = len(homework_db[subject])
        subj_cards += f"""
        <a class="card" href="/subject/{quote(subject)}">
            <h3>{subject} <span class="count-badge">{cnt}</span></h3>
            <p>{c_count} класс(ов)</p>
        </a>"""

    body = f"""
    <div class="hero">
        <h1>📊 Статистика</h1>
        <p>Заданий: <b>{total}</b> | Предметов: <b>{len(homework_db)}</b> | Классов: <b>{len(by_class)}</b> | Фото: <b>{photos_count}</b></p>
    </div>
    <h2>По классам</h2>
    <table style="width:100%; background:#fff; border-radius:12px; padding:15px; box-shadow:0 4px 15px rgba(0,0,0,.05); border-collapse:collapse;">
        <tr style="color:#888; font-size:13px; text-transform:uppercase;">
            <td style="padding:8px;">Класс</td><td style="padding:8px;">Заданий</td><td style="padding:8px;">Диаграмма</td>
        </tr>
        {rows}
    </table>
    <h2 style="margin:30px 0 15px;">По предметам</h2>
    <div class="grid">{subj_cards}</div>
    <div class="actions"><a class="btn" href="/">← На главную</a></div>
    """
    return html_page("Статистика", body)


def page_search(query):
    q = query.lower().strip()
    results = []
    if q:
        for r in all_tasks_flat():
            if (q in r["task"].lower() or q in r["num"].lower()
                    or q in r["answer"].lower() or q in r["subject"].lower()):
                results.append(r)

    if results:
        cards = ""
        for r in results:
            cards += f"""
            <a class="card" href="/task/{quote(r['subject'])}/{r['class']}/{quote(r['num'])}">
                <span class="badge">{r['subject']} • {r['class']} класс • №{r['num']}</span>
                <p>{r['task']}</p>
            </a>"""
        content = f'<div class="grid">{cards}</div>'
    else:
        content = '<div class="card"><p>😔 Ничего не найдено. Попробуй другой запрос.</p></div>'

    body = f"""
    <div class="hero"><h1>🔍 Поиск</h1><p>Запрос: "<b>{query}</b>" — найдено: {len(results)}</p></div>
    {content}
    <div class="actions"><a class="btn" href="/">← На главную</a></div>
    """
    return html_page("Поиск", body)


def page_404():
    body = f"""
    <div class="hero">
        <h1>404 😔</h1>
        <p>Страница не найдена</p>
        <div class="actions" style="justify-content:center;">
            <a class="btn" href="/">🏠 На главную</a>
            <a class="btn btn-purple" href="/random">🎲 Случайное</a>
        </div>
    </div>
    """
    return html_page("404", body)


# ============================================================
#  Фото-страницы
# ============================================================
def page_photos():
    photos = load_photos()
    if not photos:
        cards = '<div class="card" style="text-align:center; padding:40px;"><h3>Пока нет фото 😔</h3><p style="margin-top:10px;">Загрузи первое фото задания!</p><a class="btn btn-purple" href="/photos/add" style="margin-top:15px;">📸 Загрузить</a></div>'
    else:
        cards = ""
        for p in photos:
            badge = '<span class="has-solution">✅ есть решение</span>' if p.get("solution") else '<span class="no-solution">⏳ нет решения</span>'
            cards += f"""
            <a class="photo-card" href="/photo/{p['id']}">
                <img src="/photos/{p['filename']}" alt="{p['title']}" loading="lazy">
                <div class="photo-info">
                    <h3>{p['title']}</h3>
                    <p>{p.get('subject', '')} {p.get('class_num', '')} • {p['date']}</p>
                    {badge}
                </div>
            </a>"""
    body = f"""
    <div class="hero">
        <h1>📸 Галерея фото</h1>
        <p>Всего: {len(photos)} фото</p>
        <div class="quick-actions">
            <a class="btn btn-purple" href="/photos/add">📸 Загрузить фото</a>
        </div>
    </div>
    <div class="grid">{cards}</div>
    <div class="actions"><a class="btn" href="/">← На главную</a></div>
    """
    return html_page("Фото", body)


def page_photo_add(flash_msg=None, flash_type="success"):
    body = f"""
    <div class="hero">
        <h1>📸 Загрузить фото задания</h1>
        <p>Загрузите фото задания, опишите его — система найдёт ответ в базе</p>
    </div>
    <div class="card" style="max-width:600px; margin:0 auto;">
        <form method="POST" action="/photos/add" enctype="multipart/form-data">
            <div class="form-group">
                <label>Фото задания *</label>
                <input type="file" name="photo" accept="image/*" required>
            </div>
            <div class="form-group">
                <label>Название</label>
                <input type="text" name="title" placeholder="Например: Задание 1.1 стр. 15">
            </div>
            <div class="form-group">
                <label>Предмет</label>
                <input type="text" name="subject" placeholder="Математика">
            </div>
            <div class="form-group">
                <label>Класс</label>
                <input type="number" name="class_num" placeholder="5" min="1" max="11">
            </div>
            <div class="form-group">
                <label>Номер задания</label>
                <input type="text" name="task_number" placeholder="1.1">
            </div>
            <div class="form-group">
                <label>Описание задания (текстом)</label>
                <textarea name="description" rows="3" placeholder="Напишите условие задания текстом — так система найдёт ответ в базе"></textarea>
            </div>
            <button type="submit" class="btn btn-purple" style="width:100%;">📤 Загрузить</button>
        </form>
    </div>
    <div class="actions"><a class="btn" href="/photos">← К галерее</a></div>
    """
    return html_page("Загрузить фото", body, flash_msg, flash_type)


def page_photo_view(photo_id, flash_msg=None, flash_type="success"):
    p = get_photo(photo_id)
    if not p:
        return None

    auto = find_photo_answer(p.get("title", ""), p.get("description", ""))

    if p.get("solution"):
        auto_html = f"""
        <div class="answer-box">
            <b>✅ Решение (добавлено вручную)</b>
            <div class="value">{p['solution']}</div>
        </div>"""
    elif auto:
        auto_html = f"""
        <div class="auto-answer">
            <b>🤖 Найден ответ в базе автоматически</b>
            <p><b>Задание:</b> {auto['task']}</p>
            <p><b>Ответ:</b> {auto['answer']}</p>
            <p><b>Решение:</b> {auto['solution']}</p>
            <p style="margin-top:10px; font-size:13px;">Источник: {auto['subject']}, {auto['class']} класс, №{auto['num']}</p>
        </div>"""
    else:
        auto_html = """
        <div class="card" style="text-align:center;">
            <b>⏳ Решение пока не найдено</b>
            <p style="margin-top:10px;">Добавьте решение вручную ниже — оно появится на этой странице.</p>
        </div>"""

    body = f"""
    <div class="breadcrumbs">
        <a href="/">Главная</a> →
        <a href="/photos">Фото</a> →
        {p['title']}
    </div>
    <h1>{p['title']}</h1>
    <div class="card">
        <p><b>📅 Дата:</b> {p['date']}</p>
        {f"<p><b>📚 Предмет:</b> {p['subject']}</p>" if p.get('subject') else ""}
        {f"<p><b>🎓 Класс:</b> {p['class_num']}</p>" if p.get('class_num') else ""}
        {f"<p><b>📝 Номер:</b> {p['task_number']}</p>" if p.get('task_number') else ""}
        {f"<p><b>💬 Описание:</b> {p['description']}</p>" if p.get('description') else ""}
    </div>
    <img class="photo-full" src="/photos/{p['filename']}" alt="{p['title']}">

    {auto_html}

    <div class="card">
        <h3>✏️ Добавить/изменить решение</h3>
        <form method="POST" action="/photo/{p['id']}/solution">
            <div class="form-group">
                <textarea name="solution" rows="4" placeholder="Напишите решение задания...">{p.get('solution', '')}</textarea>
            </div>
            <button type="submit" class="btn">💾 Сохранить решение</button>
        </form>
    </div>

    <div class="actions">
        <a class="btn" href="/photos">← К галерее</a>
        <form method="POST" action="/photo/{p['id']}/delete" style="display:inline;">
            <button type="submit" class="btn btn-danger" onclick="return confirm('Удалить фото?')">🗑 Удалить</button>
        </form>
    </div>
    """
    return html_page(p['title'], body, flash_msg, flash_type)


# ============================================================
#  class Handler — сервер
# ============================================================
class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)
        parts = [unquote(p) for p in parsed.path.strip("/").split("/") if p]
        html = None
        status = 200

        # ===== API =====
        if parts == ["api", "search"]:
            q = parse_qs(parsed.query).get("q", [""])[0]
            self.send_json(self._search_json(q))
            return
        if parts == ["api", "stats"]:
            self.send_json({
                "total": count_all(),
                "subjects": len(homework_db),
                "classes": len(all_classes()),
                "photos": len(load_photos()),
                "by_class": stats_by_class(),
            })
            return
        if parts == ["api", "random"]:
            self.send_json(random_task() or {})
            return

        # ===== Файл фото =====
        if len(parts) == 2 and parts[0] == "photos" and parts[1] != "add":
            self.serve_photo_file(parts[1])
            return

        # ===== Страницы =====
        if not parts:
            html = page_index()
        elif parts == ["all"]:
            html = page_all()
        elif parts == ["random"]:
            html = page_random()
        elif parts == ["stats"]:
            html = page_stats()
        elif parts == ["search"]:
            q = parse_qs(parsed.query).get("q", [""])[0]
            html = page_search(q)
        elif parts == ["photos"]:
            html = page_photos()
        elif parts == ["photos", "add"]:
            html = page_photo_add()
        elif len(parts) == 2 and parts[0] == "photo":
            html = page_photo_view(parts[1])
        elif len(parts) == 2 and parts[0] == "subject":
            html = page_subject(parts[1])
        elif len(parts) == 4 and parts[0] == "subject" and parts[2] == "class":
            try:
                html = page_class(parts[1], int(parts[3]))
            except ValueError:
                html = None
        elif len(parts) == 4 and parts[0] == "task":
            try:
                html = page_task(parts[1], int(parts[2]), parts[3])
            except ValueError:
                html = None

        if html is None:
            html = page_404()
            status = 404

        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        parsed = urlparse(self.path)
        parts = [unquote(p) for p in parsed.path.strip("/").split("/") if p]

        # Загрузка фото
        if parts == ["photos", "add"]:
            self.handle_photo_upload()
            return

        # Добавить/изменить решение
        if len(parts) == 3 and parts[0] == "photo" and parts[2] == "solution":
            self.handle_solution(parts[1])
            return

        # Удалить фото
        if len(parts) == 3 and parts[0] == "photo" and parts[2] == "delete":
            if delete_photo(parts[1]):
                self.redirect("/photos")
            else:
                self.redirect("/photos")
            return

        self.send_response(404)
        self.end_headers()

    # ===== Вспомогательные методы =====
    def redirect(self, url):
        self.send_response(303)
        self.send_header("Location", url)
        self.end_headers()

    def send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))

    def _search_json(self, q):
        q_low = q.lower().strip()
        results = []
        if q_low:
            for r in all_tasks_flat():
                if (q_low in r["task"].lower() or q_low in r["num"].lower()
                        or q_low in r["answer"].lower()):
                    results.append(r)
        return {"query": q, "count": len(results), "results": results}

    def serve_photo_file(self, filename):
        """Отдаёт файл фото браузеру."""
        # Защита от обхода директорий
        safe_name = os.path.basename(filename)
        filepath = os.path.join(PHOTOS_DIR, safe_name)
        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            self.send_response(404)
            self.end_headers()
            return

        ext = os.path.splitext(safe_name)[1].lower()
        content_types = {
            ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp",
        }
        ctype = content_types.get(ext, "application/octet-stream")

        with open(filepath, "rb") as f:
            data = f.read()

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def handle_photo_upload(self):
        """Обрабатывает POST-загрузку фото."""
        length = int(self.headers.get("Content-Length", 0))
        if length == 0 or length > MAX_FILE_SIZE + 1024 * 100:
            self.redirect("/photos/add")
            return

        body = self.rfile.read(length)
        content_type = self.headers.get("Content-Type", "")

        # Собираем MIME-сообщение для парсера
        raw = f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode() + body

        try:
            msg = BytesParser(policy=email_policy).parsebytes(raw)
        except Exception:
            self.redirect("/photos/add")
            return

        file_data = None
        file_name = ""

        if msg.is_multipart():
            for part in msg.iter_parts():
                cd = part.get("Content-Disposition", "")
                if "form-data" in cd and "filename=" in cd:
                    file_name = part.get_filename() or ""
                    payload = part.get_payload(decode=True)
                    if payload:
                        file_data = payload

        if not file_data or not file_name:
            self.redirect("/photos/add")
            return

        ext = os.path.splitext(file_name)[1].lower()
        if ext not in ALLOWED_EXT:
            self.redirect("/photos/add")
            return

        if len(file_data) > MAX_FILE_SIZE:
            self.redirect("/photos/add")
            return

        # Собираем поля формы
        form = {}
        if msg.is_multipart():
            for part in msg.iter_parts():
                cd = part.get("Content-Disposition", "")
                if "form-data" in cd and "name=" in cd and "filename=" not in cd:
                    name = part.get_param("name", header="content-disposition")
                    payload = part.get_payload(decode=True)
                    if name and payload is not None:
                        try:
                            form[name] = payload.decode("utf-8", errors="replace").strip()
                        except Exception:
                            form[name] = ""

        # Сохраняем файл
        unique_name = f"{uuid.uuid4().hex[:12]}{ext}"
        filepath = os.path.join(PHOTOS_DIR, unique_name)
        with open(filepath, "wb") as f:
            f.write(file_data)

        # Создаём запись
        add_photo(
            filename=unique_name,
            title=form.get("title", ""),
            subject=form.get("subject", ""),
            class_num=int(form.get("class_num") or 0),
            task_number=form.get("task_number", ""),
            description=form.get("description", ""),
            solution="",
        )

        self.redirect("/photos")

    def handle_solution(self, photo_id):
        """Сохраняет решение для фото."""
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8", errors="replace")

        # Простой парсинг urlencoded
        from urllib.parse import parse_qs
        data = parse_qs(body)
        solution = (data.get("solution", [""])[0] or "").strip()

        update_photo_solution(photo_id, solution)
        self.redirect(f"/photo/{photo_id}")

    def log_message(self, fmt, *args):
        print(f"[{self.address_string()}] {fmt % args}")


if __name__ == "__main__":
    total = count_all()
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"

    print("=" * 50)
    print(f"{SITE_EMOJI} {SITE_NAME} запущен!")
    print(f"📚 Предметов: {len(homework_db)}")
    print(f"🎓 Классов:   {len(all_classes())}")
    print(f"📝 Заданий:   {total}")
    print(f"📸 Фото:      {len(load_photos())}")
    print(f"🌐 Порт:      {port}")
    print("🛑 Стоп:      Ctrl+C")
    print("=" * 50)

    server = HTTPServer((host, port), Handler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен. До встречи!")
    finally:
        server.server_close() 