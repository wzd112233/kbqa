from sqlalchemy import Column
from datetime import datetime

from app.extensions import db


class Question(db.Model):
    __tablename__ = 'questions'

    id = Column(db.Integer, primary_key=True)
    title = Column(db.String(128), nullable=False)
    content = Column(db.Text(1024))
    answers_count = Column(db.Integer, default=0)
    create_time = Column(db.DateTime, default=datetime.now())

    author_id = Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    author = db.relationship('User', backref=db.backref('questions', lazy='dynamic'), uselist=False)


class Knowledge(db.Model):
    __tablename__ = 'knowledge'

    id = Column(db.Integer, primary_key=True)
    title = Column(db.String(128), nullable=False)
    content = Column(db.Text(1024))
    answers = Column(db.Text(1024))
    create_time = Column(db.DateTime, default=datetime.now())


class Answer(db.Model):
    __tablename__ = 'answers'

    id = Column(db.Integer, primary_key=True)
    content = Column(db.Text(1024))
    answers_count = Column(db.Integer, default=0)
    create_time = Column(db.DateTime, default=datetime.now())

    author_id = Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    author = db.relationship('User', backref=db.backref('answers', lazy='dynamic'), uselist=False)

    question_id = Column(db.Integer, db.ForeignKey('questions.id'))
    question = db.relationship('Question', backref=db.backref('answers', lazy='dynamic'), uselist=False)


class Comment(db.Model):
    __tablename__ = 'comments'

    id = Column(db.Integer, primary_key=True)
    content = Column(db.Text(1024))
    create_time = Column(db.DateTime, default=datetime.now())

    author_id = Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    author = db.relationship('User', uselist=False)

    answer_id = Column(db.Integer, db.ForeignKey('answers.id'))
    answer = db.relationship("Answer", backref=db.backref('comments', lazy='dynamic'), uselist=False)


class Disease(db.Model):
    __tablename__ = 'disease'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(128))
    alias = Column(db.String(128))
    part = Column(db.String(128))
    age = Column(db.String(128))
    infection = Column(db.String(128))
    insurance = Column(db.String(128))
    department = Column(db.String(128))
    checklist = Column(db.String(128))
    symptom = Column(db.String(128))
    complication = Column(db.String(128))
    treatment = Column(db.String(128))
    drug = Column(db.String(128))
    period = Column(db.String(128))
    rate = Column(db.String(128))
    money = Column(db.String(128))


class Star(db.Model):
    __tablename__ = 'star'  # 数据库中的表名

    id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer, nullable=False)
    ask_id = Column(db.Integer, nullable=False)