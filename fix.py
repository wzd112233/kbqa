from app.app import app
from app.extensions import db

# 🔥 强制删除旧表 + 重建全新的表（彻底解决字段不匹配问题）
with app.app_context():
    db.drop_all()    # 删除所有旧表
    db.create_all()  # 创建全新、结构正确的表
    print("✅ 所有数据库表已重置并创建成功！")

# 启动服务
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    # 12345