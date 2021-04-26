from flask_restful import reqparse, abort, Api, Resource
from data import db_session
from data.chat import Chat
from flask import jsonify
import parser


def abort_if_chat_not_found(chat_id):
    session = db_session.create_session()
    chat = session.query(Chat).get(chat_id)
    if not chat:
        abort(404, message=f"Chat {chat_id} not found")


class ChatsResource(Resource):
    def get(self, chat_id):
        abort_if_chat_not_found(chat_id)
        session = db_session.create_session()
        chats = session.query(Chat).get(chat_id)
        return jsonify({'chats': chats.to_dict(
            only=('id', 'title', 'users', 'messages'))})

    def delete(self, chat_id):
        abort_if_chat_not_found(chat_id)
        session = db_session.create_session()
        chats = session.query(Chat).get(chat_id)
        session.delete(chats)
        session.commit()
        return jsonify({'success': 'OK'})


class ChatsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        chats = session.query(Chat).all()
        return jsonify({'chats': [item.to_dict(
            only=('id', 'title', 'users', 'messages')) for item in chats]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        chats = Chat(
            id=args['id'],
            title=args['title'],
            users=args['users'],
            messages=args['messages']
        )
        session.add(chats)
        session.commit()
        return jsonify({'success': 'OK'})