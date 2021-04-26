import flask
from flask import jsonify

from data import db_session
from data.chat import Chat

blueprint = flask.Blueprint(
    'chats_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/chats')
def get_chats():
    db_sess = db_session.create_session()
    news = db_sess.query(Chat).all()
    return jsonify(
        {
            'chats':
                [item.to_dict(only=('title', 'users', 'messages'))
                 for item in news]
        }
    )


@blueprint.route('/api/chats/<int:chat_id>', methods=['GET'])
def get_one_chat(chat_id):
    db_sess = db_session.create_session()
    chat = db_sess.query(Chat).get(chat_id)
    if not chat:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'chat': chat.to_dict(only=(
                'title', 'users', 'messages'))
        }
    )