from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import (LoginManager,
                         UserMixin,
                         login_required,
                         login_user,
                         logout_user,
                         current_user)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_bootstrap import Bootstrap



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo_list.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "KJHEF87638Y32J#@^%$^KHSDGV"


db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)





###===============>>> Forms <<<====================###


class ToDos(FlaskForm):
    item = StringField('Add a new item', validators=[DataRequired()])


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=10)])


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=10)])


###================================================###


###===============>>> Database <<<====================###


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(25), nullable=False)
    todolist = db.relationship('TodoList', back_populates='user')




class TodoList(db.Model):
    __tablename__ = 'todolist'
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='todolist')

# db.create_all()

###================================================###


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/', )
@login_required
def home():
    form = ToDos()
    tasks = TodoList.query.all()
    return render_template('index.html', form=form, tasks=tasks, status=status)


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = ToDos()
    task = form.item.data

    if form.validate_on_submit():
        task_db = TodoList(task=task)
        db.session.add(task_db)
        db.session.commit()
    return redirect(url_for('home'))


@app.route('/complete/<int:task_id>')
def status(task_id):
    todo = TodoList.query.filter_by(id=task_id).first()
    todo.status = True
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/delete/<int:task_id>')
def delete(task_id):
    to_delete = TodoList.query.filter_by(id=task_id).first()
    print(to_delete)
    db.session.delete(to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form_type = 'register'
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User(
                username=form.username.data,
                password=form.password.data,
            )
            db.session.add(user)
            db.session.commit()
            login_user(user=user)

            return redirect(url_for('home'))
        else:
            flash('Something Went Wrong!')
    return render_template('login_register.html', form_type=form_type, form=form)
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    form_type = 'login'
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if user:
            if username == user.username and password == user.password:
                login_user(user=user)
                print('logged in')
                return redirect(url_for('home'))
        else:
            flash('User  does not exist!')
    return render_template('login_register.html', form_type=form_type, form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

#############################################################
if __name__ == '__main__':
    app.run(debug=True, port=8080)
