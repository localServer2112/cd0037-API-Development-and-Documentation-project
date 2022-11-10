import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from collections.abc import Mapping
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    
    cors = CORS(app, resources={r"/*": {"origins": "*"}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTION')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=["GET"])
    def get_category():
        categories = Category.query.order_by(Category.id).all()
        # cat = [category.format() for category in categories]
        return jsonify(
            {
                    "success": True,
                   #"categories": cat,
                    "categories": {category.id: category.type for category in categories},  
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
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        
        
        if len(current_questions) == 0:
             abort(404)

        categories = Category.query.order_by(Category.id).all()
         #print(categories)
        cat = [category.format() for category in categories]

        return jsonify(
             {
                 "success": True,
                 "questions": current_questions,
                 "total_questions": len(selection),
                  #"categories": cat,
                'categories': {category.id: category.type for category in categories},
            }
         )
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(q_id):
        try:
            question = Question.query.get(q_id)
            if (question is None):
              print("not working")
              abort(404)
            
            
            question.delete()

            result = Question.query.order_by(Question.id).all()
            q_current = paginate_questions(request, result)
            q_total = Question.query.all()
            return jsonify(
                {
                    "success": True,
                    "deleted": q_id,
                    "questions": q_current,
                    "total_questions": len(q_total),
                }
            )
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
    def add_question():

      body = request.get_json()
      new_question = body.get("question", None)
      new_answer = body.get("answer", None)
      new_category = body.get("category", None)
      new_diffiulty = body.get("difficulty", None)

      try:
          question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_diffiulty)
          question.insert()

          selection = Question.query.order_by(Question.id).all()
          current_questions = paginate_questions(request, selection)

          return jsonify(
                {
                    "success": True,
                    "created": question.id,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                }
            )
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
    @app.route("/questions/search", methods=["POST"])
    def search_questions():
       body = request.get_json()

       search = body.get("searchTerm", None)
       selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(search)))
       current_questions = paginate_questions(request, selection)

       return jsonify(
                    {
                        "success": True,
                        "questions": current_questions,
                        "total_questions": len(selection.all()),
                    }
                )
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def questions_by_category(category_id):
      
        try:
            category = Category.query.filter_by(id=category_id).one_or_none()

            if (category) is None:
                abort(404)

            result = Question.query.filter_by(category=category.id).order_by(Question.id).all()
            q_current = paginate_questions(request, result)

            return jsonify(
                    {
                        "success": True,
                        "category": category.type,
                        "questions": q_current,
                        "total_questions": len(result),
                    }
                )
        except:
            abort(422)
        
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
    @app.route("/quizzes", methods=["POST"])
    def play_game():

      body = request.get_json()
      quiz_category = body.get("quiz_category", None)
      q_previous = body.get("previous_questions", None)

      if ((quiz_category is None) or (q_previous is None)):
        abort(400)
      else:
        c_id = quiz_category['id']
      try:
        if c_id == 0:
            r_questions = Question.query.filter(Question.id.notin_(q_previous)).all()
        else:
            r_questions = Question.query.filter(Question.category==c_id,Question.id.notin_(q_previous)).all()
        
        if len(r_questions) > 0:
            n_question = r_questions[random.randrange(0,len(r_questions),1)]
            return jsonify({
               "success": True,
               "question" : n_question.format()
            })
        else :
         return jsonify(
          {
            "success": True
          })
      except:
         abort(422)
    


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
                "success": False, 
                "error": 404,
                "message": "Not found"
                }), 404

    @app.errorhandler(400)
    def bad_request(error):
            return jsonify({
                "success": False, 
                "error": 400,
                "message": "bad request"
                }), 400

    @app.errorhandler(500)
    def not_found(error):
        return jsonify({
                "success": False, 
                "error": 500,
                "message": "Internal server error"
                }), 500


    @app.errorhandler(422)
    def unproccesable(error):
        return jsonify({
                "success": False, 
                "error": 422,
                "message": "unproccessable"
                }), 422
  
    return app

