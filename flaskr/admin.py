from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.auth import login_required, admin_required
from flaskr.db import get_db

from flask import jsonify

bp = Blueprint('admin', __name__)

@bp.route('/admin')
@admin_required
def index():
    users_l=[]
    db = get_db()
    users = db.execute(
        'SELECT id, username, role, created_at'
        ' FROM user'
        ' ORDER BY created_at DESC'
    ).fetchall()
    for user in users:
         users_l.append(list(user))

    return jsonify(users_l)
    # return render_template('admin/index.html', users=users)

@bp.route('/creatu', methods=('GET', 'POST'))
@login_required
@admin_required
def creatu():
    if request.method == 'POST':
        username = request.json['username']
        password = request.json['password']
        # username = request.form['username']
        # password = request.form['password']
        role = "ROLE_USER"
        error = None

        if request.json.get('role') == "on":
            role = "ROLE_ADMIN"

        if not username:
            error = 'Username is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO user (username, password, role)'
                ' VALUES (?, ?, ?)',
                (username, generate_password_hash(password), role)
            )
            db.commit()
            return redirect(url_for('admin.index'))

    # return render_template('admin/creatu.html')

def get_user(id):
    user = get_db().execute(
        'SELECT id, username, role, password'
        ' FROM user'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if user is None:
        abort(404, "User id {0} doesn't exist.".format(id))

    return user

@bp.route('/<int:id>/updatu', methods=('GET', 'POST'))
@login_required
@admin_required
def updatu(id):
    user = get_user(id)

    if request.method == 'POST':
        username = request.json['username']
        password = request.json['password']
        # username = request.form['username']
        # password = request.form['password']
        role = "ROLE_USER"
        error = None
        db = get_db()

        if request.form.get('role') == "on":
            role = "ROLE_ADMIN"

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None and user['username'] != username:
            error = 'User {} is already registered.'.format(username)

        if error is not None:
            flash(error)
        else:
            db.execute(
                'UPDATE user SET username = ?,password = ?, role = ?'
                ' WHERE id = ?',
                (username, generate_password_hash(password), role, id,)
            )
            db.commit()
            return redirect(url_for('admin.index'))

    # return render_template('admin/updatu.html', user=user)

@bp.route('/<int:id>/deletu', methods=('POST',))
@login_required
@admin_required
def deletu(id):
    get_user(id)
    print(id)
    db = get_db()
    db.execute('DELETE FROM user WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('admin.index'))