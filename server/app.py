from flask import Flask, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'a\xdb\xd2\x13\x93\xc1\xe9\x97\xef2\xe3\x004U\xd1Z'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json_compact = False

db.init_app(app)
migrate = Migrate(app, db)

api = Api(app, catch_all_404s=True, errors={
    'Exception': {'message': 'An error occurred', 'status': 500}
})

class ClearSession(Resource):
    def get(self):
        session.clear()
        return '', 204

class IndexArticle(Resource):
    def get(self):
        articles = Article.query.all()
        return jsonify([article.to_dict() for article in articles]), 200

class ShowArticle(Resource):
    def get(self, id):
        session['page_views'] = session.get('page_views', 0) + 1
        if session['page_views'] <= 3:
            article = Article.query.get_or_404(id)
            return jsonify(article.to_dict()), 200
        return jsonify({'message': 'Maximum pageview limit reached'}), 401

class Login(Resource):
    def post(self):
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No JSON data provided"}), 400
            
            username = data.get('username')
            if not username:
                return jsonify({"error": "Username not provided"}), 400
            
            user = User.query.filter_by(username=username).first()
            if user:
                session['user_id'] = user.id
                return jsonify({
                    "id": user.id,
                    "username": user.username
                }), 200
            else:
                return jsonify({"error": "User not found"}), 404
        except Exception as e:
            return jsonify({"error": "An error occurred during login"}), 500


class Logout(Resource):
    def delete(self):
        session.pop('user_id', None)
        return '', 204

class CheckSession(Resource):
    def get(self):
        try:
            user_id = session.get('user_id')
            if user_id:
                user = User.query.get(user_id)
                if user:
                    return jsonify(user.to_dict()), 200
                else:
                    return jsonify({"error": "User not found"}), 404
            return jsonify({"error": "User not logged in"}), 401
        except Exception as e:
            return jsonify({"error": str(e)}), 500

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
