from flask import *
import requests
from Tracker.forms import *
from Tracker.models import *
from flask_login import login_required, current_user, login_user, logout_user
from Tracker import *
from sqlalchemy import func
from datetime import datetime, timedelta
from collections import Counter


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
        user = current_user.username

        movies = Movie.query.filter_by(username=user).count()
        all_movies = Movie.query.filter_by(username=user).all()

        # Flatten and count genres (since they're comma-separated strings)
        all_genres = []
        for movie in all_movies:
            if movie.genre:
                genres = [g.strip() for g in movie.genre.split(',')]
                all_genres.extend(genres)

        genre_counts = Counter(all_genres)
        genre_name = genre_counts.most_common(1)[0][0] if genre_counts else None

        recent_add = (
            Movie.query.filter_by(username=user)
            .filter(Movie.added >= one_week_ago)
            .limit(3)
            .all()
        )

        watch = (
            Movie.query.filter_by(username=user)
            .filter(Movie.progress == 'Completed', Movie.finish >= one_week_ago)
            .limit(3)
            .all()
        )

        return render_template(
            'dashboard.html',
            movies=movies,
            genre_name=genre_name,
            user=user,
            recent_add=recent_add,
            watch=watch
        )
    
    #Glossary Route
    @app.route('/glossary', methods=['GET', 'POST'])
    def glossary():
        form = SearchForm()
        results = None
        search_performed = False
        all_terms = Glossary.query.all()
        
        if form.validate_on_submit():
            search_performed = True
            search_term = form.search.data.lower()
            if search_term:
                # Search in both term and definition
                results = Glossary.query.filter(
                    db.or_(
                        db.func.lower(Glossary.term).contains(search_term),
                        db.func.lower(Glossary.definition).contains(search_term)
                    )
                ).all()
        
        return render_template('glossary.html', 
                            form=form, 
                            results=results, 
                            all_terms=all_terms, 
                            search_performed=search_performed)


    #Add Movie Route
    @app.route('/add_movie', methods=['GET', 'POST'])
    @login_required
    def addMovie():
        form = AddMovieForm()
        form.genre.data = form.genre.data or []
        if form.validate_on_submit():
            name=form.name.data
            rate=form.rate.data
            added=form.added.data
            plot=form.plot.data
            release=form.release.data
            genre=",".join(form.genre.data)
            progress=form.progress.data
            repeat=form.repeat.data
            start=form.start.data
            finish=form.finish.data
            notes=form.notes.data

            new_movie=Movie(name=name, username=current_user.username, rate=rate, added=added, genre=genre, progress=progress, repeat=repeat, start=start, finish=finish, notes=notes, plot=plot, release=release)

            db.session.add(new_movie)
            db.session.commit()
            flash_message('Movie was registered.', 'success')
            return redirect(url_for('dashboard'))
        return render_template('add.html', form=form)
    
    #View All Logs
    @app.route('/view_all', methods=['GET', 'POST'])
    @login_required
    def viewMovies():
        form = SearchForm()
        movies = Movie.query.filter_by(username=current_user.username).all()
        if form.validate_on_submit():
            search_term = form.search.data
            results = Movie.query.filter_by(username=current_user.username).filter(Movie.name.ilike(f"%{search_term}%")).all()
            return render_template('view_all.html', form=form, results=results, movies=movies)
        return render_template('view_all.html', form=form, movies=movies)
    
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
        form.genre.data = [g.strip() for g in movie.genre.split(',')] if movie.genre else []
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
    
    #Search Route
    @app.route('/search', methods=['GET', 'POST'])
    @login_required
    def search():
        form = SearchForm()
        if form.validate_on_submit():
            search_term = form.search.data
            results = get_movie(search_term)
            return render_template('search.html', form=form, results=results)
        return render_template('search.html', form=form)

    def get_movie(search_term):
        if not search_term:
            return None

        url = "http://www.omdbapi.com/"
        params = {
            'apikey': OMDB_API_KEY,
            's': search_term
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('Response') == "True":
                return data.get('Search', [])
            return []
        else:
            return []
    
    #Movie Info Route
    @app.route('/movie_info/<string:imdb_id>', methods=['GET'])
    @login_required
    def movie_info(imdb_id):
        url = "http://www.omdbapi.com/"
        params = {
            'apikey': OMDB_API_KEY,
            'i': imdb_id
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('Response') == "True":
                return render_template('movie_info.html', movie=data)
            else:
                flash_message('Movie not found.', 'danger')
                return redirect(url_for('search'))
        else:
            flash_message('Error fetching movie details.', 'danger')
            return redirect(url_for('search'))
        
    #Add from IMDB
    @app.route('/add_from_imdb/<string:imdb_id>', methods=['GET'])
    @login_required
    def add_from_imdb(imdb_id):
        url = "http://www.omdbapi.com/"
        params = {
            'apikey': OMDB_API_KEY,
            'i': imdb_id
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('Response') == "True":
                genres_raw = data.get('Genre', '')
                genre_list = [g.strip() for g in genres_raw.split(',')] if genres_raw else []
                movie_data = {
                    'name': data.get('Title'),
                    'rate': 'Neutral',
                    'added': datetime.now(),
                    'genre': genre_list,
                    'plot': data.get('Plot'),
                    'release': datetime.strptime(data.get('Released'), "%d %b %Y").date() if data.get('Released') else None,
                    'progress': 'Not Started',
                    'repeat': False,
                    'start': None,
                    'finish': None,
                    'notes': ''
                }
                print(movie_data)
                form = AddMovieForm(data=movie_data)
                return render_template('add.html', form=form)
            else:
                flash_message('Movie not found.', 'danger')
                return redirect(url_for('search'))
        else:
            flash_message('Error fetching movie details.', 'danger')
            return redirect(url_for('search'))
        