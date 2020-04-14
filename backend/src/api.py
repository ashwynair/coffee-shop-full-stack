import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db, db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''

# db_drop_and_create_all()


# ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks():
    """
    Public endpoint. Contains only the drink.short() data representation
    :return: Status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
    or appropriate status code indicating reason for failure
    """
    drinks = list(map(Drink.short, Drink.query.all()))
    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    """
    Requires get:drinks-detail permissions. Contains the drink.long() data representation
    :return: status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
    or appropriate status code indicating reason for failure
    """
    drinks = list(map(Drink.long, Drink.query.all()))
    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks():
    """
    Requires post:drinks permissions. Creates a new row in the drinks table.
    Response contains the drink.long() data representation
    :return: Status code 200 and json {"success": True, "drinks": drink} where drink an array containing
    only the newly created drink or appropriate status code indicating reason for failure
    """
    data = dict(request.get_json())
    if not all(key in data.keys() for key in ("id", "title", "recipe")):
        abort(422)
    error = False
    try:
        drink = Drink(
            id=data["id"],
            title=data["title"],
            recipe=data["recipe"],
        )
        drink.insert()
    except Exception:
        error = True
        db.session.rollback()
        print(exc.info())
    finally:
        db.session.close()
        if error:
            abort(500)
        else:
            result = {
                "success": True,
                "drinks": drink.long()
            }
            return jsonify(result)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

## Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
