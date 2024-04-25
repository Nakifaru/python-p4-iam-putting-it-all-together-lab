#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):

    def post(self):
        data = request.get_json()

        username = data.get('username')
        image_url = data.get('image_url')
        bio = data.get('bio')
        password = data.get('password')
        password_confirmation = data.get('password_confirmation')

        existing_user = User.query.filter(User.username == username).first()

        if existing_user:
            return (
                {'error': 'Username already exists'},
                422,
            )        

        if not all ([username, image_url, bio, password, password_confirmation]):
            return (
                {'error': 'All fields are required to be filled'},
                422,
            )

        if password_confirmation != password:
            return (
                {'error': 'Password confirmation does not match password'},
                422,
            )

        user = User(username=username, image_url=image_url, bio=bio)
        user.password_hash(password)
        session['user_id'] = user.id

        return (
            user.to_dict(),
            201,
        )


class CheckSession(Resource):
    
    def get(self):
        ID = session['user_id']

        if ID:
            user = User.query.filter(User.id == ID).first()

            return ({
                user.to_dict(),
                200,
            })
        else:
            return (
                {'error': 'User not logged in.'},
                401,
            )


class Login(Resource):
    
    def post(self):

        username = request.get_json()['username']
        password = request.get_json()['password']

        user = User.query.filter(User.username == username).first()

        if not user:
            return (
                {'error': 'Username not found.'},
                401,
            )
        if user.authenticate(password):
            session['user_id'] = user.id
            return (
                user.to_dict(),
                200,
            )
        else:
            return (
                {'error': 'Incorrect password'},
                401,
            )

class Logout(Resource):

    def delete(self):
        if session['user_id']:
            session['user_id'] = None
            return (
                {},
                204,
            )
        else:
            return (
                {'error': 'User must be logged in.'},
                401,
            )


class RecipeIndex(Resource):

    def get(self):
        ID = session['user_id']
        
        if ID:
            recipes = []
            for recipe in Recipe.query.all():
                recipe.user_id = ID
                recipe_dict = recipe.to_dict()
                recipes += recipe_dict
            return (
                recipes,
                200,
            )
        else:
            return (
                {'error': 'User must be logged in.'},
                401,
            )
        
    def post(self):
        ID = session['user_id']
        data = request.get_json()
        title = data.get('title')
        instructions = data.get('instructions')
        minutes_to_complete = data.get('minutes_to_complete')
        
        if ID:
            user = User.query.filter(User.id == ID).first()
            if not all([data, title, instructions, minutes_to_complete]):
                return (
                    {'error': 'All fields must be filled'},
                    422,
                )
            new_recipe = Recipe(title=title, instructions=instructions, minutes_to_complete=minutes_to_complete, user_id=ID)
            
            return (
                new_recipe.to_dict(),
                201
            )
        
        else:
            return (
                {'error': 'User must be logged in.'},
                422,
            )




    pass

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)