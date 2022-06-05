from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import  String, ARRAY


db = SQLAlchemy()

class Venue(db.Model):
    __tablename__ = 'Venues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(ARRAY(String()), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    
    def __repr__(self):
        return f'<Venue {self.name, self.address, self.genres, self.shows}>'



    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    def __repr__(self):
        return f'<Artist {self.id, self.name, self.genres, self.shows}>'
    


    # TODO: implement any missing fields, as a database migration using Flask-Migrate


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime,nullable=False)
    venue = db.relationship('Venue', backref=db.backref('shows'))
    venue_Id = db.Column(db.Integer,db.ForeignKey('Venues.id',onupdate='CASCADE', ondelete='CASCADE'),nullable=False)
    artist = db.relationship('Artist', backref=db.backref('shows'))
    artist_id = db.Column(db.Integer,db.ForeignKey('Artists.id', onupdate='CASCADE', ondelete='CASCADE'),nullable=False)  
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    def __repr__(self):
        return f'<Show {self.id, self.start_time, self.artist}>'