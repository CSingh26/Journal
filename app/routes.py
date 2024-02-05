from datetime import datetime, timedelta
from flask import Flask, render_template, url_for, flash, redirect, session
from app import app, db, mail
from app.models import User, Journal
from app.forms import SignupForm, LoginForm, JournalForm, DeleteJournalForm, ResetPassword, ResetReqestPassword
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message

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
    deleteForm = DeleteJournalForm()
    return render_template('profile.html', user=user, posts=posts, form=deleteForm)

@app.route('/logout')
def logout():
    session.clear()  
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/journal/new', methods=['GET', 'POST'])
def newJournalEntry():
    if 'user_id' not in session:
        flash('Please login to strat Journaling', 'warning')
        return redirect(url_for('login'))
    
    today_min = datetime.combine(datetime.today(), datetime.min.time())
    today_max = datetime.combine(datetime.today(), datetime.max.time())

    todays_posts = Journal.query.filter(
        Journal.user_id == session['user_id'],
        Journal.created_at.between(today_min, today_max)
    ).order_by(Journal.created_at).all()

    if len(todays_posts) >= 4:
        flash('You cannot post more than 4 times a day.')
        return redirect(url_for('home'))
    
    form = JournalForm()
    if form.validate_on_submit():
        journalEntry = Journal(content=form.content.data, user_id=session['user_id'])
        db.session.add(journalEntry)
        db.session.commit()
        return redirect(url_for('profile', username=session['username']))
    
    return render_template('blog.html', form=form)

@app.route('/journal/delete/<int:post_id>', methods=['POST'])
def deleteEntry(post_id):
    if 'user_id' not in session:
        flash('Please log in to delete journal enteries', 'warning')
        return redirect(url_for('login'))
    
    postToDelete = Journal.query.get_or_404(post_id)
    db.session.delete(postToDelete)
    db.session.commit()

    return redirect(url_for('profile', username=session['username']))

@app.route('/journal/entry/<int:post_id>')
def journalEntry(post_id):
    post = Journal.query.get_or_404(post_id)
    return render_template('entry.html', post=post)

def sendMail(user):
    token = User.generateConfirmationToken(user.email)
    msg = Message('Password Rest Request', recipients=[user.email], sender='noreply@journal.com')
    msg.body = f''' To reset your password, Please follow the link below

    {url_for('resetRequest', token=token, _external=True)}

    If you didnt send a password reset request, then please ignore this message.
    '''
    mail.send(msg)

@app.route('/resetPassword', methods=['GET', 'POST'])
def resetPassword():
    form = ResetPassword()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            flash('Password reset email sent', 'info')
            sendMail(user)
            return redirect(url_for('login'))
        else:
            flash('Username does not exit', 'danger')
    return render_template('reset.html', form=form)

@app.route('/resetPassword/<token>', methods=['GET', 'POST'])
def resetRequest(token):
    userEmail = User.confirmToken(token)
    if userEmail is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('resetPassword'))
    
    user = User.query.filter_by(email=userEmail).first()
    if user is None:
        flash('No user found with this email', 'warning')
        return redirect(url_for('resetPassword'))

    form = ResetReqestPassword()
    if form.validate_on_submit():
        hashedPwd = generate_password_hash(form.password.data)
        user.password_hash = hashedPwd
        db.session.commit()
        flash('Password changed', 'success')
        return redirect(url_for('login'))
    
    return render_template('change.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)