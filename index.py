import sqlite3
from flask import Flask, redirect, render_template, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class DB:
    def __init__(self):
        conn = sqlite3.connect('news.db', check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()


class UserModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_name VARCHAR(50),
                             user_surname VARCHAR(50),
                             user_email VARCHAR(50),
                             password_hash VARCHAR(128),
                             user_type INTEGER
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, user_surname, user_email, password_hash):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, user_surname, user_email, password_hash) 
                          VALUES (?,?,?,?)''', (user_name, user_surname, user_email, password_hash))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute(f'''SELECT * FROM users WHERE id = {user_id}''')
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def exists(self, user_email, password_hash):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_email = ? AND password_hash = ?", (user_email, password_hash))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False, None)


class NewsModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS news 
                                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                   title VARCHAR(100),
                                   content VARCHAR(1000),
                                   user_id INTEGER
                                   )''')
        cursor.close()
        self.connection.commit()

    def insert(self, title, content, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO news 
                            (title, content, user_id) 
                            VALUES (?,?,?)''', (title, content, str(user_id)))
        cursor.close()
        self.connection.commit()

    def get(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute('''SELECT * FROM news WHERE id = ?''' + (str(news_id)))
        row = cursor.fetchone()
        return row

    def get_all(self, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute(f'''SELECT * FROM news WHERE user_id = {user_id} ORDER BY id DESC''')
        else:
            cursor.execute('''SELECT * FROM news''')
        rows = cursor.fetchall()
        return rows

    def get_feed(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute(
            f'''SELECT * FROM news WHERE user_id in (SELECT follow_id from feed WHERE user_id =  {user_id} ) ORDER BY id DESC''')
        rows = cursor.fetchall()
        return rows

    def delete(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute(f'''DELETE FROM news WHERE id = {news_id}''')
        cursor.close()
        self.connection.commit()


class Message:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS messages 
                                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                   from_user INTEGER,
                                   to_user INTEGER,
                                   content VARCHAR(2500)
                                   )''')
        cursor.close()
        self.connection.commit()

    def insert(self, from_user, to_user, content):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO messages 
                            (from_user, to_user, content) 
                            VALUES (?,?,?)''', (str(from_user), str(to_user), content))
        cursor.close()
        self.connection.commit()

    def get_all(self, to_user, from_user=None):
        cursor = self.connection.cursor()
        if from_user is None:
            cursor.execute(f'''SELECT * FROM messages WHERE to_user = {to_user} ORDER BY id DESC''')
        else:
            cursor.execute(
                f'''SELECT * FROM messages WHERE to_user = {to_user} and from_user = {from_user}  ORDER BY id DESC''')
        rows = cursor.fetchall()
        return rows

    def delete(self, id):
        cursor = self.connection.cursor()
        cursor.execute(f'''DELETE FROM messages WHERE id = {id}''')
        cursor.close()
        self.connection.commit()


class Feed:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS feed 
                                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                   user_id INTEGER,
                                   follow_id INTEGER
                                   )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_id, follow_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO feed 
                            ( user_id, follow_id) 
                            VALUES (?,?)''', (str(user_id), str(follow_id)))
        cursor.close()
        self.connection.commit()

    def delete(self, user_id, follow_id):
        cursor = self.connection.cursor()
        cursor.execute(f'''DELETE FROM feed WHERE  user_id= {user_id} and follow_id = {follow_id}''')
        cursor.close()
        self.connection.commit()

    def exists_feed(self, user_id, test_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM feed WHERE user_id = " + str(user_id) + " AND follow_id = " + str(test_id))
        row = cursor.fetchone()
        return True if row else False


class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
    reg = SubmitField('Регистрация')


class RegForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired()])
    email = StringField('Почта', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_test = PasswordField('Повторите пароль', validators=[DataRequired()])
    back = SubmitField('Назад')
    reg = SubmitField('Зарегистрироваться')


class Profile(FlaskForm):
    name = StringField('Имя')
    title = StringField('Заголовок новости', validators=[DataRequired()])
    content = TextAreaField('Текст новости', validators=[DataRequired()])
    submit = SubmitField('Добавить')


db = DB()
user_model = UserModel(db.get_connection())
news_model = NewsModel(db.get_connection())
feed_model = Feed(db.get_connection())
message_model = Message(db.get_connection())
user_model.init_table()
news_model.init_table()
feed_model.init_table()
message_model.init_table()
app = Flask(__name__, )
app.config['SECRET_KEY'] = '12345'
user_id = None
user_status = False


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    global user_id, user_status
    form = LoginForm()
    user_status, user_id = user_model.exists(form.email.data, form.password.data)
    session['user_status'] = False
    if form.submit.data:
        if form.validate_on_submit() and user_status:
            session['user_status'] = True
            session['id'], session['name'], session['surname'], session['email'] = user_model.get(user_id)[:4]
            print(user_model.get(user_id))
            return redirect('/news')
    elif form.reg.data:
        return redirect('/register')
    return render_template('login.html', title='Авторизация', form=form, user_status=user_status)


@app.route('/logout', methods=['GET'])
def logout():
    session = {}
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegForm()
    if form.back.data:
        return redirect('/login')
    elif form.reg.data:
        if form.validate_on_submit():
            if form.password.data == form.password_test.data:
                user_model.insert(form.email.data, form.surname.data, form.email.data, form.password.data)
                return redirect('/login')

    return render_template('register.html', title='Авторизация', form=form)


@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id):
    form = Profile()
    news_list = news_model.get_all(user_id)
    name, surname, email, = user_model.get(user_id)[1:4:]
    if user_id == session['id']:
        lock = True
    else:
        lock = False

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        news_model.insert(title, content, user_id)
        return redirect(f"/profile/{session['id']}")

    return render_template('profile.html', title=f'{name} {surname}', form=form, news=news_list,
                           Name=name, Surname=surname, lock=lock)


