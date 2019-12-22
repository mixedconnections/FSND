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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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
    def test_404(self):
        res = self.client().get('/foobar')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    def test_categories_all(self):
        res = self.client().get('/categories')
        self.assertEqual(res.status_code, 200)

    def test_category_by_id(self):
        res = self.client().get('/categories/1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['type'], 'Science')

    def test_questions_by_id(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['current_category'], 1)

    def test_questions_paginated(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['current_category'])
        self.assertTrue(data['categories'])

    def test_questions_by_id_fail(self):
        res = self.client().get('/categories/500/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)


    def test_question_create(self):
        res = self.client().post('/questions/create', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertEqual(data['new_question']['category'], 1)

    def test_search_questions(self):
        res = self.client().post('/questions/search', json={'search':'Hematology is a branch of medicine involving the study of what?'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)

    def test_search_questions_fail(self):
        res = self.client().post('/questions/search', json={'search':'foobar'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 0)

    def test_play_all(self):
        res = self.client().post('/play', json={'category': None})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['current_question']), 5)


    def test_play_by_category(self):
        res = self.client().post('/play', json={'category': 3, 'previous_questions':[1,3]})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 3)
        self.assertEqual(len(data['current_question']), 5)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
