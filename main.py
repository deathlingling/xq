from datetime import datetime

from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weixin.db'
app.config['SECRET_KEY'] = 'wqw'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class WeixinUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    wechat_id = db.Column(db.String(120), unique=True, nullable=False)
    location = db.Column(db.String(120), nullable=True)
    entry_time = db.Column(db.DateTime, default=datetime.now())
    gender = db.Column(db.String(10), nullable=True)  # 性别
    drawn_times = db.Column(db.Integer, default=0)  # 被抽次数
    jf = db.Column(db.Integer, default=1)  # 积分


def sj(xb):
    random_user = WeixinUser.query.filter(WeixinUser.gender == f'{xb}').order_by(func.random()).first()
    user_data = {}
    if random_user:
        user_data = {
            'name': random_user.name,
            'wechat_id': random_user.wechat_id,
            'location': random_user.location,
            'gender': random_user.gender,  # 添加性别字段
            'drawn_times': random_user.drawn_times  # 添加被抽次数字段
        }
        random_user.drawn_times += 1  # 增加被抽次数
        db.session.commit()  # 提交数据库会话以保存更改
    return user_data


@app.route('/', methods=['GET', 'POST'])
def get_users():
    if request.method == 'POST':
        try:
            data = request.json
            if data['gender'] not in ['男', '女']:
                return jsonify({'message': 'Invalid gender'}), 400
            new_user = WeixinUser(name=data['name'], wechat_id=data['wechat_id'], location=data['location'],
                                  gender=data['gender'])
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'消息': '用户添加成功'}), 201
        except Exception as e:
            return jsonify({'消息': 'An error occurred: ' + str(e)}), 500

    return render_template('home.html')


@app.route('/lottery', methods=['POST'])
def lottery():
    data = request.json
    if data['gender'] not in ['男', '女']:
        return jsonify({'消息': 'Invalid gender'}), 400

    return sj(data['gender'])


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True)
