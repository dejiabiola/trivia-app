import os
import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    return questions[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow_Headers",
                             "Content-Type, Authorization, true")
        response.headers.add("Access-Control-Allow-Methods",
                             "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        return response

    @app.route('/categories')
    def get_categories():
        try:
            categories = Category.query.all()

            if len(categories) == 0:
                abort(422)

            formatted_categories = {}
            for category in categories:
                formatted_categories[category.id] = category.type

            return jsonify({
                "success": True,
                "categories": formatted_categories,
                "total_categories": len(categories)
            })
        except Exception as error:
            print(error)
            abort(422)

    @app.route('/categories', methods=["POST"])
    def create_category():
        try:
            body = request.get_json()

            category_type = body.get('type', None)
            category = Category(type=category_type)

            category.insert()

            return jsonify({
                "success": True,
                "category": category.format()
            })
        except Exception as error:
            print(error)
            abort(422)

    @app.route('/questions')
    def get_questions():
        try:
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            categories = Category.query.all()

            if len(current_questions) == 0:
                abort(422)

            return jsonify({
                "success": True,
                "questions": current_questions,
                "total_questions": len(selection),
                "current_category": "",
                "categories": {cat.id: cat.type for cat in categories}
            })
        except Exception as error:
            print(error)
            abort(422)

    @app.route('/questions/<int:question_id>', methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                "success": True,
                "deleted": question_id,
            })
        except Exception as error:
            print(error)
            abort(422)

    @app.route('/questions/create', methods=["POST"])
    def create_questions():
        body = request.get_json()
        question = body.get('question', None)
        answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)

        try:
            if None in [question, answer, difficulty, category]:
                abort(422)
            else:
                question = Question(
                    question=question, answer=answer,
                    difficulty=difficulty, category=category)
                question.insert()
                questions = Question.query.all()
                formatted_questions = [question.format()
                                       for question in questions]
                return jsonify({
                    "success": True,
                    "new_question": question.format(),
                    "questions": formatted_questions,
                    "total_questions": len(questions)
                })

        except Exception as error:
            print(error)
            abort(422)

    @app.route('/questions/search', methods=["POST"])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        try:
            questions = Question.query.order_by(Question.id).filter(
                Question.question.ilike('%{}%'.format(search_term))).all()

            formatted_questions = [question.format()
                                   for question in questions]

            return jsonify({
                "success": True,
                "questions": formatted_questions,
                "total_questions": len(questions),
                "current_category": "",
            })

        except Exception as error:
            print(error)
            abort(422)

    @app.route('/categories/<string:category_id>/questions', methods=["GET"])
    def get_questions_by_categories(category_id):
        try:
            category = Category.query.get(category_id)
            questions = Question.query.filter(
                Question.category == category_id).all()
            formatted_questions = [question.format() for question in questions]

            if len(formatted_questions) == 0 or category is None:
                abort(422)

            return jsonify({
                "success": True,
                "questions": formatted_questions,
                "total_questions": len(formatted_questions),
                "current_category": category_id
            })
        except Exception as error:
            print(error)
            abort(422)

    @app.route('/quizzes', methods=["POST"])
    def play_quizzes():
        try:
            body = request.get_json()
            previous_questions = body.get('previous_questions', None)
            quiz_category = body.get('quiz_category', None)

            if quiz_category is None or previous_questions is None:
                abort(422)

            else:

                if quiz_category["id"] == 0:
                    questions = Question.query.all()
                else:
                    questions = Question.query.filter(
                        Question.category == str(quiz_category["id"])).all()

                if len(questions) == len(previous_questions):
                    question = None
                else:
                    question = random.choice(questions)
                    while question.id in previous_questions:
                        question = random.choice(questions)

                return jsonify({
                    "success": True,
                    "question": question.format(),
                })
        except Exception as error:
            print(error)
            abort(422)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable entity"
        }), 422

    return app
