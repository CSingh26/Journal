from datetime import datetime, timedelta
from flask import Flask, render_template, url_for, flash, redirect, session
from app import app, db
from app.models import User, Journal
from app.forms import SignupForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            session['user_id'] = user.id 
            session['username'] = user.username
            flash('Loged In', 'success')
            return redirect(url_for('profile', username=user.username))
        else:
            flash('Invalid UserName or Password', 'danger')
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hassed_pwd = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password_hash=hassed_pwd)
        db.session.add(new_user)
        db.session.commit()
        flash('Account Successully Created!', 'success')
        return  redirect(url_for('login'))
    return render_template('signup.html', title='Sign Up', form=form)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    thirtyDaysAgo = datetime.utcnow() - timedelta(days=30)
    posts = Journal.query.filter(Journal.user_id == user.id, Journal.created_at > thirtyDaysAgo).order_by(Journal.created_at.desc()).all()
    return render_template('profile.html', user=user, posts=posts)

@app.route('/logout')
def logout():
    session.clear()  
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)