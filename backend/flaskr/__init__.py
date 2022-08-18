import os
import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

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

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app)

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow_Headers",
                             "Content-Type, Authorization, true")
        response.headers.add("Access-Control-Allow-Methods",
                             "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        return response

    '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()

        if len(categories) == 0:
            abort(404)

        formatted_categories = {}
        for category in categories:
            formatted_categories[category.id] = category.type

        return jsonify({
            "success": True,
            "categories": formatted_categories,
            "total_categories": len(categories)
        })

    '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
    @app.route('/questions')
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        categories = Category.query.all()

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "questions": current_questions,
            "total_questions": len(selection),
            "current_category": "",
            "categories": {category.id: category.type for category in categories}
        })

    '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
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
        except:
            abort(422)

    '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
    '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
    @app.route('/questions', methods=["POST"])
    def search_questions():
        body = request.get_json()

        search_term = body.get('searchTerm', None)
        question = body.get('question', None)
        answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)

        try:
            if search_term is not None:
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
            else:
                if None in [question, answer, difficulty, category]:
                    abort(400)
                    return
                else:
                    question = Question(
                        question=question, answer=answer, difficulty=difficulty, category=category)
                    question.insert()
                    questions = Question.query.all()
                    formatted_questions = paginate_questions(
                        request, questions)
                    return jsonify({
                        "success": True,
                        "new_question": question.format(),
                        "questions": formatted_questions,
                        "total_questions": len(questions)
                    })

        except:
            abort(422)

    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
    @app.route('/categories/<string:category_id>/questions', methods=["GET"])
    def get_questions_by_categories(category_id):
        try:
            category = Category.query.get(category_id)
            questions = Question.query.filter(
                Question.category == category_id).all()
            formatted_questions = [question.format() for question in questions]

            if len(formatted_questions) == 0 or category is None:
                abort(404)

            return jsonify({
                "success": True,
                "questions": formatted_questions,
                "total_questions": len(formatted_questions),
                "current_category": category_id
            })
        except:
            abort(422)

    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
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
        except:
            abort(422)

    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
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
