import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, PATCH, POST, DELETE, OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        formatted_categories = [c.format() for c in categories]
        return jsonify({
            "success": True,
            "categories": formatted_categories,
            "total_categories": len(formatted_categories)
        })

    @app.route('/questions', methods=['GET'])
    def get_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        categories = Category.query.all()
        formatted_categories = [c.format() for c in categories]

        questions = Question.query.all()
        formatted_questions = [q.format() for q in questions]
        return jsonify({
            "success": True,
            "questions": formatted_questions[start:end],
            "categories": formatted_categories,
            "total_questions": len(formatted_questions),

        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)

        if question is None:
            abort(404)

        try:
            question.delete()

            return jsonify({
                'success': True,
                'request': question.format()
            })

        except BaseException:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_new_question():
        body = request.get_json()

        try:
            answer = body.get('answer', None)
            question = body.get('question', None)
            difficulty = body.get('difficult', None)
            category = body.get('category', None)

            question = Question(
                question=question, answer=answer,
                category=category, difficulty=difficulty)
            question.insert()

            return jsonify({
                'success': True,
                'request': question.format()
            })

        except BaseException:
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        search_term = request.json['searchTerm']
        search_results = Question.query.filter(
            Question.question.ilike('%' + search_term + '%')).all()
        formatted_search_results = [r.format() for r in search_results]
        return jsonify({
            "success": True,
            "questions": formatted_search_results,
            "total_questions": len(formatted_search_results)
        })

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_category_questions(category_id):
        category_id = str(category_id)
        questions = Question.query.filter_by(category=category_id).all()
        formatted_questions = [q.format() for q in questions]
        return jsonify({
            "success": True,
            "questions": formatted_questions,
            "total_questions": len(formatted_questions),
            "currentCategory": category_id
        })

    @app.route('/play', methods=['POST'])
    def play():

        category_id = str(
            request.json['quizCategory']) if 'quizCategory' in request.json else None
        previous_question_ids = (request.json['previousQuestions']
                                 if 'previousQuestions' in request.json
                                 else None)

        choices = (
            Question.query.filter(
                Question.id.notin_(previous_question_ids)).filter(
                Question.category == category_id).all() if category_id and previous_question_ids else Question.query.filter(
                Question.id.notin_(previous_question_ids)).all() if previous_question_ids else Question.query.filter(
                    Question.category == category_id).all() if category_id else Question.query.all())

        if len(choices) > 0:
            selected_question = random.choice(choices)
            formatted_question = selected_question.format()
            return jsonify({
                "success": True,
                "question": formatted_question,
            })

        return jsonify({
            "success": True,
            "question": False,
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Check input values"
        }), 422

    return app
