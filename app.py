#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy.ext.declarative import declarative_base
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)

moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#




class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    website= db.Column(db.String(500))
    seeking_talent= db.Column(db.Boolean)
    seeking_description= db.Column(db.String(),default='')
    shows = db.relationship('Shows', backref="venue", lazy=True)
    
    def __repr__(self):
        return '<Venue {}>'.format(self.name)
    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website= db.Column(db.String(500))
    seeking_venue= db.Column(db.Boolean)
    seeking_description= db.Column(db.String())
    shows = db.relationship('Shows', backref="artist", lazy=True)
    def __repr__(self):
        return '<Artist {}>'.format(self.name)




class Shows(db.Model):
    __tablename__ = 'shows'
    id = db.Column( db.Integer, primary_key=True)            
    venue_id =db.Column( db.Integer, db.ForeignKey('venue.id'),nullable=False)
    artist_id = db.Column( db.Integer, db.ForeignKey('artist.id'),nullable=False)
    show_time = db.Column(db.DateTime, nullable=False)    
    def __repr__(self):
        return '<Shows {}{}>'.format(self.artist_id, self.venue_id)
    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relation_ships and properties, as a database migration.


    


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):

  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale = 'en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
#   data=[{
#     "city": "San Francisco",
#     "state": "CA",
#     "venues": [{
#       "id": 1,
#       "name": "The Musical Hop",
#       "num_upcoming_shows": 0,
#     }, {
#       "id": 3,
#       "name": "Park Square Live Music & Coffee",
#       "num_upcoming_shows": 1,
#     }]
#   }, {
#     "city": "New York",
#     "state": "NY",
#     "venues": [{
#       "id": 2,
#       "name": "The Dueling Pianos Bar",
#       "num_upcoming_shows": 0,
#     }]
#   }]
 
  venues=Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
 
  data=[]
  loc_data =''
  
  for venue in venues:   
    if loc_data == venue.city + venue.state:
        data[len(data)-1]["venues"].append({
             "id": venue.id,
          "name":venue.name,
          "num_upcoming_shows": len(Shows.query.filter(Shows.venue_id==1).filter(Shows.show_time>datetime.now()).all())
            })
    else:    
        
        data.append({
        "city":venue.city,
        "state":venue.state,
        "venues": [{
          "id": venue.id,
          "name":venue.name,
          "num_upcoming_shows":  len(Shows.query.filter(Shows.venue_id==1).filter(Shows.show_time>datetime.now()).all())
        }]
      })
        loc_data = venue.city + venue.state


  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
