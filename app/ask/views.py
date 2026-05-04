import re
from flask import Blueprint, render_template, request, url_for, redirect, flash, current_app
from flask.json import jsonify
from flask_login import current_user, login_required
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from ..auth.models import User
from .models import Question, Answer, Comment, Knowledge, Disease
from ..extensions import db
from data.kbqa_test import KBQA

ask = Blueprint('ask', __name__, url_prefix='/')

@ask.route('', methods=['GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('ask.index'))
    return render_template('login.html')

@ask.route('/index', methods=['GET', 'POST'])
def index():
    # user_id = current_user.id
    # print('111:', user_id)
    if request.method == "POST":
        search_name = (request.form.get("search_name") or '').strip()
        if not search_name:
            return redirect(url_for('ask.index'))
        handler = KBQA()
        result = handler.qa_main(search_name)
        return render_template('ask/index.html', current_user=current_user, result=result, question=search_name)
    return render_template('ask/index.html', current_user=current_user)

@ask.route('/knowledge_search', methods=['GET', 'POST'])
def knowledge_search():
    search_name = (request.values.get("search_name") or "").strip()
    result = []
    if search_name:
        result = Knowledge.query.filter(Knowledge.content.like("%" + search_name + "%")).all()
    return render_template('ask/knowledge_search.html', current_user=current_user, result=result, search_name=search_name)

@ask.route('/question/add', methods=['GET', 'POST'])
@login_required
def question_add():
    if request.method == 'POST':
        title = (request.form.get('title') or '').strip()
        content = (request.form.get('content') or '').strip()
        if not title or not content:
            return jsonify(status='error', info='标题和内容不能为空！')
        question = Question.query.filter(Question.title == title).first()
        if not question:
            question = Question()
            question.title = title
            question.content = content
            question.author_id = current_user.id
            db.session.add(question)
            db.session.commit()
            # flash("问题创建成功！", "ok")
            return jsonify(status='success', info='创建成功！')
        else:
            return jsonify(status='error', info='已经存在该问题！')
    else:
        return render_template('ask/ask_question.html')

@ask.route('/question/list/<int:page>', methods=['GET', 'POST'])
def question_list(page=0):
    if page == 0:
        page = 1
    questions = Question.query.order_by(Question.create_time.desc()).paginate(page=page, per_page=5)
    return render_template('ask/list_question.html', qss=questions)

@ask.route('/question/<int:question_id>')
def question_detail(question_id):
    question = Question.query.filter_by(id=question_id).first_or_404()
    return render_template('ask/detail_question.html', qs=question)

@ask.route('/question/answer/<int:question_id>', methods=['GET', 'POST'])
@login_required
def question_answer(question_id):
    content = (request.form.get('content') or '').strip()
    if not content:
        return jsonify(status='error', info='内容不能为空')
    question = Question.query.filter_by(id=question_id).first()
    if not question:
        return jsonify(status='error', info='不存在该问题')
    answer = Answer()
    answer.content = content
    answer.author_id = current_user.id
    answer.question_id = question_id
    question.answers_count += 1
    db.session.add(question)
    db.session.add(answer)
    db.session.commit()
    return jsonify(status='success', info='回答成功！')

@ask.route('/question/<int:question_id>/comment', methods=['GET', 'POST'])
@login_required
def question_comment(question_id):
    rid = (request.form.get('rid') or '').strip()
    content = (request.form.get('content') or '').strip()
    if not rid or not content:
        return jsonify(status='error', info='参数不完整')
    answer = Answer.query.filter_by(id=rid).first()
    if not answer:
        return jsonify(status='error', info='没有该条回复')

    comment = Comment()
    comment.content = content
    comment.author_id = current_user.id
    comment.answer_id = answer.id
    answer.answers_count += 1
    db.session.add(answer)
    db.session.add(comment)
    db.session.commit()
    return jsonify(status='success', info='回复成功！')

@ask.route('/knowledge/list/<int:page>', methods=['GET', 'POST'])
def knowledge_list(page=0):
    if page == 0:
        page = 1
    knowledges = Knowledge.query.order_by(Knowledge.create_time.desc()).paginate(page=page, per_page=10)
    return render_template('ask/list_knowledge.html', kls=knowledges)

@ask.route('/disease/list', methods=['GET', 'POST'])
def disease_list():
    diseases = db.session.query(Disease.name).all()
    names = [d[0] for d in diseases if d and d[0]]
    if request.method == 'POST':
        search_name = (request.form.get('search') or '').strip()
        if not search_name:
            return render_template('ask/disease.html', names=names)
        result = Disease.query.filter(
            or_(Disease.name.like("%" + search_name + "%"), Disease.alias.like("%" + search_name + "%"))).first()
        return render_template('ask/disease.html', names=names, result=result, search_name=search_name)
    return render_template('ask/disease.html', names=names)

@ask.route('/knowledge/<int:knowledge_id>')
def knowledge_detail(knowledge_id):
    knowledge = Knowledge.query.filter_by(id=knowledge_id).first_or_404()
    return render_template('ask/detail_knowledge.html', kl=knowledge)

@ask.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        form_type = (request.form.get('form_type') or '').strip()
        if form_type == 'basic':
            username = (request.form.get('username') or '').strip()
            email = (request.form.get('email') or '').strip()
            if not username:
                flash('用户名不能为空。')
                return redirect(url_for('ask.profile'))
            if len(username) > 32:
                flash('用户名长度不能超过 32 位。')
                return redirect(url_for('ask.profile'))
            if not email:
                flash('邮箱不能为空。')
                return redirect(url_for('ask.profile'))
            if len(email) > 64:
                flash('邮箱长度不能超过 64 位。')
                return redirect(url_for('ask.profile'))
            if not re.match(r'^[^\s]+@[^\s]+\.[^\s]+$', email):
                flash('邮箱格式不正确。')
                return redirect(url_for('ask.profile'))
            existed = User.query.filter(User.username == username, User.id != current_user.id).first()
            if existed:
                flash('该用户名已被占用，请更换。')
                return redirect(url_for('ask.profile'))
            existed = User.query.filter(User.email == email, User.id != current_user.id).first()
            if existed:
                flash('该邮箱已被占用，请更换。')
                return redirect(url_for('ask.profile'))
            if username == current_user.username and email == current_user.email:
                flash('未检测到信息变更。')
                return redirect(url_for('ask.profile'))
            current_user.username = username
            current_user.email = email
            try:
                db.session.commit()
                flash('个人信息已更新。')
            except IntegrityError:
                db.session.rollback()
                flash('更新失败：用户名或邮箱已存在。')
            except Exception as e:
                db.session.rollback()
                current_app.logger.exception(e)
                flash('更新失败，请稍后重试。')
            return redirect(url_for('ask.profile'))
        if form_type == 'password':
            current_password = (request.form.get('current_password') or '').strip()
            new_password = (request.form.get('new_password') or '').strip()
            confirm_password = (request.form.get('confirm_password') or '').strip()
            if not current_password or not new_password or not confirm_password:
                flash('请完整填写密码相关字段。')
                return redirect(url_for('ask.profile'))
            if not current_user.verify_password(current_password):
                flash('当前密码不正确。')
                return redirect(url_for('ask.profile'))
            if len(new_password) < 6 or len(new_password) > 16:
                flash('新密码长度必须为 6~16 位。')
                return redirect(url_for('ask.profile'))
            if new_password != confirm_password:
                flash('两次输入的新密码不一致。')
                return redirect(url_for('ask.profile'))
            current_user.set_password(new_password)
            try:
                db.session.commit()
                flash('密码修改成功。')
            except Exception as e:
                db.session.rollback()
                current_app.logger.exception(e)
                flash('密码修改失败，请稍后重试。')
            return redirect(url_for('ask.profile'))
    my_questions = Question.query.filter_by(author_id=current_user.id).order_by(Question.create_time.desc()).limit(10).all()
    my_answers = Answer.query.filter_by(author_id=current_user.id).order_by(Answer.create_time.desc()).limit(10).all()
    questions_count = Question.query.filter_by(author_id=current_user.id).count()
    answers_count = Answer.query.filter_by(author_id=current_user.id).count()
    return render_template('ask/profile.html',
                           my_questions=my_questions,
                           my_answers=my_answers,
                           questions_count=questions_count,
                           answers_count=answers_count)