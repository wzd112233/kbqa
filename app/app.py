from flask import Flask, redirect, url_for
from .config import FlaskConfig
from .extensions import db, login_manager

app = Flask(__name__)
app.config.from_object(FlaskConfig)

db.init_app(app)

login_manager.login_view = 'ask.login'
login_manager.refresh_view = 'ask.login'
login_manager.login_message = '请先登录！'
login_manager.session_protection = 'basic'
login_manager.init_app(app=app)

@login_manager.user_loader
def load_user(id):
    from .auth.models import User
    return User.query.get(int(id))

# 在应用上下文里导入蓝图，避免循环导入
with app.app_context():
    from .ask import ask
    from .auth import auth
    app.register_blueprint(ask)
    app.register_blueprint(auth)

# 添加根路由，访问 / 自动跳转到首页
@app.route('/')
def index():
    # 重定向到 ask 蓝图的首页
    return redirect(url_for('ask.index'))