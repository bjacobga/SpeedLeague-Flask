from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import UserMixin, login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from .supabase_client import supabase

auth_bp = Blueprint('auth', __name__)


class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username


def load_user_by_id(user_id):
    response = supabase.table('players').select('id, username').eq('id', user_id).execute()
    if response.data:
        d = response.data[0]
        return User(d['id'], d['username'])
    return None


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        response = supabase.table('players').select('id, username, password_hash').eq('username', username).execute()
        if response.data:
            player = response.data[0]
            if check_password_hash(player['password_hash'], password):
                login_user(User(player['id'], player['username']))
                return redirect(url_for('main.submit'))

        flash('Invalid username or password.')
        return render_template('login.html')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
