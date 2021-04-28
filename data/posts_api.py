import flask
from flask import jsonify, request

from data import db_session
from data.posts import Post

blueprint = flask.Blueprint(
    'posts_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/posts')
def get_posts():
    db_sess = db_session.create_session()
    posts = db_sess.query(Post).all()
    return jsonify(
        {
            'posts':
                [item.to_dict(only=('title', 'content', 'user.name', 'created_date', 'is_private'))
                 for item in posts]
        }
    )


@blueprint.route('/api/posts/<int:posts_id>', methods=['GET'])
def get_one_post(posts_id):
    db_sess = db_session.create_session()
    posts = db_sess.query(Post).get(posts_id)
    if not posts:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'posts': posts.to_dict(only=(
                'title', 'content', 'user.name', 'created_date', 'is_private'))
        }
    )


@blueprint.route('/api/posts', methods=['POST'])
def create_post():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['title', 'content', 'user_id', 'is_private']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    posts = Post(
        title=request.json['title'],
        content=request.json['content'],
        user_id=request.json['user_id'],
        is_private=request.json['is_private'],
        image_name=request.json['image_name']
    )
    db_sess.add(posts)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/posts/<int:news_id>', methods=['DELETE'])
def delete_posts(posts_id):
    db_sess = db_session.create_session()
    posts = db_sess.query(Post).get(posts_id)
    if not posts:
        return jsonify({'error': 'Not found'})
    db_sess.delete(posts)
    db_sess.commit()
    return jsonify({'success': 'OK'})