#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session, abort
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'a\xdb\xd2\x13\x93\xc1\xe9\x97\xef2\xe3\x004U\xd1Z'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


class ClearSession(Resource):
    def delete(self):
        session.clear()
        return '', 204
    
class IndexArticle(Resource):
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):
    def get(self, id):
        session['page_views'] = session.get('page_views', 0) + 1

        if session['page_views'] <= 3:
            article = Article.query.filter_by(id=id).first()
            if article:
                return jsonify(article.to_dict()), 200
            else:
                return {'message': 'Article not found'}, 404
        else:
            return {'message': 'Maximum pageview limit reached'}, 401
            
    @app.route('/login', methods=['POST'])
    def login():
        data = request.json
        username = data.get('username')

        if not username:
            abort(400, description='Username is required.')

        user = User.query.filter_by(username=username).first()

        if not user:
            abort(404, description='User not found.')

        # Simulate login by storing user_id in session
        session['user_id'] = user.id

        # Return serialized user data in JSON response
        return jsonify(user.serialize()), 200

    @app.route('/logout', methods=['DELETE'])
    def logout():
        session.pop('user_id', None)
        return '', 204

    @app.route('/check_session', methods=['GET'])
    def check_session():
        if 'user_id' not in session:
            return jsonify({}), 401  

        user_id = session['user_id']
        user = db.session.query(User).get(user_id)

        if not user:
            abort(404, description='User not found.')

        return jsonify(user.serialize()), 200

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
