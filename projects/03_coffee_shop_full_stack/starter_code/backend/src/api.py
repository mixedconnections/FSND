import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['GET'])
def get_drinks():
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in Drink.query.all()]
    })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth("get:drinks-detail")
def get_drinks_details(payload):
    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in Drink.query.all()]
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    body = request.get_json()
    if not body:
        abort(422)

    title = body.get('title', None)
    recipe = body.get('recipe', None)

    try:
        # create the drink
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
        new_drink = Drink.query.filter_by(id=drink.id).first()

        return jsonify({
            'success': True,
            'drinks': new_drink.long()
        })

    except:
        abort(422)

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

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, drink_id):
    body = request.get_json()

    title = body.get('title', None)
    recipe = body.get('recipe', None)

    try:
        drink = Drink.query.get(drink_id)

        if not drink:
            abort(404)

        if title is not None:
            drink.title = title

        if recipe is not None:
            drink.recipe = json.dumps(recipe)

        drink.update()

        drink_updated = Drink.query.filter_by(id=drink_id).first()

        return jsonify({
            'success': True,
            'drinks': drink_updated.long()
        })

    except:
        abort(422)

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
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    try:
        drink = Drink.query.get(drink_id)
        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink_id
        })

    except:
        abort(422)

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
@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify(e.error), e.status_code
