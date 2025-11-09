from flask import Flask, render_template, request, redirect, session, jsonify, flash, url_for
import random
from datetime import datetime
import json
import os
from typing import Dict, List

app = Flask(__name__)
app.secret_key = 'greenwork_production_secret_2024_v2'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['TEMPLATES_AUTO_RELOAD'] = True

class Database:
    def __init__(self):
        self.users: Dict = {
            "VADIM": {
                "password": "VADIM", 
                "role": "user", 
                "balance": 0, 
                "email": "vadim@greenwork.com",
                "registered": "2024-01-15",
                "completed_tasks": 0,
                "total_earned": 0
            },
            "Aleksey": {
                "password": "Aleksey", 
                "role": "admin", 
                "balance": 0, 
                "email": "aleksey@greenwork.com",
                "registered": "2024-01-15", 
                "completed_tasks": 0,
                "total_earned": 0
            }
        }
        self.withdrawal_requests: List = []
        self.task_history: List = []
        self.payment_methods: List = [
            {"id": "sberbank", "name": "Сбербанк", "type": "card", "icon": "🏦"},
            {"id": "tinkoff", "name": "Тинькофф", "type": "card", "icon": "💛"},
            {"id": "vtb", "name": "ВТБ", "type": "card", "icon": "🔷"},
            {"id": "alfabank", "name": "Альфа-Банк", "type": "card", "icon": "🔶"},
            {"id": "mir", "name": "Карта МИР", "type": "card", "icon": "🌍"},
            {"id": "visa", "name": "Visa", "type": "card", "icon": "💳"},
            {"id": "mastercard", "name": "MasterCard", "type": "card", "icon": "💳"},
            {"id": "qiwi", "name": "Qiwi", "type": "ewallet", "icon": "🥝"},
            {"id": "yomoney", "name": "ЮMoney", "type": "ewallet", "icon": "💜"},
            {"id": "paypal", "name": "PayPal", "type": "ewallet", "icon": "🔵"}
        ]

db = Database()

class TaskBot:
    def __init__(self, bot_id: int):
        self.bot_id = bot_id
        self.task_types = [
            {
                "title": "🔧 Разработка Python скрипта", 
                "description": "Создайте функцию для вычисления чисел Фибоначчи с использованием рекурсии и мемоизации.",
                "difficulty": "medium",
                "category": "programming",
                "icon": "🐍"
            },
            {
                "title": "🌍 Перевод технической документации", 
                "description": "Переведите техническую документацию с английского на русский (около 500 символов).",
                "difficulty": "easy", 
                "category": "translation",
                "icon": "📄"
            },
            {
                "title": "🐛 Дебаггинг кода", 
                "description": "Проанализируйте предоставленный код и найдите синтаксические и логические ошибки.",
                "difficulty": "hard",
                "category": "debugging",
                "icon": "🔍"
            },
            {
                "title": "📊 Анализ dataset",
                "description": "Проанализируйте dataset с продажами и найдите сезонные закономерности.",
                "difficulty": "medium",
                "category": "analysis",
                "icon": "📈"
            },
            {
                "title": "🎨 Создание SEO-контента",
                "description": "Напишите SEO-оптимизированную статью на тему 'Искусственный интеллект в 2024 году' (1000+ символов).", 
                "difficulty": "easy",
                "category": "content",
                "icon": ✍️"
            },
            {
                "title": "🤖 Создание Telegram бота",
                "description": "Разработайте простого Telegram бота для уведомлений на Python.",
                "difficulty": "medium",
                "category": "programming", 
                "icon": "🤖"
            },
            {
                "title": "📱 Адаптация дизайна",
                "description": "Адаптируйте веб-дизайн под мобильные устройства.",
                "difficulty": "medium",
                "category": "design",
                "icon": "📱"
            },
            {
                "title": "🔍 Тестирование API",
                "description": "Протестируйте REST API endpoints и составьте отчет по багам.",
                "difficulty": "hard",
                "category": "testing",
                "icon": "⚡"
            }
        ]
    
    def generate_task(self) -> Dict:
        task = random.choice(self.task_types).copy()
        task["reward"] = random.randint(20, 100)
        task["bot_id"] = self.bot_id
        task["time_estimate"] = f"{random.randint(5, 45)} минут"
        task["id"] = f"task_{self.bot_id}_{random.randint(1000, 9999)}"
        return task

# Инициализация ботов
bots = [TaskBot(i) for i in range(100)]

