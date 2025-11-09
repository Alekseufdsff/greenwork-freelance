# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production-12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Модель новости
class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Модель продукта
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    product_type = db.Column(db.String(20), default='key')  # 'key', 'subscription', 'free'
    features = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Модель промокода
class PromoCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_percent = db.Column(db.Float, default=0)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Модель заказа
class UserProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    activation_key = db.Column(db.String(100))
    is_activated = db.Column(db.Boolean, default=False)
    purchased_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

# Создаем таблицы и тестовые данные
@app.before_first_request
def create_tables():
    db.create_all()
    
    # Создаем специального админа Aleksey_Mainkraft
    if not User.query.filter_by(username='Aleksey_Mainkraft').first():
        admin_user = User(
            username='Aleksey_Mainkraft',
            email='aleksey@example.com',
            password=generate_password_hash('0713401092', method='sha256')
        )
        db.session.add(admin_user)
        
        # Тестовые новости
        news1 = News(title="Добро пожаловать!", content="Мы запустили новый магазин цифровых товаров.")
        news2 = News(title="Обновление системы", content="Добавлена возможность покупки и активации продуктов.")
        db.session.add(news1)
        db.session.add(news2)
        
        # Тестовые продукты
        products = [
            Product(
                name="Премиум подписка на 1 месяц",
                description="Полный доступ ко всем функциям на 30 дней",
                price=299.99,
                product_type="subscription",
                features="✓ Все возможности\n✓ Приоритетная поддержка\n✓ Доступ к бета-тестам\n✓ Эксклюзивный контент"
            ),
            Product(
                name="Игровой ключ активации",
                description="Постоянный ключ для активации игры",
                price=999.99,
                product_type="key",
                features="✓ Постоянный доступ\n✓ Все DLC включены\n✓ Техническая поддержка"
            ),
            Product(
                name="Бесплатный демо-доступ",
                description="Бесплатный пробный период на 7 дней",
                price=0.00,
                product_type="free",
                features="✓ Базовые функции\n✓ Ограниченный период\n✓ Техподдержка"
            )
        ]
        
        for product in products:
            db.session.add(product)
        
        db.session.commit()

# Проверка админских прав
def is_admin():
    return session.get('username') == 'Aleksey_Mainkraft'

# Главная страница
@app.route('/')
def index():
    news_list = News.query.order_by(News.created_at.desc()).limit(5).all()
    return render_template('index.html', news_list=news_list)

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Пользователь с таким именем или почтой уже существует.', 'error')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Добро пожаловать, {username}!', 'success')
            
            if username == 'Aleksey_Mainkraft':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('profile'))
        else:
            flash('Неверное имя пользователя или пароль.', 'error')

    return render_template('login.html')

# Выход
@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))

# Личный кабинет
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    user_products = UserProduct.query.filter_by(user_id=user.id).all()
    
    return render_template('profile.html', user=user, user_products=user_products)

# Страница продуктов
@app.route('/products')
def products():
    product_list = Product.query.filter_by(is_active=True).all()
    return render_template('products.html', products=product_list)

# Админ-панель
@app.route('/admin')
def admin_dashboard():
    if not is_admin():
        flash('Доступ запрещен. Только для Aleksey_Mainkraft', 'error')
        return redirect(url_for('index'))
    
    stats = {
        'users_count': User.query.count(),
        'products_count': Product.query.count(),
        'news_count': News.query.count()
    }
    
    return render_template('admin/dashboard.html', stats=stats)

# Управление новостями
@app.route('/admin/news')
def admin_news():
    if not is_admin():
        flash('Доступ запрещен. Только для Aleksey_Mainkraft', 'error')
        return redirect(url_for('index'))
    
    news_list = News.query.all()
    return render_template('admin/news.html', news_list=news_list)

# Добавление новости
@app.route('/admin/news/add', methods=['GET', 'POST'])
def admin_add_news():
    if not is_admin():
        flash('Доступ запрещен.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        new_news = News(title=title, content=content)
        db.session.add(new_news)
        db.session.commit()
        
        flash('Новость успешно добавлена!', 'success')
        return redirect(url_for('admin_news'))
    
    return render_template('admin/add_news.html')

# Управление продуктами
@app.route('/admin/products')
def admin_products():
    if not is_admin():
        flash('Доступ запрещен.', 'error')
        return redirect(url_for('index'))
    
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

# Добавление продукта
@app.route('/admin/products/add', methods=['GET', 'POST'])
def admin_add_product():
    if not is_admin():
        flash('Доступ запрещен.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        product_type = request.form['product_type']
        features = request.form['features']
        
        new_product = Product(
            name=name,
            description=description,
            price=price,
            product_type=product_type,
            features=features
        )
        db.session.add(new_product)
        db.session.commit()
        
        flash('Продукт успешно добавлен!', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/add_product.html')

if __name__ == '__main__':
    app.run(debug=True)