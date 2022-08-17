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
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

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
        response = self.client().delete('/questions/1')
        data = json.loads(response.data)

        question = Question.query.filter(Question.id == 1).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 1)
        self.assertEqual(question, None)

    def test_422_if_question_does_not_exist(self):
        """Test that end point sends formatted message if question does not exist"""
        response = self.client().post('/questions/10000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
