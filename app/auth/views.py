#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Blueprint, request, redirect, current_app, url_for, jsonify, render_template
from flask_login import login_required, login_user, logout_user
from sqlalchemy import or_

from .models import User
from ..extensions import db

auth = Blueprint('auth', __name__)

@auth.route('/login/', methods=['POST'])
def login_users():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        u = User.query.filter_by(username=username).first()
        if u and u.verify_password(password):
            login_user(u)
            return jsonify({'success': True, 'redirect_url': url_for('ask.index')})
        else:
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
    except Exception as e:
        # 打印完整错误
        current_app.logger.error(f"登录错误: {str(e)}")
        return jsonify({'success': False, 'message': '服务器错误'}), 500

@auth.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@auth.route('/signup/', methods=['POST'])
def signup_user():
    try:
        username = request.json['username']
        email = request.json.get('email')
        password = request.json['password']

        u = User.query.filter(or_(User.username == username, User.email == email)).first()
        if u:
            return jsonify(status='error', message='已经存在该用户！')
        
        # 创建用户
        new_user = User()
        new_user.username = username
        new_user.email = email
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        return jsonify(status='success', message='恭喜你，注册成功了！')
        
    except Exception as e:
        # 强制打印详细错误到控制台
        current_app.logger.error(f"注册失败详情: {str(e)}")
        return jsonify(status='error', message='注册失败，请重试！'), 500

@auth.route('/logout', methods=['GET'])
@login_required
def logout_users():
    logout_user()
    return redirect(url_for('ask.index'))