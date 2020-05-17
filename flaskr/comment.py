from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

from flask import jsonify

bp = Blueprint('post', __name__)

@bp.route('/<int:id>/show')
def show(id):
    db = get_db()
    post = get_post(id)
    comments_l = []
    comment = db.execute(
        'SELECT c.id, content, p.created, created_at_comment, author_comment_id, u.username'
        ' FROM comment c JOIN user u ON c.author_comment_id = u.id'
        ' JOIN  post p ON c.post_id = p.id'
        ' WHERE c.post_id = ?',
        (id,)
    ).fetchall()
    for comments in comment:
         comments_l.append(list(comments))

    return jsonify(comments_l)
    # return render_template('comment/post.html', post=post, comments=comment)

@bp.route('/<int:id>/creatc', methods=('GET', 'POST'))
@login_required
def creatc(id):
    post = get_post(id)
    if request.method == 'POST':
        content = request.json['content']
        # content = request.form['content']
        error = None

        if not content:
            error = 'Content is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO comment (content, post_id , author_comment_id)'
                ' VALUES (?, ?, ?)',
                (content, id, g.user['id'],)
            )
            db.commit()
            return redirect(url_for('post.show', id=id))

    # return render_template('comment/creatc.html', post=post)

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

def get_comment(id, check_author=True):
    comment = get_db().execute(
        'SELECT c.id, content, p.created, created_at_comment, author_comment_id, u.username, post_id'
        ' FROM comment c JOIN user u ON c.author_comment_id = u.id'
        ' JOIN  post p ON c.post_id = p.id'
        ' WHERE c.id = ?',
        (id,)
    ).fetchone()

    if comment is None:
        abort(404, "Comment id {0} doesn't exist.".format(id))

    if check_author and comment['author_comment_id'] != g.user['id']:
        abort(403)

    return comment


@bp.route('/<int:id>/updatc', methods=('GET', 'POST'))
@login_required
def updatc(id):
    comment = get_comment(id)

    if request.method == 'POST':
        content = request.json['content']
        # content = request.form['content']
        error = None

        if not content:
            error = 'Content is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE comment SET content = ?'
                ' WHERE id = ?',
                (content, id)
            )
            db.commit()
            return redirect(url_for('post.show', id=comment['post_id']))

    # return render_template('comment/updatc.html', comment=comment)

@bp.route('/<int:id>/deletc', methods=('POST',))
@login_required
def deletc(id):
    comment = get_comment(id)
    post_id=comment['post_id']
    db = get_db()
    db.execute('DELETE FROM comment WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('post.show', id=post_id))