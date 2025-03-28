from flask import Flask, jsonify, request, Response
from database import Session
from flask.views import MethodView
from models import Announcement, User, Base
from errors import HttpError
from schema import (
    CreateAdSchema,
    CreateUserSchema,
    UpdateAdSchema,
    validate_json
)
from auth import hash_password, auth


app = Flask(__name__)


@app.errorhandler(HttpError)
def error_headler(err: HttpError):
    http_responce = jsonify({'error': err.message})
    http_responce.status_code = err.status_code
    return http_responce


@app.before_request
def before_request():
    request.db_session = Session()


@app.after_request
def after_request(reponse: Response):
    request.db_session.close()
    return reponse


def get_announ(announ_id: int):
    announ = request.db_session.get(Announcement, announ_id)
    if announ is None:
        raise HttpError(404, 'announcecment is not found')
    return announ


def add_obj(obj: Base):
    request.db_session.add(obj)
    request.db_session.commit()


def delete_obj(obj: Base):
    request.db_session.delete(obj)
    request.db_session.commit()


class AnnouncementView(MethodView):

    def get(self, announ_id: int):
        announ = get_announ(announ_id)
        return jsonify(announ.dict)

    @auth.login_required
    def post(self):
        try:
            json_data = validate_json(CreateAdSchema, request.json)
            announ = Announcement(
                title=json_data['title'],
                description=json_data['description'],
                user_id=auth.current_user().id
            )
            add_obj(announ)
            return jsonify(announ.id_dict)
        except KeyError:
            raise HttpError(400, 'Bad Request')

    @auth.login_required
    def patch(self, announ_id: int):
        announ = get_announ(announ_id)
        if announ.user_id != auth.current_user().id:
            raise HttpError(403, 'Permission denied')
        json_data = validate_json(UpdateAdSchema, request.json)
        if 'title' in json_data:
            announ.title = json_data['title']
        if 'description' in json_data:
            announ.description = json_data['description']
        add_obj(announ)
        return jsonify({'message': 'announcement update'}), 200

    @auth.login_required
    def delete(self, announ_id: int):
        announ = get_announ(announ_id)
        if announ.user_id != auth.current_user().id:
            raise HttpError(403, 'Permission denied')
        delete_obj(announ)
        return jsonify({'message': 'announcement delete'})


class UserView(MethodView):

    def get(self):
        pass

    def post(self):
        json_data = validate_json(CreateUserSchema, request.json)
        check_user = request.db_session.query(User).filter(
            User.email == json_data['email']
        ).first()

        if check_user is not None:
            raise HttpError(400, 'User already exists')
        user = User(
            email=json_data['email'],
            password=hash_password(json_data['password'])
        )
        add_obj(user)

        return jsonify({'message': f'Create user: {user.id}'}), 201

    def patch(self):
        pass

    def delete(self):
        pass


announ_view = AnnouncementView.as_view('announ_view')
user_view = UserView.as_view('user_view')


app.add_url_rule(
    '/api/v1/announcements',
    view_func=announ_view,
    methods=['POST']
)
app.add_url_rule(
    '/api/v1/announcements/<int:announ_id>',
    view_func=announ_view,
    methods=['GET', 'PATCH', 'DELETE']
)


app.add_url_rule('/api/v1/register', view_func=user_view, methods=['POST'])
app.add_url_rule(
    '/api/v1/users/<int:user_id>',
    view_func=user_view,
    methods=['GET', 'PATCH', 'DELETE']
)


if __name__ == '__main__':
    app.run()
