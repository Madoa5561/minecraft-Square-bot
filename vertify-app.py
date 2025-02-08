import uuid
import json
from flask import Flask, request, redirect, render_template, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import re

# Flaskアプリケーションの設定
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///whitelist.db'  # SQLiteデータベース
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemyの初期化
db = SQLAlchemy(app)

# ホワイトリストテーブルのモデル
class Whitelist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mcid = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    added_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# 認証リクエスト用のモデル
class AuthRequest(db.Model):
    uuid = db.Column(db.String(36), primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# DBの初期化
with app.app_context():
    db.create_all()

# allowlist.jsonのパス
ALLOWLIST_JSON_PATH = 'allowlist.json'

# ランダムなUUIDを生成してURLを返すエンドポイント
@app.route('/generate_url_59b22d41-2bc2-b996-fa5d-851ccbf02121', methods=['GET'])
def generate_url():
    random_uuid = str(uuid.uuid4())  # ランダムなUUIDを生成
    ip_address = request.remote_addr
    
    # 新しい認証リクエストを作成
    auth_request = AuthRequest(uuid=random_uuid, ip_address=ip_address)
    db.session.add(auth_request)
    db.session.commit()
    
    return jsonify({"url": 'https://moyashi.xyz/minecraft-app/authenticate/'+random_uuid})

# UUIDによる認証処理
@app.route('/authenticate/<uuid>', methods=['GET', 'POST'])
def authenticate(uuid):
    auth_request = AuthRequest.query.get(uuid)
    
    if not auth_request:
        return "無効なURLです。", 404  # UUIDが見つからない場合
    
    if auth_request.used:
        return "このURLはすでに使用されました。", 400  # 既に使われたURL
    
    if request.method == 'POST':
        # フォームから送信されたMCIDを取得
        mcid = request.form.get('mcid')
        
        if not mcid or not re.match(r'^[a-zA-Z0-9_]+$', mcid):
            return "無効なMinecraft IDです。", 400
        
        # IPアドレスがバンされているかチェック（省略）
        ip_address = request.remote_addr
        
        # ホワイトリストに追加
        new_entry = Whitelist(mcid=mcid, ip_address=ip_address)
        db.session.add(new_entry)
        auth_request.used = True  # URLを無効化
        db.session.commit()

        # allowlist.jsonに新しいMinecraft IDを追加
        add_to_allowlist(mcid)

        return f"{mcid}さんがホワイトリストに追加されました。", 200
    
    # GETリクエストでフォームを表示
    return render_template('authenticate.html', uuid=uuid)

def add_to_allowlist(mcid):
    # 現在のallowlist.jsonを読み込む
    try:
        with open(ALLOWLIST_JSON_PATH, 'r', encoding='utf-8') as f:
            allowlist = json.load(f)
    except FileNotFoundError:
        allowlist = []  # ファイルがない場合は空リスト

    # 新しいMCIDをallowlistに追加
    new_entry = {"name": mcid, "ignoresPlayerLimit": False}
    allowlist.append(new_entry)

    # 更新されたallowlistを保存
    with open(ALLOWLIST_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(allowlist, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    app.run(debug=True,port=7334)