# Маршруты Flask
@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect('/dashboard')
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    
    if username in db.users and db.users[username]['password'] == password:
        session['username'] = username
        session['role'] = db.users[username]['role']
        session['logged_in'] = True
        return jsonify({'success': True, 'redirect': '/dashboard'})
    else:
        return jsonify({'success': False, 'error': 'Неверный логин или пароль'})

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect('/')
    user_data = db.users.get(session['username'], {})
    return render_template('dashboard.html', 
                         user=user_data, 
                         payment_methods=db.payment_methods)

@app.route('/tasks')
def tasks():
    if not session.get('logged_in'):
        return redirect('/')
    
    current_tasks = []
    for _ in range(8):
        bot = random.choice(bots)
        task = bot.generate_task()
        current_tasks.append(task)
    
    return render_template('tasks.html', tasks=current_tasks)

@app.route('/complete_task', methods=['POST'])
def complete_task():
    if not session.get('logged_in'):
        return jsonify({'success': False})
    
    username = session['username']
    reward = random.randint(20, 100)
    
    db.users[username]['balance'] += reward
    db.users[username]['completed_tasks'] += 1
    db.users[username]['total_earned'] += reward
    
    task_record = {
        'user': username,
        'reward': reward,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'task_type': 'completed'
    }
    db.task_history.append(task_record)
    
    return jsonify({
        'success': True, 
        'reward': reward, 
        'balance': db.users[username]['balance'],
        'completed_tasks': db.users[username]['completed_tasks'],
        'total_earned': db.users[username]['total_earned']
    })

@app.route('/request_withdrawal', methods=['POST'])
def request_withdrawal():
    if not session.get('logged_in'):
        return jsonify({'success': False})
    
    username = session['username']
    data = request.get_json()
    
    if db.users[username]['balance'] < 6000:
        return jsonify({'success': False, 'error': '❌ Недостаточно средств для вывода. Минимум 6,000 ₽'})
    
    if int(data['amount']) < 6000:
        return jsonify({'success': False, 'error': '❌ Минимальная сумма вывода: 6,000 ₽'})
    
    if int(data['amount']) > db.users[username]['balance']:
        return jsonify({'success': False, 'error': '❌ Запрашиваемая сумма превышает ваш баланс'})
    
    withdrawal_request = {
        'id': len(db.withdrawal_requests) + 1,
        'user_id': username,
        'amount': data['amount'],
        'card_number': data['card_number'],
        'card_holder': data['card_holder'].upper(),
        'payment_method': data['payment_method'],
        'status': 'pending',
        'created_at': datetime.now().strftime("%d.%m.%Y %H:%M"),
        'user_balance': db.users[username]['balance'],
        'contact_email': db.users[username]['email']
    }
    
    db.withdrawal_requests.append(withdrawal_request)
    
    # Списываем сумму с баланса
    db.users[username]['balance'] -= int(data['amount'])
    
    return jsonify({
        'success': True, 
        'message': '✅ Заявка на вывод успешно отправлена! Обработка занимает до 7 рабочих дней.',
        'new_balance': db.users[username]['balance']
    })

@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return redirect('/dashboard')
    
    stats = {
        'total_users': len(db.users),
        'total_withdrawals': len(db.withdrawal_requests),
        'pending_requests': len([r for r in db.withdrawal_requests if r['status'] == 'pending']),
        'total_processed': len([r for r in db.withdrawal_requests if r['status'] == 'paid']),
        'total_earned_all': sum(user['total_earned'] for user in db.users.values())
    }
    
    return render_template('admin.html', 
                         requests=db.withdrawal_requests, 
                         users=db.users,
                         stats=stats)

@app.route('/admin/update_balance', methods=['POST'])
def update_balance():
    if session.get('role') != 'admin':
        return jsonify({'success': False})
    
    data = request.get_json()
    username = data['username']
    new_balance = int(data['balance'])
    
    if username in db.users:
        db.users[username]['balance'] = new_balance
    
    return jsonify({'success': True, 'new_balance': new_balance})

@app.route('/admin/process_request', methods=['POST'])
def process_request():
    if session.get('role') != 'admin':
        return jsonify({'success': False})
    
    data = request.get_json()
    request_id = int(data['request_id'])
    action = data['action']
    
    for req in db.withdrawal_requests:
        if req['id'] == request_id:
            req['status'] = action
            req['processed_at'] = datetime.now().strftime("%d.%m.%Y %H:%M")
            req['processed_by'] = session['username']
            break
    
    return jsonify({'success': True})

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.errorhandler(404)
def not_found(e):
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)