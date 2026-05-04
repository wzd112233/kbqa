from app.app import app
# 启动 Flask 服务
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)