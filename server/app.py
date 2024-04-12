from flask import Flask, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User  # Importing the required models

# Create the Flask application
app = Flask(__name__)

# Set the secret key for sessions
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'

# Set the database URI and other configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize the database and migrations
db.init_app(app)
migrate = Migrate(app, db)

# Create the API
api = Api(app)

# Resource to clear session data
class ClearSession(Resource):
    def delete(self):
        session.clear()  # Clear the entire session
        return '', 204  # Return 204 (No Content)

# Resource for indexing articles
class IndexArticle(Resource):
    def get(self):
        articles = Article.query.all()
        return jsonify([article.to_dict() for article in articles]), 200

# Resource for showing an article by ID
class ShowArticle(Resource):
    def get(self, id):
        # Check page views in session
        session['page_views'] = session.get('page_views', 0) + 1
        
        if session['page_views'] <= 3:
            article = Article.query.get_or_404(id)
            return jsonify(article.to_dict()), 200
        
        return jsonify({'message': 'Maximum pageview limit reached'}), 401

# Resource for logging in a user
class Login(Resource):
    def post(self):
        try:
            data = request.get_json()
            username = data.get('username')
            
            # Find the user by username
            user = User.query.filter_by(username=username).first()
            
            if user:
                session['user_id'] = user.id
                return jsonify(user.to_dict()), 200
            else:
                return jsonify({"error": "User not found"}), 404
        except Exception as e:
            # Return JSON error response with 500 status code
            return jsonify({"error": str(e)}), 500

# Resource for logging out a user
class Logout(Resource):
    def delete(self):
        session.pop('user_id', None)
        return '', 204

# Resource for checking session for user login status
class CheckSession(Resource):
    def get(self):
        try:
            user_id = session.get('user_id')
            
            if user_id:
                # Find the user by ID
                user = User.query.get(user_id)
                if user:
                    return jsonify(user.to_dict()), 200
                else:
                    return jsonify({"error": "User not found"}), 404
            
            return jsonify({"error": "User not logged in"}), 401
        except Exception as e:
            # Return JSON error response with 500 status code
            return jsonify({"error": str(e)}), 500

# Register the resources with the API
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

# Start the Flask application
if __name__ == '__main__':
    app.run(port=5555, debug=True)
