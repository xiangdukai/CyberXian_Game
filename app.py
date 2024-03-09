from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, Character
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cyberxian_game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_character', methods=['GET', 'POST'])
def create_character():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']  # 获取密码
        existing_character = Character.query.filter_by(name=name).first()
        if existing_character is None:
            # 创建新角色时包括密码
            new_character = Character(name=name, password=password)
            db.session.add(new_character)
            db.session.commit()
            flash('Character created successfully!')
            return redirect(url_for('index'))
        else:
            flash('Character name already exists!')
            return redirect(url_for('index'))
    return render_template('create_character.html')


@app.route('/practice/<int:character_id>', methods=['POST'])  # 允许 POST 方法
def practice(character_id):
    character = Character.query.get(character_id)
    if character:
        message = character.practice()
        db.session.commit()
        flash(message)  # 使用 flash 传递消息
    else:
        flash("角色不存在。")
    return redirect(url_for('character_status', character_id=character_id))

    
@app.route('/character_status/<int:character_id>')
def character_status(character_id):
    # 确保角色ID在会话中并且匹配请求的角色ID
    if 'character_id' in session and session['character_id'] == character_id:
        character = Character.query.get(character_id)
        if character:
            # 渲染角色状态页面
            return render_template('character_status.html', character=character)
        else:
            flash("角色不存在。")
            return redirect(url_for('index'))
    else:
        flash("你不能查看其他用户的角色状态。")
        return redirect(url_for('index'))

@app.route('/find_opportunity/<int:character_id>', methods=['POST'])
def find_opportunity(character_id):
    character = Character.query.get(character_id)
    if character:
        message = character.find_opportunity()
        flash(message)
    else:
        flash("角色不存在。")
    return redirect(url_for('character_status', character_id=character_id))


@app.route('/duel', methods=['POST'])
def duel():
    character_id = request.form.get('character_id')
    opponent_id = request.form.get('opponent_id')
    character = Character.query.get(character_id)
    opponent = Character.query.get(opponent_id)
    if character and opponent:
        message = character.duel(opponent)
        flash(message)
    else:
        flash("Character or opponent does not exist.")
    return redirect(url_for('character_status', character_id=character_id))

@app.route('/rebirth/<int:character_id>', methods=['POST'])
def rebirth(character_id):
    character = Character.query.get(character_id)
    if character:
        message = character.rebirth()
        flash(message)
    else:
        flash("角色不存在。")
    return redirect(url_for('character_status', character_id=character_id))

    
@app.route('/login', methods=['POST'])
def login():
    name = request.form['name']
    password = request.form['password']
    character = Character.query.filter_by(name=name).first()
    if character and character.password == password:
        session['character_id'] = character.id  # 保存用户状态
        return redirect(url_for('character_status', character_id=character.id))
    else:
        flash('Invalid username or password!')
        return redirect(url_for('index'))
    
@app.route('/logout')
def logout():
    session.pop('character_id', None)  # 从会话中移除用户ID
    return redirect(url_for('index'))

@app.route('/leaderboard')
def leaderboard():
    # 使用 SQLAlchemy 查询并按 Spirit Power 和 Combat Talent 排序
    characters = Character.query.order_by(Character.spirit_power.desc(), Character.combat_talent.desc()).all()
    return render_template('leaderboard.html', characters=characters)

if __name__ == '__main__':
    app.run(debug=True)
