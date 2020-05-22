import os
from flask import Flask, request, jsonify, abort
import json
from flask_cors import CORS
from sys import exc_info

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


db_drop_and_create_all()


# ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks(*args, **kwargs):
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
def get_drinks_detail(*args, **kwargs):
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
def add_drinks(*args, **kwargs):
    """
    Requires post:drinks permissions. Creates a new row in the drinks table.
    Response contains the drink.long() data representation
    :return: Status code 200 and json {"success": True, "drinks": drink} where drink an array containing
    only the newly created drink or appropriate status code indicating reason for failure
    """
    data = dict(request.get_json())
    if not all(key in data.keys() for key in ("title", "recipe")):
        abort(422)
    error = False
    try:
        recipe = data.get("recipe")
        if not isinstance(recipe, list):
            recipe = [recipe]
        new_drink = Drink(
            title=data["title"],
            recipe=json.dumps(recipe)
        )
        new_drink.insert()
        result = {
            "success": True,
            "drinks": new_drink.long()
        }
        return jsonify(result)
    except Exception:
        error = True
        db.session.rollback()
        print(exc_info())
    finally:
        db.session.close()
        if error:
            abort(500)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(*args, **kwargs):
    """
    Responds with a 400 error if <drink_id> is not provided by client
    Responds with a 404 error if drink corresponding <drink_id> is not found
    Updates the corresponding row for <drink_id>
    Requires the 'patch:drinks' permission
    Contains the drink.long() data representation in response
    :param drink_id: Integer for id of drink
    :return: Status code 200 and JSON {"success": True, "drinks": drink}, where drink an array containing only
    the updated drink or appropriate status code indicating reason for failure
    """
    drink_id = kwargs.get("drink_id", None)
    if not drink_id:
        abort(400)
    data = dict(request.get_json())
    title = data.get("title", None)
    recipe = data.get("recipe", None)
    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404)
    error = False
    try:
        if title:
            drink.title = title
        if recipe:
            if not isinstance(recipe, list):
                recipe = [recipe]
            drink.recipe = json.dumps(recipe)
        drink.update()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    except Exception:
        error = True
        db.session.rollback()
        print(exc_info())
    finally:
        db.session.close()
        if error:
            abort(500)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(*args, **kwargs):
    """
    Responds with a 400 error if <drink_id> is not provided by client
    Responds with a 404 error if drink corresponding <drink_id> is not found
    Deletes the corresponding row for <drink_id>
    Requires the 'delete:drinks' permission
    :param drink_id: Integer for id of drink
    :return: Status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
    or appropriate status code indicating reason for failure
    """
    drink_id = kwargs.get("drink_id", None)
    if not drink_id:
        abort(400)
    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404)
    error = False
    try:
        drink.delete()
        return jsonify({
            "success": True,
            "delete": drink_id
        })
    except Exception:
        error = True
        db.session.rollback()
        print(exc_info())
    finally:
        db.session.close()
        if error:
            abort(500)


# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400
