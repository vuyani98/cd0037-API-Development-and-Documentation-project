
from logging import captureWarnings
import os
import json
from dotenv import load_dotenv
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from random import *

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*" : {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    #enabling cross-domain/cross-origin 
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET, PUT, POST, DELETE, OPTIONS")

        return response

    #gets catergories and returns object version    
    def get_all_categories():
        categories = Category.query.all()
        return {category.id: category.type for category in categories}
 
    # returns paginated questions
    def paginate_questions(request, questions):
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        paginated_questions = [question.format() for question in questions]

        return paginated_questions[start:end]

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=['GET'])
    def get_categories():

        try:
            categories = get_all_categories()

            if categories is None:
                    abort(404)
        
        except:
            abort(400)

        return jsonify({
            "success": True,
            "categories": categories
        })



    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions", methods=["GET"])
    def get_questions():

        try:
            questions = Question.query.order_by(Question.id).all()
            paginated_questions = paginate_questions(request, questions)
            categories = get_all_categories()
            
            
            if len(paginated_questions) == 0 or categories is None:
                abort(404)


        except:
            abort(400)
        
        return jsonify({
            "success" : True,
            "questions" : paginated_questions,
            "totalQuestions" : len(questions),
            "categories" : categories
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):

        
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is None:
                abort(404)

            question.delete()
            return jsonify({
                "success" : True,
                "deleted_question" : question_id
            })     

        except:
            abort(422)


    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def add_new():
        body = request.get_json()

        #Handling seach term
        if (body.get("searchTerm")):
            try:
                searchTerm = body.get("searchTerm")
                questions = Question.query.filter(Question.question.ilike(f'%{searchTerm}%'))
                paginated_questions = paginate_questions(request, questions)

                if questions is None:
                    abort(404) 

            except:
                abort(400)

            return jsonify({
                "success": True,
                "questions": paginated_questions,
                "totalQuestions": len(paginated_questions)
            })

        else:
            new_question = body.get("question", None)
            answer = body.get("answer", None)
            difficulty = body.get("difficult", None)
            category = body.get("category", None)

            try:
                question = Question(question=new_question, answer=answer, difficulty=difficulty, category=category)
                question.insert()
                print(question)

                return jsonify({
                    "success" : True
                })
            except:
                abort(422)



    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:id>/questions", methods=["GET"])
    def category_specific_questions(id):
        
        try:
            questions = Question.query.filter(Question.category == id)
            paginated_questions = paginate_questions(request, questions)
            currentCategory = Category.query.filter(Category.id==id).one_or_none()

            if questions is None:
                abort(404)      
        except:
            abort(400)

        return jsonify({
            "success" : True,
            "questions" : paginated_questions,
            "totalQuestions": len(paginated_questions),
            "currentCategory": currentCategory.type
            })
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/quizzes', methods=['POST'])
    def get_puzzles():
        pass

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app

