import os
import unittest
import json
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

dotenv_path = os.path.abspath(os.path.dirname(__file__))
load_dotenv(dotenv_path+'/.env')
database_user = os.getenv('database_username')
database_password = os.getenv('database_password')
database_name = 'trivia_test'
database_host= 'localhost:5432'
database_path = 'postgresql://{}:{}@{}/{}'.format(database_user,database_password,'localhost:5432', database_name)

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = database_path
        #"postgresql://{}:{}@{}/{}'.format(database_user,database_password,database_host, database_name)"
        setup_db(self.app, self.database_path)

        self.new_question = { "question": "Heres a new question string", "answer": "Heres a new answer string", "difficulty": 1, "category": 3 }
        self.bad_question = { "question": "Heres a new question string", "answer": "Heres a new answer string", "difficulty": 1, "category": 1000 }
    
        self.searchTerm = { "searchTerm": "Who" }
        self.quiz_body = { "previous_questions": [2, 4], "quiz_category": { "id" : 5, "type" : "Entertainment"}}
       
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
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    def test_400_get_categories_with_args(self):
        res = self.client().get("/categories?page=1")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad request")     

    
    def test_get_questions(self):
        res = self.client().get("/questions?page=1")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["categories"])
        self.assertTrue(data['totalQuestions'] > 0)

    def test_400_get_questions_outOfrange(self):
        res = self.client().get("/questions?page=2000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad request")     

    def test_delete_question(self):

        question = Question.query.filter(Question.id==18).one_or_none()       
        res = self.client().delete("/questions/18")
        data = json.loads(res.data)
        
        if question is None:
            self.assertEqual(res.status_code, 422)
        
        else:
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data["success"], True)
            self.assertTrue(data["deleted_question"])

        
    def test_404_delete_question_wrong_id(self):
        res = self.client().delete("/questions/h")
        data = json.loads(res.data)

  

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not found")

    def test_422_delete_deleted_question(self):
        res = self.client().delete("/questions/2000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["message"], "Bad request")

    def test_add_new(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
    
    def test_search_term(self):
        res = self.client().post("/questions", json=self.searchTerm)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["totalQuestions"])

    def test_404_search_term_notfound(self):
        res = self.client().post("/questions", json={ "searchTerm" : "890"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not found")

    def test_422_add_term_error(self):
        res = self.client().post("/questions", json=self.bad_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["message"], "Bad request")

    def test_category_specific_questions(self):
        res = self.client().get("/categories/2/questions")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True) 
        self.assertTrue(data["questions"])
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(data["currentCategory"])

    def test_400_category_specific_questions_nonexisting(self):
        res = self.client().get("/categories/20/questions")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad request")

    def test_get_quizzes(self):
        res = self.client().post("/quizzes", json=self.quiz_body)
        data = json.loads(res.data)
    
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True) 
        

    def test_400_get_quizzes_without_body(self):
        res = self.client().post("/quizzes")
        data = json.loads(res.data)
    
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False) 
        self.assertEqual(data["message"], "Bad request")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()