"""
Main Application File
Contains all routes and endpoints for the music app.
"""

# Imports
import os
import logging
import babel
import dateutil.parser
from datetime import datetime
from collections import defaultdict
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from logging import FileHandler, Formatter

from forms import *
from models import db, Artist, Venue, Show

# App Setup
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# Jinja Custom Filter
def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value) if isinstance(value, str) else value
    format_str = {
        'full': "EEEE MMMM d, y 'at' h:mma",
        'medium': "EE MM dd, y h:mma"
    }.get(format, format)
    return babel.dates.format_datetime(date, format_str)

app.jinja_env.filters['datetime'] = format_datetime

# Home Route
@app.route('/')
def index():
    recent_artists = Artist.query.order_by(Artist.created_at.desc()).limit(10).all()
    recent_venues = Venue.query.order_by(Venue.created_at.desc()).limit(10).all()
    return render_template('pages/home.html', recent_artists=recent_artists, recent_venues=recent_venues)

# Search Route
@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    artists = venues = []

    if request.method == 'POST':
        if form.validate():
            city, state = form.city.data, form.state.data
            artists = Artist.query.filter_by(city=city, state=state).all()
            venues = Venue.query.filter_by(city=city, state=state).all()
            return render_template('pages/show_results.html', city=city, state=state, artists=artists, venues=venues)
        flash('Please enter a valid city and state.')

    return render_template('forms/search_results.html', form=form, artists=artists, venues=venues)

# Artist Routes
@app.route('/artists')
def artists():
    return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
    term = request.form.get('search_term')
    artists = Artist.query.filter(Artist.name.ilike(f'%{term}%')).all()
    return render_template('pages/search_artists.html', results={'count': len(artists), 'data': artists}, search_term=term)

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    return render_template('forms/new_artist.html', form=ArtistForm())

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            artist = Artist(**{field.name: field.data for field in form})
            db.session.add(artist)
            db.session.commit()
            flash(f'Artist {artist.name} was successfully listed!')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            print(e)
            flash(f'An error occurred. Artist {form.name.data} could not be listed.')
        finally:
            db.session.close()
    else:
        errors = ", ".join([f"{field}: {error}" for field, errs in form.errors.items() for error in errs])
        flash(f'Please fix the following errors: {errors}')
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    now = datetime.now()

    shows = db.session.query(Show, Venue).join(Venue).filter(Show.artist_id == artist_id).all()
    past, upcoming = [], []

    for show, venue in shows:
        info = {
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": format_datetime(show.start_time)
        }
        (past if show.start_time <= now else upcoming).append(info)

    artist_data = artist.__dict__
    artist_data.update({
        'past_shows': past,
        'upcoming_shows': upcoming,
        'past_shows_count': len(past),
        'upcoming_shows_count': len(upcoming)
    })

    availability = []
    if artist.availability:
        for slot in artist.availability:
            try:
                slot_time = datetime.strptime(f"{slot['date']} {slot['start_time']}", "%Y-%m-%d %H:%M")
                if slot_time > now:
                    availability.append(f"{slot['date']}, {slot['start_time']}")
            except ValueError:
                continue

    return render_template('pages/show_artist.html', artist=artist_data, availability_data=availability)

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    return render_template('forms/edit_artist.html', form=ArtistForm(obj=artist), artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)
    artist = Artist.query.get_or_404(artist_id)
    try:
        for field in form:
            if hasattr(artist, field.name):
                setattr(artist, field.name, field.data)
        db.session.commit()
        flash(f'Artist {artist.name} was successfully updated!')
    except Exception as e:
        db.session.rollback()
        print(e)
        flash(f'An error occurred. Artist {form.name.data} could not be updated.')
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

# Venue Routes
@app.route('/venues')
def venues():
    venues = Venue.query.order_by(Venue.state, Venue.city).all()
    grouped_data = defaultdict(lambda: {"venues": []})

    for venue in venues:
        key = (venue.city, venue.state)
        grouped_data[key]["city"] = venue.city
        grouped_data[key]["state"] = venue.state
        grouped_data[key]["venues"].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len([show for show in venue.shows if show.start_time > datetime.now()])
        })

    return render_template('pages/venues.html', areas=list(grouped_data.values()))