@app.route('/index')
@app.route('/news')
def news():
    if user_status:
        news_list = news_model.get_feed(user_id)
        return render_template('news.html', news=news_list, user=user_model)
    else:
        return redirect('/login')


@app.route('/users/')
def users():
    if user_status:
        user_list = user_model.get_all()
        subs = []
        for item in user_list:
            if feed_model.exists_feed(user_id, item[0]):
                subs.append(True)
            else:

                subs.append(False)

        return render_template('users.html', test="<h2>test</h2>", users=zip(user_list, subs))
    else:
        return redirect('/login')


@app.route('/groups/')
def groups():
    if user_status:
        user_list = user_model.get_all()
        subs = []
        for item in user_list:
            if feed_model.exists_feed(user_id, item[0]):
                subs.append(True)
            else:

                subs.append(False)

        return render_template('users.html', test="<h2>test</h2>", users=zip(user_list, subs))
    else:
        return redirect('/login')


@app.route('/subsribe/<int:follow_id>', methods=['GET'])
def subsribe(follow_id):
    if not user_status:
        return redirect('/login')
    feed_model.insert(user_id, follow_id)
    return redirect("/users")


@app.route('/unsubsribe/<int:follow_id>', methods=['GET'])
def unsubsribe(follow_id):
    if not user_status:
        return redirect('/login')
    feed_model.delete(user_id, follow_id)
    return redirect("/users")


@app.route('/messages')
def messages():
    if user_status:
        news_list = news_model.get_all(user_id)
        return render_template('news.html', news=news_list)
    else:
        return redirect('/login')


@app.route('/delete_news/<int:news_id>', methods=['GET'])
def delete_news(news_id):
    if not user_status:
        return redirect('/login')
    news_model.delete(news_id)
    return redirect(f"/profile/{session['id']}")


@app.route('/news', methods=['GET'])
def button_news():
    return redirect('./news')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
