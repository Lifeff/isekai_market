from flask import Flask, request, redirect, session, render_template
from werkzeug.utils import secure_filename
import sqlite3, os, uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'isekai_secret_key_2024'

ADMIN_ID = 'admin'
ADMIN_PW = 'admin1234'

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ─── DB 연결 ───────────────────────────────────────
def get_db():
    conn = sqlite3.connect('market.db')
    conn.row_factory = sqlite3.Row
    return conn, conn.cursor()

# ─── DB 초기화 ─────────────────────────────────────
def init_db():
    conn, cursor = get_db()
    cursor.execute('''CREATE TABLE IF NOT EXISTS items (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        title       TEXT,
        category    TEXT,
        price       INTEGER,
        description TEXT,
        seller      TEXT,
        status      TEXT DEFAULT '판매중',
        views       INTEGER DEFAULT 0,
        date        TEXT,
        image       TEXT DEFAULT NULL
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        nickname TEXT,
        date     TEXT
    )''')
    # 기존 DB에 image 컬럼 없으면 추가
    try:
        cursor.execute('ALTER TABLE items ADD COLUMN image TEXT DEFAULT NULL')
    except:
        pass
    conn.commit()
    conn.close()

init_db()

# ─── 이미지 유효성 검사 ─────────────────────────────
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file):
    if not file or file.filename == '':
        return None
    if not allowed_file(file.filename):
        return None
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return filename

def delete_image(filename):
    if filename:
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(path):
            os.remove(path)

# ─── 메인 목록 (Read - 전체) ────────────────────────
@app.route('/')
def index():
    conn, cursor = get_db()
    keyword  = request.args.get('keyword', '')
    category = request.args.get('category', '')

    query  = 'SELECT * FROM items WHERE 1=1'
    params = []
    if keyword:
        query += ' AND (title LIKE ? OR description LIKE ? OR seller LIKE ?)'
        params += [f'%{keyword}%', f'%{keyword}%', f'%{keyword}%']
    if category:
        query += ' AND category = ?'
        params.append(category)
    query += ' ORDER BY id DESC'

    cursor.execute(query, params)
    items = cursor.fetchall()
    cursor.execute('SELECT COUNT(*) FROM items')
    total = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM items WHERE status="판매중"')
    on_sale = cursor.fetchone()[0]
    conn.close()
    return render_template('index.html',
        items=items, total=total, on_sale=on_sale,
        keyword=keyword, category=category)

# ─── 상세보기 (Read - 단건) ─────────────────────────
@app.route('/detail/<int:id>/')
def detail(id):
    conn, cursor = get_db()
    # 세션 기반 조회수 중복 방지
    viewed_key = f'viewed_{id}'
    if not session.get(viewed_key):
        cursor.execute('UPDATE items SET views = views + 1 WHERE id = ?', (id,))
        conn.commit()
        session[viewed_key] = True
    cursor.execute('SELECT * FROM items WHERE id = ?', (id,))
    item = cursor.fetchone()
    conn.close()
    if not item:
        return redirect('/')
    return render_template('detail.html', item=item,
        user=session.get('user'), is_admin=session.get('is_admin'))

# ─── 상품 등록 (Create) ─────────────────────────────
@app.route('/create/', methods=['GET', 'POST'])
def create():
    if not session.get('user') and not session.get('is_admin'):
        return redirect('/login/')
    error = ''
    if request.method == 'POST':
        title    = request.form['title']
        category = request.form['category']
        price    = request.form['price']
        desc     = request.form['description']
        seller   = session.get('user', 'admin')
        date     = datetime.now().strftime('%Y-%m-%d')

        image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            if not allowed_file(image_file.filename):
                error = '허용되지 않는 파일 형식입니다. (jpg, jpeg, png, gif, webp만 가능)'
                return render_template('create.html', error=error)
        filename = save_image(image_file)

        conn, cursor = get_db()
        cursor.execute(
            'INSERT INTO items (title,category,price,description,seller,date,image) VALUES (?,?,?,?,?,?,?)',
            (title, category, price, desc, seller, date, filename)
        )
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('create.html', error=error)

