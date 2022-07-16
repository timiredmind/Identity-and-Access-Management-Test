import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from http import HTTPStatus
# from ..database.models import db_drop_and_create_all, setup_db, Drink
from auth.auth import AuthError, requires_auth
from database.models import db_drop_and_create_all, setup_db, Drink, db

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drink():
    drinks = [drink.short() for drink in Drink.query.all()]
    return jsonify({
        "success": True,
        "drinks": drinks
    }), HTTPStatus.OK


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def get_drink_detail():
    drinks = Drink.query.all()
    drinks_detail = [drink.long() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": drinks_detail
    }), HTTPStatus.OK


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def create_drinks():
    request_body = request.json
    if 'title' not in request_body:
        abort(400)

    if "recipe" not in request_body:
        abort(400)

    try:
        new_drink = Drink(
            title=request_body["title"],
            recipe=json.dumps(request_body["recipe"])
        )
        new_drink.insert()

    except Exception:
        db.session.rollback()
        abort(500)
    else:
        return jsonify({
            "success": True,
            "drinks": new_drink.short()
        }), HTTPStatus.CREATED

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


@app.route("/drinks/<int:drink_id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def patch_drink(drink_id):
    drink = Drink.query.get(id)
    if not drink:
        abort(HTTPStatus.NOT_FOUND)
    request_body = request.json
    if "title" in request_body:
        drink.title = request_body["title"]
    elif "recipe" in request_body:
        drink.recipe = json.dumps(request_body["recipe"])
    else:
        abort(HTTPStatus.UNPROCESSABLE_ENTITY)
    try:
        drink.update()
    except Exception:
        db.session.rollback()
        abort(505)
    else:
        return jsonify({
            "success": True,
            "drinks": drink.long()
        }), HTTPStatus.OK
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


@app.route("/drinks/<int:drink_id>")
@requires_auth("delete:drinks")
def delete_drinks(drink_id):
    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404)
    try:
        drink.delete()
    except Exception:
        db.session.rollback()
        abort(500)
    else:
        return jsonify({
            "success": True,
            "delete": drink_id
        }), HTTPStatus.OK

# Error Handling
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
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success":False,
        "message": "Bad Request"
    }), HTTPStatus.BAD_REQUEST


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "message": "Internal Server Error"
    }), HTTPStatus.INTERNAL_SERVER_ERROR
'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "message": "Resource Not Found"
    }), HTTPStatus.NOT_FOUND
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error_handler(error):
    return jsonify({
        "success": False,
        "error": error.error["error"]
    }), error.status_code
    pass


if __name__ == "__main__":
    app.run()
