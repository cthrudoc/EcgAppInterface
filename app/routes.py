from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User, User_Login, Chart, Vote, Post
from datetime import datetime, timezone

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = []
    return render_template('index.html', title='Home', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)

        login_happened = User_Login(user_id = user.id) # tracking user login
        db.session.add(login_happened)
        db.session.commit()

        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/testing', methods=['GET','POST'])
@login_required
def testing():
    username = current_user.username
    user = db.first_or_404(sa.select(User).where(User.username == username))
    times = db.session.execute(sa.select(User_Login.login_time).join(User).where(User.username == username)).scalars().all()
    print(times)


    # wyświetlanie listy wykresów i oceny użytkownika 
    user_id = current_user.id
    chart_data = db.session.query(Chart).options(so.selectinload(Chart.chart_votes), so.selectinload(Vote.interacter))
    chart_to_display = [] 
    for chart in chart_data:
        for vote in Chart.chart_votes:
            requester_vote = None # resetujemy wartość do niczego żeby przy następnej pętli nie przypisało tej samej wartości (jeżeli następny chart nie ma głosu to zostałby z poprzedniej pętli)
            if Vote.interacter == user_id: 
                requester_vote = Vote.user_vote
                break
        
        chart_to_display.append(
            {"chart_id" : Chart.id} , 
            {"requester_vote" : requester_vote } 
        )

    return render_template('testing.html', user=user , times=times, chart_data=chart_to_display )

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/admin', methods=['GET','POST'])
@login_required
def admin():
    return render_template("admin.html")

@app.route('/wykres', methods=['GET','POST'])
@login_required
def wykres():
   # wyświetlanie pojedynczego wykresu
    user_id = current_user.id
    chart_data = db.session.execute(sa.select(Chart.chart_data).where(Chart.id == current_user.last_chart)).scalar_one_or_none()
    chart_id = db.session.execute(sa.select(Chart.id).where(Chart.id == current_user.last_chart)).scalar_one_or_none()
    ## zapisywanie wyświetlanego wykresu jako ostatniego zapisanego
    current_user.last_chart = chart_id
    db.session.commit()
    #zapis oceny
    submitted_vote = int(request.form[Post])
    new_vote = Vote()
    db.session.add(new_vote)

    return render_template("wykres.html", chart_data_to_display=chart_data)