#     response={
#       "count": 1,
#       "data": [{
#         "id": 2,
#         "name": "The Dueling Pianos Bar",
#         "num_upcoming_shows": 0,
#       }]
#     }
    search_term=request.form.get('search_term', '')
    venues = Venue.query.all()
    data=[]
    count =0
    for venue in venues:
        if search_term.lower() in venue.name.lower():            
            count+=1      
               
            data.append({                    
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": len(Shows.query.filter(Shows.venue_id==1).filter(Shows.show_time>datetime.now()).all()),
                    })
                
    response={
        "count":count,
        "data":data
        }       
              
       
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
 
  past_shows=[]
  upcoming_shows=[]
  shows = Shows.query.join(Artist).filter(Shows.venue_id==venue_id).all()
  for show in shows:
      if (show.show_time>datetime.now()):
          upcoming_shows.append({
               "artist_id": show.artist_id,
               "artist_name": show.artist.name,
               "artist_image_link": show.artist.image_link,
               "start_time": format_datetime(str(show.show_time), format='full')   
              })
      else:
          past_shows.append({
               "artist_id": show.artist_id,
               "artist_name": show.artist.name,
               "artist_image_link": show.artist.image_link,
               "start_time": format_datetime(str(show.show_time), format='full')  
              })
          
          
      
  venue = Venue.query.get(venue_id)
  data={
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
    "upcoming_shows_count": len(upcoming_shows),
      
      }
  
  return render_template('pages/show_venue.html', venue=data)

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
#  form = VenueForm(request.form)
  error=False
  try:
      name=request.form['name']
      city=request.form['city']
      state=request.form['state']
      address=request.form['address']
      phone=request.form['phone']
      genres=request.form['genres']
      facebook_link=request.form['facebook_link']
      venue= Venue(name=name,city=city, state=state,address=address,phone=phone, genres=genres,facebook_link=facebook_link)
      db.session.add(venue)
      db.session.commit()
  except Exception as e:
      error=True
      db.session.rollback()
      print(e)
      print(sys.exc_info)
      
  finally:
      db.session.close()    
      
  if error:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
      
      
      

  # on successful db insert, flash success
 
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        Venue.query.filter_by(venue_id=todo_id).delete()
        db.session.commit()
    except:
      error=True
      db.session.rollback()
      print(sys.exc_info)
      
    finally:
      db.session.close()    
      
    if error:
        flash('An error occurred. Venue with id' + 'venue_id'  + ' could not be deleted.')
    else:
        flash('Venue with id ' + 'venue_id' + ' was successfully deleted!')
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
#   data=[{
#     "id": 4,
#     "name": "Guns N Petals",
#   }, {
#     "id": 5,
#     "name": "Matt Quevedo",
#   }, {
#     "id": 6,
#     "name": "The Wild Sax Band",
#   }]
  data = Artist.query.all() 
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term=request.form.get('search_term', '')
  artists = Artist.query.all()
  data=[]
  count =0
  for artist in artists:
        if search_term.lower() in artist.name.lower():            
            count+=1      
               
            data.append({                    
                    "id": artist.id,
                    "name": artist.name,
                    "num_upcoming_shows": len(Shows.query.filter(Shows.artist_id==artist.id).filter(Shows.show_time>datetime.now()).all()),
                    })
                
            response={
                "count":count,
                "data":data
                }       
           
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
#   data1={
#     "id": 4,
#     "name": "Guns N Petals",
#     "genres": ["Rock n Roll"],
#     "city": "San Francisco",
#     "state": "CA",
#     "phone": "326-123-5000",
#     "website": "https://www.gunsnpetalsband.com",
#     "facebook_link": "https://www.facebook.com/GunsNPetals",
#     "seeking_venue": True,
#     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
#     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
#     "past_shows": [{
#       "venue_id": 1,
#       "venue_name": "The Musical Hop",
#       "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
#       "start_time": "2019-05-21T21:30:00.000Z"
#     }],
#     "upcoming_shows": [],
#     "past_shows_count": 1,
#     "upcoming_shows_count": 0,
#   }
#   data2={
#     "id": 5,
#     "name": "Matt Quevedo",
#     "genres": ["Jazz"],
#     "city": "New York",
#     "state": "NY",
#     "phone": "300-400-5000",
#     "facebook_link": "https://www.facebook.com/mattquevedo923251523",
#     "seeking_venue": False,
#     "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
#     "past_shows": [{
#       "venue_id": 3,
#       "venue_name": "Park Square Live Music & Coffee",
#       "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
#       "start_time": "2019-06-15T23:00:00.000Z"
#     }],
#     "upcoming_shows": [],
#     "past_shows_count": 1,
#     "upcoming_shows_count": 0,
#   }
#   data3={
#     "id": 6,
#     "name": "The Wild Sax Band",
#     "genres": ["Jazz", "Classical"],
#     "city": "San Francisco",
#     "state": "CA",
#     "phone": "432-325-5432",
#     "seeking_venue": False,
#     "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#     "past_shows": [],
#     "upcoming_shows": [{
#       "venue_id": 3,
#       "venue_name": "Park Square Live Music & Coffee",
#       "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
#       "start_time": "2035-04-01T20:00:00.000Z"
#     }, {
#       "venue_id": 3,
#       "venue_name": "Park Square Live Music & Coffee",
#       "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
#       "start_time": "2035-04-08T20:00:00.000Z"
#     }, {
#       "venue_id": 3,
#       "venue_name": "Park Square Live Music & Coffee",
#       "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
#       "start_time": "2035-04-15T20:00:00.000Z"
#     }],
#     "past_shows_count": 0,
#     "upcoming_shows_count": 3,
#   }
  past_shows=[]
  upcoming_shows=[]
  shows = Shows.query.join(Venue).filter(Shows.artist_id==artist_id).all()
  for show in shows:
      if (show.show_time>datetime.now()):
          upcoming_shows.append({
               "venue_id": show.venue_id,
               "venue_name": show.venue.name,
               "venue_image_link": show.venue.image_link,
               "start_time": format_datetime(str(show.show_time), format='full')   
              })
      else:
          past_shows.append({
               "venue_id": show.venue_id,
               "venue_name": show.venue.name,
               "venue_image_link": show.venue.image_link,
               "start_time": format_datetime(str(show.show_time), format='full')   
              })
          
  artist = Artist.query.get(artist_id)
  data={
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
    "upcoming_shows_count": len(upcoming_shows),
      
      }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  
  if artist:
      form.name.data =artist.name
      form.city.data = artist.city
      form.state.data=artist.state
      form.phone.data=artist.phone
      form.genres.data=artist.genres
      form.facebook_link.data=artist.facebook_link
      form.image_link.data=artist.image_link
      form.website.data=artist.website
      form.seeking_venue.data=artist.seeking_venue
      form.seeking_description.data=artist.seeking_description

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error=False
  artist = Artist.query.get(artist_id)
  try:
      artist.name=request.form['name']
      artist.city=request.form['city']
      artist.state=request.form['state']      
      artist.phone=request.form['phone']
      artist.genres=request.form['genres']
      print(1)
      artist.facebook_link=request.form['facebook_link']
      print(2)
      artist.image_link=request.form['image_link']
      print(3)
      artist.website=request.form['website']
      print(4)
 #     print(request.form['seeking_venue'])
      print(5)
      artist.seeking_venue=True if request.form.get['seeking_venue'] else False
      print(artist.seeking_venue)
      artist.seeking_description= request.form['seeking_description']
      
 #     artist= Artist(name=name,city=city, state=state,phone=phone, genres=genres,facebook_link=facebook_link, image_link=image_link, website=website, seeking_venue=seeking_venue, seeking_description=seeking_description)
      db.session.add(artist)
      db.session.commit()
  except Exception as e:
      error=True
      db.session.rollback()
      print(e)
      print(sys.exc_info)
      
  finally:
      db.session.close()    
      
  if error:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
  else:
        flash('Artist ' + request.form['name'] + ' was successfully Edited!')
  

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
      name=request.form['name']
      city=request.form['city']
      state=request.form['state']      
      phone=request.form['phone']
      genres=request.form['genres']
      facebook_link=request.form['facebook_link']
      image_link=request.form['image_link']
      website=request.form['website']
      seeking_venue=request.form['seeking_venue']
      seeking_description=request.form['seeking_description']
      venue= Venue(name=name,city=city, state=state,address=address,phone=phone, genres=genres,facebook_link=facebook_link, image_link=image_link, website=website, seeking_venue=seeking_venue, seeking_description=seeking_description)
      db.session.add(venue)
      db.session.commit()
  except Exception as e:
      error=True
      db.session.rollback()
      print(e)
      print(sys.exc_info)
      
  finally:
      db.session.close()    
      
  if error:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