# ─── 수정 (Update) ──────────────────────────────────
@app.route('/update/<int:id>/', methods=['GET', 'POST'])
def update(id):
    conn, cursor = get_db()
    cursor.execute('SELECT * FROM items WHERE id = ?', (id,))
    item = cursor.fetchone()
    if not item:
        conn.close()
        return redirect('/')
    if not session.get('is_admin') and session.get('user') != item['seller']:
        conn.close()
        return redirect(f'/detail/{id}/')
    error = ''
    if request.method == 'POST':
        title    = request.form['title']
        category = request.form['category']
        price    = request.form['price']
        desc     = request.form['description']
        status   = request.form['status']

        image_file  = request.files.get('image')
        old_image   = item['image']
        new_filename = old_image  # 기본: 기존 이미지 유지

        # 이미지 삭제 체크박스
        if request.form.get('delete_image'):
            delete_image(old_image)
            new_filename = None
        elif image_file and image_file.filename != '':
            if not allowed_file(image_file.filename):
                error = '허용되지 않는 파일 형식입니다. (jpg, jpeg, png, gif, webp만 가능)'
                conn.close()
                return render_template('update.html', item=item, error=error)
            delete_image(old_image)
            new_filename = save_image(image_file)

        cursor.execute(
            'UPDATE items SET title=?,category=?,price=?,description=?,status=?,image=? WHERE id=?',
            (title, category, price, desc, status, new_filename, id)
        )
        conn.commit()
        conn.close()
        return redirect(f'/detail/{id}/')
    conn.close()
    return render_template('update.html', item=item, error=error)

# ─── 삭제 (Delete) ──────────────────────────────────
@app.route('/delete/<int:id>/')
def delete(id):
    conn, cursor = get_db()
    cursor.execute('SELECT * FROM items WHERE id = ?', (id,))
    item = cursor.fetchone()
    if item:
        if session.get('is_admin') or session.get('user') == item['seller']:
            delete_image(item['image'])
            cursor.execute('DELETE FROM items WHERE id = ?', (id,))
            conn.commit()
    conn.close()
    return redirect('/')

# ─── 회원가입 ────────────────────────────────────────
@app.route('/register/', methods=['GET', 'POST'])
def register():
    error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        nickname = request.form['nickname']
        date     = datetime.now().strftime('%Y-%m-%d')
        conn, cursor = get_db()
        try:
            cursor.execute(
                'INSERT INTO users (username,password,nickname,date) VALUES (?,?,?,?)',
                (username, password, nickname, date)
            )
            conn.commit()
            conn.close()
            return redirect('/login/')
        except sqlite3.IntegrityError:
            error = '이미 사용 중인 아이디입니다.'
            conn.close()
    return render_template('register.html', error=error)

# ─── 로그인 ──────────────────────────────────────────
@app.route('/login/', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_ID and password == ADMIN_PW:
            session['user']     = 'admin'
            session['is_admin'] = True
            return redirect('/admin/')
        conn, cursor = get_db()
        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user']     = user['nickname']
            session['is_admin'] = False
            return redirect('/')
        error = '아이디 또는 비밀번호가 틀렸습니다.'
    return render_template('login.html', error=error)

# ─── 로그아웃 ────────────────────────────────────────
@app.route('/logout/')
def logout():
    session.clear()
    return redirect('/')

# ─── 관리자 페이지 ───────────────────────────────────
@app.route('/admin/')
def admin():
    if not session.get('is_admin'):
        return redirect('/login/')
    conn, cursor = get_db()
    cursor.execute('SELECT * FROM items ORDER BY id DESC')
    items = cursor.fetchall()
    cursor.execute('SELECT * FROM users ORDER BY id DESC')
    users = cursor.fetchall()
    cursor.execute('SELECT COUNT(*) FROM items')
    total_items = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM items WHERE status="판매중"')
    on_sale = cursor.fetchone()[0]
    conn.close()
    return render_template('admin.html',
        items=items, users=users,
        total_items=total_items, total_users=total_users, on_sale=on_sale)

# ─── 관리자 - 유저 삭제 ─────────────────────────────
@app.route('/admin/delete_user/<int:id>/')
def admin_delete_user(id):
    if not session.get('is_admin'):
        return redirect('/login/')
    conn, cursor = get_db()
    cursor.execute('DELETE FROM users WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/admin/')

if __name__ == '__main__':
    pass  # 배포 시 주석처리 - PythonAnywhere는 wsgi.py로 실행
    # app.run(debug=True)
