#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for,abort,jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from config import SQLALCHEMY_DATABASE_URI
from flask_migrate import Migrate
from flask_wtf import Form
from forms import *
from datetime import datetime
from models import db, Artist, Venue, Show
from flask_wtf.csrf import CsrfProtect







#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.debug = True

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
def my_form_error(fieldName, errorMessages):
    return flash(
        'Some errors on ' +
        fieldName.replace('_', ' ') +
        ': ' +
        ' '.join([str(message) for message in errorMessages]),
        'warning'
    )
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

def get_value(field_name):

  if field_name == 'genres':
    return request.form.getlist(field_name)
  elif field_name == 'seeking_talent' or field_name == 'seeking_venue' and request.form[field_name] == 'y':
    return True
  elif field_name == 'seeking_talent' or field_name == 'seeking_venue' and request.form[field_name] != 'y':
    return False
  else:
    return request.form[field_name]
#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues_list = Venue.query.all()
  venues_dict = {}
  for venue in venues_list:
    key = f'{venue.city}, {venue.state}'
    venues_dict.setdefault(key, []).append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': len(venue.shows),
        'city': venue.city,
        'state': venue.state
      })
  data = []
  for value in venues_dict.values():
      data.append({
        'city': value[0]['city'],
        'state': value[0]['state'],
        'venues': value
      })

  return render_template('pages/venues.html', areas=data)


 

@app.route('/venues/search', methods=['POST'])
def search_venues():

  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = get_value('search_term')
  venue_result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  response = {
    "count": len(venue_result),
    "data": []
  }

  for result in venue_result:
    response["data"].append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(result.shows)
    })
  
  db.session.close()

    
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
  


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id) 

  
  past_shows = []
  upcoming_shows = []
  show_attributes = None

  for show in venue.shows:
    show_attributes = {
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%m/%d/%Y, %H:%M:%S')
    }

    if show.start_time <= datetime.now():
      past_shows.append(show_attributes)
    else:
      upcoming_shows.append(show_attributes)


  venue_dict = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=venue_dict)
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)



@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(csrf_enabled=True)
  if not form.validate():
        for fieldName, errorMessages in form.errors.items():
            my_form_error(fieldName, errorMessages)
        return redirect(url_for('create_venue_form'))
  new_venue = Venue(
  name = get_value('name'),
  genres = get_value('genres'),
  address = get_value('address'),
  city = get_value('city'),
  state = get_value('state'),
  phone = get_value('phone'),
  website = get_value('website_link'),
  seeking_talent = get_value('seeking_talent'),
  seeking_description = get_value('seeking_description'),
  facebook_link = get_value('facebook_link'),
  image_link = get_value('image_link'),
  )

  try:
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except:
    flash('An error occurred. Venue ' + new_venue.name + ' could not be listed.', category='error')
    db.session.rollback()

  finally:
    db.session.close()
    return redirect(url_for('venues'))
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
 

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  status = False
  try:
    venue = Venue.query.get(venue_id)
    status=True
    db.session.delete(venue)
    db.session.commit()
    flash('Venue successfully deleted!')
  
  except:
    status=False
    db.session.rollback()

    flash('Error deleting venue', category='error')

  finally:
    db.session.close()
  
  return jsonify({
    'success': status
    })
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data = []
  artist_ke = {}

  for artist in artists:
    artist_ke = {
      "id": artist.id,
      "name": artist.name,
    }
    data.append(artist_ke)
  return render_template('pages/artists.html', artists=data)
  # TODO: replace with real data returned from querying the database
  

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = get_value('search_term')
  artist_res = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

  res = {
    "count": len(artist_res),
    "data": []
  }

  for result in artist_res:
    res["data"].append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(result.shows)
    })
  
  db.session.close()
  return render_template('pages/search_artists.html', results=res, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)

  past_shows = []
  upcoming_shows = []
  show_assign = None

  for show in artist.shows:
    show_assign = {
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%m/%d/%Y, %H:%M:%S')
    }
    
    if show.start_time <= datetime.now():
      past_shows.append(show_assign)
    else:
      upcoming_shows.append(show_assign)


  artistry = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }



  return render_template('pages/show_artist.html', artist=artistry)

  

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.state.default = artist.state
  form.city.default = artist.city
  form.phone.default = artist.phone
  form.genres.default = artist.genres
  form.name.default = artist.name
  form.seeking_venue.default = artist.seeking_venue
  form.seeking_description.default = artist.seeking_description
  form.facebook_link.default = artist.facebook_link
  form.image_link.default = artist.image_link
  form.website_link.default = artist.website
  form.process()

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  art = Artist.query.get(artist_id)
  try:
    art.name = get_value('name')
    art.genres = get_value('genres')
    art.city = get_value('city')
    art.state = get_value('state')
    art.phone = get_value('phone')
    art.website = get_value('website_link')
    art.seeking_talent = get_value('seeking_talent')
    art.seeking_description = get_value('seeking_description')
    art.facebook_link = get_value('facebook_link')
    art.image_link = get_value('image_link')
    db.session.commit()
    flash('artist ' + request.form['name'] + ' was successfully updated!')

  except:
    flash('An error occurred. artist ' + request.form['name'] + ' could not be updated.', category='error')
    db.session.rollback()

  finally:
    db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  
  venue = Venue.query.get(venue_id)
  print('request.form: ========== ', form.errors)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

  # TODO: populate form with values from venue with ID <venue_id>
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm()

  venue = Venue.query.get(venue_id)
  print('request.form: ========== ', form.errors)

  try:
    venue.name = get_value('name')
    venue.genres = get_value('genres')
    venue.address = get_value('address')
    venue.city = get_value('city')
    venue.state = get_value('state')
    venue.phone = get_value('phone')
    venue.website = get_value('website_link')
    venue.seeking_talent = get_value('seeking_talent')
    venue.seeking_description = get_value('seeking_description')
    venue.facebook_link = get_value('facebook_link')
    venue.image_link = get_value('image_link')
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.', category='error')
    db.session.rollback()
  finally:
    db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))
 
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form=ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(csrf_enabled=True)
  if not form.validate():
    for fieldName, errorMessages in form.errors.items():
      my_form_error(fieldName, errorMessages)
    return redirect(url_for('create_artist_form'))

  new_artist = Artist(
    name = get_value('name'),
    genres = get_value('genres'),
    city = get_value('city'),
    state = get_value('state'),
    phone = get_value('phone'),
    website = get_value('website_link'),
    seeking_venue = get_value('seeking_venue'),
    seeking_description = get_value('seeking_description'),
    facebook_link = get_value('facebook_link'),
    image_link = get_value('image_link')
  )
  try:
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + new_artist.name + ' could not be listed.', category='error')
    db.session.rollback()
  finally:
    db.session.close()
    return redirect(url_for('artists'))
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():

  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  data = []
  shower = {}
  for show in shows:
    shower = {
      'venue_id': show.venue.id,
      'venue_name': show.venue.name,
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.strftime('%d/%m/%Y, %H:%M:%S')
    }
    data.append(shower)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  new_show = Show(
    artist_id = get_value('artist_id'),
    venue_Id = get_value('venue_id'),
    start_time = get_value('start_time')
  )

  try:
    db.session.add(new_show)
    db.session.commit()
    flash('Show ' + request.form['name'] + ' was successfully listed!')
    
  except:
    flash('An error occurred. Show ' + request.form['name'] + ' could not be listed.', category='error')
    db.session.rollback()

  finally:
    db.session.close()
    return redirect(url_for('shows'))
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
