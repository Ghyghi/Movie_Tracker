from flask import *
from Tracker.forms import *
from Tracker.models import *
from flask_login import login_required, current_user, login_user, logout_user
from Tracker import *
from sqlalchemy import func
from datetime import datetime, timedelta


def flash_message(message, category):
    flash(message, category)

def register_routes(app):

    # Home Route
    @app.route('/')
    @app.route('/home')
    def home():
        return render_template('index.html')
    
    #Register Route
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form=RegisterForm()
        if form.validate_on_submit():
            names = form.names.data
            username = form.username.data
            password = form.password.data

            existing_user = User.query.filter(username == User.username).first()
            if existing_user:
                flash_message('Username already exists. Please choose a different one.', 'danger')
                return render_template('register.html', form=form)
            else:
                new_user = User(names=names, username=username, password=password)
                db.session.add(new_user)
                db.session.commit()
                flash_message('Please log in.', 'success')
                return redirect(url_for('login'))
        return render_template('register.html', form=form)
    
    #Login Route
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form=LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            user = User.query.filter_by(username=username).first()

            #Check if user exists
            if user and user.password == password:
                login_user(user)
                flash_message('User logged in successfully!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash_message('Invalid username or password. Please try again.', 'danger')
                return redirect(url_for('login'))
        return render_template('login.html', form=form)
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('home'))

    #Dashboard Route
    @app.route('/dashboard', methods=['GET'])
    @login_required
    def dashboard():
        one_week_ago = datetime.now() - timedelta(weeks=1)
        movies = Movie.query.filter_by(username=current_user.username).count()
        user = current_user.username
        viewed =(
            db.session.query(Movie.genre)
            .filter(Movie.username == current_user.username)
            .group_by(Movie.genre)
            .order_by(func.count(Movie.genre).desc())  # Sort by count in descending order
            .first()  # Get the first result
        )
        genre_name = viewed[0] if viewed else None
        recent_add = Movie.query.filter_by(username=user).filter(Movie.added >= one_week_ago).limit(3).all()
        watch = Movie.query.filter_by(username=user).filter(Movie.progress == 'Completed', Movie.finish >= one_week_ago).limit(3).all()
        return render_template('dashboard.html', movies=movies, genre_name=genre_name, user=user, recent_add=recent_add, watch=watch)
    
    #Glossary Route
    @app.route('/glossary', methods=['GET'])
    @login_required
    def glossary():
        return render_template('glossary.html')
    
    #Add Movie Route
    @app.route('/add_movie', methods=['GET', 'POST'])
    @login_required
    def addMovie():
        form = AddMovieForm()
        if form.validate_on_submit():
            name=form.name.data
            rate=form.rate.data
            added=form.added.data
            genre=",".join(form.genre.data)
            progress=form.progress.data
            repeat=form.repeat.data
            start=form.start.data
            finish=form.finish.data
            notes=form.notes.data

            new_movie=Movie(name=name, username=current_user.username, rate=rate, added=added, genre=genre, progress=progress, repeat=repeat, start=start, finish=finish, notes=notes)

            db.session.add(new_movie)
            db.session.commit()
            flash_message('Movie was registered.', 'success')
            return redirect(url_for('dashboard'))
        return render_template('add.html', form=form)
    
    #View All Logs
    @app.route('/view_all', methods=['GET'])
    @login_required
    def viewMovies():
        movies = Movie.query.filter_by(username=current_user.username).all()
        return render_template('view_all.html', movies=movies)
    
    #View A Single Movie
    @app.route('/view_movie/<int:id>', methods=['GET'])
    @login_required
    def view_movie(id):
        movie = Movie.query.filter_by(id=id).first()
        return render_template('view_movie.html', movie=movie)
    
    #Delete a movie
    @app.route('/delete/<int:id>', methods=['GET','POST'])
    @login_required
    def delete(id):
        movie = Movie.query.filter_by(id=id).first_or_404()
        db.session.delete(movie)
        db.session.commit()
        flash_message('Movie deleted successfully!', 'success')
        return redirect(url_for('viewMovies'))
    
    #Update a movie
    @app.route('/update/<int:id>', methods=['GET', 'POST'])
    @login_required
    def update(id):
        movie = Movie.query.filter_by(id=id).first_or_404()
        form = AddMovieForm(obj=movie)
        if form.validate_on_submit():
            movie.name=form.name.data
            movie.rate=form.rate.data
            movie.username = current_user.username
            movie.added=form.added.data
            movie.genre=",".join(form.genre.data)
            movie.progress=form.progress.data
            movie.repeat=form.repeat.data
            movie.start=form.start.data
            movie.finish=form.finish.data
            movie.notes=form.notes.data

            db.session.commit()
            flash_message('Movie was updated.', 'success')
            return redirect(url_for('viewMovies'))
        
        return render_template('update.html', form=form, movie=movie)