@app.route('/venues/search', methods=['POST'])
def search_venues():
    term = request.form.get('search_term')
    venues = Venue.query.filter(Venue.name.ilike(f'%{term}%')).all()
    data = [{
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': len([show for show in venue.shows if show.start_time > datetime.now()])
    } for venue in venues]

    return render_template('pages/search_venues.html', results={'count': len(data), 'data': data}, search_term=term)

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    return render_template('forms/new_venue.html', form=VenueForm())

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            venue = Venue(**{field.name: field.data for field in form})
            db.session.add(venue)
            db.session.commit()
            flash(f'Venue {venue.name} was successfully listed!')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            print(e)
            flash('An error occurred. Venue could not be listed.')
        finally:
            db.session.close()
    else:
        errors = ", ".join([f"{field}: {error}" for field, errs in form.errors.items() for error in errs])
        flash(f'Please fix the following errors: {errors}')
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    now = datetime.now()

    shows = db.session.query(Show, Artist).join(Artist).filter(Show.venue_id == venue_id).all()
    past, upcoming = [], []

    for show, artist in shows:
        info = {
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": format_datetime(show.start_time)
        }
        (past if show.start_time <= now else upcoming).append(info)

    venue_data = venue.__dict__
    venue_data.update({
        'past_shows': past,
        'upcoming_shows': upcoming,
        'past_shows_count': len(past),
        'upcoming_shows_count': len(upcoming)
    })

    return render_template('pages/show_venue.html', venue=venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    return render_template('forms/edit_venue.html', form=VenueForm(obj=venue), venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    venue = Venue.query.get_or_404(venue_id)
    try:
        for field in form:
            if hasattr(venue, field.name):
                setattr(venue, field.name, field.data)
        db.session.commit()
        flash(f'Venue {venue.name} was successfully updated!')
    except Exception as e:
        db.session.rollback()
        print(e)
        flash(f'An error occurred. Venue {form.name.data} could not be updated.')
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

# Show Routes
@app.route('/shows')
def shows():
    shows = db.session.query(
        Show.venue_id,
        Venue.name.label("venue_name"),
        Show.artist_id,
        Artist.name.label("artist_name"),
        Artist.image_link.label("artist_image_link"),
        Show.start_time
    ).join(Artist).join(Venue).all()

    data = [{
        'venue_id': show.venue_id,
        'venue_name': show.venue_name,
        'artist_id': show.artist_id,
        'artist_name': show.artist_name,
        'artist_image_link': show.artist_image_link,
        'start_time': show.start_time.isoformat()
    } for show in shows]

    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create', methods=['GET', 'POST'])
def create_show_submission():
    form = ShowForm(request.form, meta={'csrf': False})
    if request.method == 'POST' and form.validate():
        try:
            show = Show(
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                start_time=form.start_time.data
            )
            show_date = show.start_time.date().isoformat()
            show_time = show.start_time.time().strftime('%H:%M')
            if is_artist_available(show.artist_id, show_date, show_time):
                db.session.add(show)
                db.session.commit()
                flash('Show successfully listed!')
                return redirect(url_for('index'))
            else:
                flash('Artist is not available at that time.')
        except Exception as e:
            db.session.rollback()
            print(e)
            flash('An error occurred. Show could not be listed.')
        finally:
            db.session.close()
    return render_template('forms/new_show.html', form=form)

def is_artist_available(artist_id, date_str, time_str):
    artist = Artist.query.get_or_404(artist_id)
    return any(slot['date'] == date_str and slot['start_time'] == time_str for slot in artist.availability)

# Artist Availability
@app.route('/artists/<int:artist_id>/set_availability', methods=['GET', 'POST'])
def set_availability(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    form = AvailabilityForm(request.form, meta={'csrf': False})
    if request.method == 'POST' and form.validate():
        try:
            availability = [{
                'date': entry.date.data.strftime('%Y-%m-%d'),
                'start_time': entry.start_time.data.strftime('%H:%M')
            } for entry in form.entries]
            artist.availability = availability
            db.session.commit()
            flash('Availability updated!')
            return redirect(url_for('show_artist', artist_id=artist_id))
        except Exception as e:
            db.session.rollback()
            print(e)
            flash('Error updating availability.')
        finally:
            db.session.close()
    return render_template('forms/set_availability.html', form=form, artist=artist)

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

# Logging
if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.info('Errors logged')

# Entry Point
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5010))
    app.run(host='0.0.0.0', port=port, debug=True)
