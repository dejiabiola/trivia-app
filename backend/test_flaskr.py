import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = os.getenv("DB_NAME", "trivia_test")
        self.database_path = "postgresql://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "How many bottles of wine would get an average cow drunk?",
            "answer": "Two bottles",
            "difficulty": 3,
            "category": 1
        }

        self.new_invalid_question = {
            "question": None,
            "answer": "Two bottles",
            "difficulty": 3,
            "category": 1
        }

        self.general_quiz = {
            'previous_questions': [],
            'quiz_category': {
                'id': 0,
                'type': 'null'
            },
        }
        self.specific_quiz = {
            'previous_questions': [],
            'quiz_category': {
                'id': 2,
                'type': 'Art'
            },
        }

        self.invalid_quiz = {
            'quiz_category': {
                'id': 2,
                'type': 'Art'
            },
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        """Test that the get category function works successfully"""
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(data["categories"], dict))
        self.assertTrue(data["total_categories"])
        self.assertEqual(data["success"], True)

    def test_404_get_categories_empty(self):
        """Test that the get_categories method returns 404 when no categories are defined"""
        pass

    def test_get_paginated_questions(self):
        """Test that endpoint to get questions in pagination works correctly"""
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(isinstance(data["questions"], list))
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["categories"])
        self.assertTrue(isinstance(data["categories"], dict))
        self.assertEqual(data["current_category"], "")

    def test_404_get_questions_beyond_valid_page(self):
        """Test that endpoint sends 404 if request for questions is not valid"""
        response = self.client().get('/questions?page=10000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_delete_question(self):
        """Test that endpoint to delete a question works correctly"""
        response = self.client().delete('/questions/9')
        data = json.loads(response.data)

        question = Question.query.filter(Question.id == 9).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 9)
        self.assertEqual(question, None)

    def test_422_if_question_does_not_exist(self):
        """Test that end point sends formatted message if question does not exist"""
        response = self.client().delete('/questions/10000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable entity")

    def test_search_question(self):
        """Test that endpoint to search a question works correctly"""
        response = self.client().post(
            '/questions', json={"searchTerm": "largest"})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(isinstance(data["questions"], list))
        self.assertTrue(data["total_questions"])

    def test_search_question_with_unknown_value(self):
        """Test that endpoint to search a question works correctly if value is unknown"""
        response = self.client().post(
            '/questions', json={"searchTerm": "sakdhfkasdflkhsdfasf"})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertFalse(data["questions"])
        self.assertTrue(isinstance(data["questions"], list))
        self.assertEqual(data["total_questions"], 0)
        self.assertEqual(data["total_questions"], 0)

    def test_create_question(self):
        """Test that endpoint to create a question works correctly"""
        response = self.client().post(
            '/questions', json=self.new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(isinstance(data["questions"], list))
        self.assertTrue(data["total_questions"])
        self.assertEqual(data["new_question"]["question"],
                         self.new_question["question"])
        self.assertEqual(data["new_question"]["answer"],
                         self.new_question["answer"])
        self.assertEqual(data["new_question"]["difficulty"],
                         self.new_question["difficulty"])
        self.assertEqual(data["new_question"]["category"],
                         self.new_question["category"])

    def test_400_bad_request_on_create_question(self):
        """Test endpoint returns 400 error when creating a new question with incomplete request"""
        response = self.client().post(
            '/questions', json=self.new_invalid_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable entity")

    def test_get_question_by_category(self):
        """Test that endpoint to get a question by category works correctly"""
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["current_category"])

    def test_404_invalid_get_question_by_category(self):
        """Test that endpoint returns formatted error message if question by category id is invalid"""
        response = self.client().get('/categories/1000/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable entity")

    def test_play_quizzes_all_categories(self):
        """Test that endpoint to play quizzes for all categories works correctly"""
        response = self.client().post('/quizzes', json=self.general_quiz)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_play_quizzes_specific_categories(self):
        """Test that endpoint to play quizzes for specific category works correctly"""
        response = self.client().post('/quizzes', json=self.specific_quiz)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])
        self.assertEqual(data["question"]["category"],
                         self.specific_quiz["quiz_category"]["id"])

    def test_422_quizzes_error(self):
        """Test that returns error when making a request to the quizzes endpoint with invalid parameters."""
        response = self.client().post('/quizzes', json=self.invalid_quiz)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["message"], "unprocessable entity")

    def test_create_category(self):
        """Test that endpoint to create category works correctly"""
        response = self.client().post(
            '/categories', json={"type": "Metaverse"})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["category"])
        self.assertEqual(data["category"]["type"], "Metaverse")

    def test_422_create_category_error(self):
        """Test that returns error when making a post request to the categories endpoint with invalid parameters."""
        response = self.client().post('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["message"], "unprocessable entity")

    def test_404_invalid_endpoint(self):
        """Test that app returns 404 when endpoint is invalid"""
        response = self.client().post('/invalid')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