#   data=[{
#     "venue_id": 1,
#     "venue_name": "The Musical Hop",
#     "artist_id": 4,
#     "artist_name": "Guns N Petals",
#     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
#     "start_time": "2019-05-21T21:30:00.000Z"
#   }, {
#     "venue_id": 3,
#     "venue_name": "Park Square Live Music & Coffee",
#     "artist_id": 5,
#     "artist_name": "Matt Quevedo",
#     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
#     "start_time": "2019-06-15T23:00:00.000Z"
#   }, {
#     "venue_id": 3,
#     "venue_name": "Park Square Live Music & Coffee",
#     "artist_id": 6,
#     "artist_name": "The Wild Sax Band",
#     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#     "start_time": "2035-04-01T20:00:00.000Z"
#   }, {
#     "venue_id": 3,
#     "venue_name": "Park Square Live Music & Coffee",
#     "artist_id": 6,
#     "artist_name": "The Wild Sax Band",
#     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#     "start_time": "2035-04-08T20:00:00.000Z"
#   }, {
#     "venue_id": 3,
#     "venue_name": "Park Square Live Music & Coffee",
#     "artist_id": 6,
#     "artist_name": "The Wild Sax Band",
#     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#     "start_time": "2035-04-15T20:00:00.000Z"
#   }]
  data=[]
  shows = Shows.query.all()
  
  for show in shows: 
      venue = Venue.query.filter_by(id = show.venue_id).with_entities(Venue.name).one() 
      artist = Artist.query.filter_by(id = show.artist_id).with_entities(Artist.name,Artist.image_link).one()
     # format_datetime(value, format='medium')
           
      data.append({
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": format_datetime(str(show.show_time), format='full')
            })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.isoformat(timespec='milliseconds')
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
