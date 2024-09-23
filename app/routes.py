from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, logout_user, current_user, login_required
from functools import wraps
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

def admin_required(f):
    @wraps
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def admin_prohibited(f):
    @wraps
    def decorated_function(*args, **kwargs):
        if current_user.is_admin: 
            abort(403) 
        return f(*args, **kwargs) 
    return decorated_function 


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin == True:
            return redirect(url_for('admin'))
        return redirect(url_for('user', username=current_user.username))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)

        login_happened = User_Login(user_id = user.id) # śledzenie logowania 
        db.session.add(login_happened) # zapisywanie logowania 
        db.session.commit()

        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('admin') if user.is_admin else url_for('user', username=user.username)
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('login'))
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
@admin_prohibited
def user(username):
    user = db.first_or_404(sa.select(User).where(User.id == current_user.id))
    username = user.username

    # wyświetlanie listy wykresów i głosy użytkownika 

    page = request.args.get( 'page' , 1 , type = int )
    per_page = 20 
    offset = (page - 1) * per_page
    charts = db.session.execute(sa.select(Chart).offset(offset).limit(per_page)).scalars().all() # wczytywanie określonej liczby głosów 

    all_charts = db.session.execute(sa.select(Chart)).scalars().all()
    total_charts = len(all_charts)
    total_pages = (total_charts-1) // per_page + 1
    next_page = page + 1 if page*per_page < total_charts else None 
    prev_page = page - 1 if page >1 else None # jeżeli strona to 1 to nie wyświetlamy strony "zero"

    votes = db.session.execute(sa.select(Vote).where(Vote.interacting_user == user.id)).scalars().all()
    
    latest_votes_for_chart = {} # dict na najnowsze głosy
    for vote in votes:
        if vote.chart_id not in latest_votes_for_chart or vote.revision_number > latest_votes_for_chart[vote.chart_id].revision_number: # jeżeli jeszcze nie ma głosu albo głos w aktualnej pętli jest nowszy...
            latest_votes_for_chart[vote.chart_id] = vote # zapisujemy głos z aktualnej pętli
    
    chart_to_display = []
    for chart in charts:
        requester_vote = latest_votes_for_chart.get(chart.id, None) 
        if requester_vote is not None:
            requester_vote = requester_vote.user_vote
        else:
            requester_vote = None
        chart_to_display.append({
            "chart_id": chart.id,
            "requester_vote": requester_vote
        })

    # wywoływanie numeru ostatniego wykresu : 
    last_chart = user.last_chart

    return render_template(
        'user.html', user=user, 
        chart_data=chart_to_display , last_chart = last_chart , 
        next_page = next_page , prev_page = prev_page , total_pages = total_pages , current_page = page 
        )


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
    # wyświetlanie wszystkich czasów loginów 
    user = db.first_or_404(sa.select(User).where(User.id == current_user.id))
    times = db.session.execute(sa.select(User_Login.login_time).join(User).where(User.username == user.username)).scalars().all()
    print(times)

    # wyświetlanie listy wykresów i głosy użytkownika 

    charts = db.session.execute(sa.select(Chart)).scalars().all()  
    votes = db.session.execute(sa.select(Vote).where(Vote.interacting_user == user.id)).scalars().all()
    

    latest_votes_for_chart = {} # dict na najnowsze głosy

    for vote in votes:
        if vote.chart_id not in latest_votes_for_chart or vote.revision_number > latest_votes_for_chart[vote.chart_id].revision_number: # jeżeli jeszcze nie ma głosu albo głos w aktualnej pętli jest nowszy...
            latest_votes_for_chart[vote.chart_id] = vote # zapisujemy głos z aktualnej pętli
    
    chart_to_display = []
    for chart in charts:
        requester_vote = latest_votes_for_chart.get(chart.id, None)
        if requester_vote is not None:
            requester_vote = requester_vote.user_vote
        else:
            requester_vote = None
        chart_to_display.append({
            "chart_id": chart.id,
            "requester_vote": requester_vote
        })

    # wywoływanie numeru ostatniego wykresu : 
    last_chart = user.last_chart

    return render_template('testing.html', user=user , times=times, chart_data=chart_to_display , last_chart = last_chart )


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/wykres', methods=['GET','POST'])
@login_required
@admin_prohibited
def wykres(): 
    user = db.first_or_404(sa.select(User).where(User.id == current_user.id)) # wczytanie obiektu użytkownik 
    chart_id = request.args.get('chart_id', default = None, type = int)
    if chart_id: # wyświetlanie podanego wykresu, jeżeli nie podany, domyślnie ostatni wykres
        chart = db.first_or_404(sa.select(Chart).where(Chart.id == chart_id))
    else:
        chart = db.first_or_404(sa.select(Chart).where(Chart.id == user.last_chart))
        chart_id = chart.id
    chart_data = chart.chart_data 
    # zapisywanie wyświetlanego wykresu jako ostatniego zapisanego
    user.last_chart = chart_id
    db.session.commit()
    #zapis oceny
    submitted_vote = request.args.get('vote')
    form_chart_id = request.args.get('chart_id')
    if submitted_vote is not None and form_chart_id == str(chart_id):
        # sprawdzanie która to wersja głosu i przypisywanie numeru
        latest_vote = db.session.execute(sa.select(Vote) 
                                     .where(Vote.interacting_user == user.id, Vote.chart_id == chart_id)
                                     .order_by(Vote.revision_number.desc())
                                     .limit(1)).scalar() # wybieramy głosy na dany wykres, i wybieramy ostatni z listy. Jeżeli głosu nie ma, .scalar() zwraca None
        if latest_vote: # jeżeli głos istnieje w ogóle 
            new_revision_number = (latest_vote.revision_number + 1) # to dodaj do aktualnego +1
        else: # jeżeli nie istnieje 
            new_revision_number = 1 # to podejście ma numer 1

        new_vote = Vote(user_vote = submitted_vote, interacting_user = user.id, chart_id = chart.id, revision_number = new_revision_number)
        db.session.add(new_vote)
        db.session.commit()

    return render_template("wykres.html", chart_data=chart_data, chart_id = chart_id)    

@app.route('/admin')
@admin_required
def admin():
    return render_template("admin.html")


@app.route('/admin/charts')
@admin_required
def admin_wykresy():
    return render_template('admin_charts.html')


@app.route('/admin/users')
@admin_required
def admin_users():
    return render_template('admin_users.html')