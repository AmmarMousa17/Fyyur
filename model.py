from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import _datetime
from flask_moment import Moment
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

# Base = declarative_base()
db = SQLAlchemy()


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

# Venue Model with serialization
class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(150))
    state = db.Column(db.String(150))
    address = db.Column(db.String(150))
    genres = db.Column(db.String(150))
    phone = db.Column(db.String(150))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(150))
    website = db.Column(db.String(150))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    artists = db.relationship('Artist', secondary='shows')#Many to many relationship wit assocuition table
    shows = db.relationship('Show', backref=('venues'))



    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'address': self.address,
            'phone': self.phone,
            'image_link': self.image_link,
            'genres': self.genres.split(','),
            'facebook_link': self.facebook_link,
            'website': self.website,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
        }


    def todict_upcoming_shows(self):
        return {'id': self.id,
                'name': self.name,
                'city': self.city,
                'state': self.state,
                'phone': self.phone,
                'address': self.address,
                'image_link': self.image_link,
                'genres': self.genres.split(','),
                'facebook_link': self.facebook_link,
                'website': self.website,
                'seeking_talent': self.seeking_talent,
                'seeking_description': self.seeking_description,
                'num_shows': Show.query.filter(
                    Show.start_time > datetime.now(),
                    Show.venue_id == self.id)
                }

    def todict_shows(self):
        upcomingshows = Show.query.filter(
            Show.start_time > datetime.now(),
            Show.artist_id == self.id).all()
        pastshows = Show.query.filter(
            Show.start_time < datetime.now(),
            Show.artist_id == self.id).all()
        return {'id': self.id,
                'name': self.name,
                'city': self.city,
                'state': self.state,
                'phone': self.phone,
                'address': self.address,
                'genres': self.genres,
                'image_link': self.image_link,
                'facebook_link': self.facebook_link,
                'seeking_talent': self.seeking_talent,
                'seeking_description': self.seeking_description,
                'website': self.website,

                'upcoming_shows': [show.todict_show_venue() for show in upcomingshows],
                'past_shows': [show.todict_show_venue() for show in pastshows],
                'upcoming_shows_count': len(db.session.query(Show).join(Artist).filter
                                            (Show.venue_id == self.id).filter(Show.start_time > datetime.now()).all()),
                'past_shows_count': len(db.session.query(Show).join(Artist).filter
                                        (Show.venue_id == self.id).filter(Show.start_time < datetime.now()).all())
                }

    def __repr__(self):
        return f'<venues {self.id} {self.name}>'

# Artist

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(150))
    state = db.Column(db.String(150))
    phone = db.Column(db.String(150))
    genres = db.Column(db.String(150))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(150))
    website = db.Column(db.String(150))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    venues = db.relationship('Venue', secondary='shows') #Many to many relationship wit assocuition table
    shows = db.relationship('Show', backref=('artists'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'genres': self.genres.split(','),
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'website': self.website,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
        }

    def todict_shows(self):
        upcomingshows = Show.query.filter(
            Show.start_time > datetime.now(),
            Show.artist_id == self.id).all()
        pastshows = Show.query.filter(
            Show.start_time < datetime.now(),
            Show.artist_id == self.id).all()
        return {'id': self.id,
                'name': self.name,
                'city': self.city,
                'state': self.state,
                'phone': self.phone,
                'genres': self.genres,
                'image_link': self.image_link,
                'facebook_link': self.facebook_link,
                'seeking_venue': self.seeking_venue,
                'seeking_description': self.seeking_description,
                'website': self.website,

                'upcoming_shows': [show.todict_show_venue() for show in upcomingshows],
                'past_shows': [show.todict_show_venue() for show in pastshows],
                'upcoming_shows_count': len(db.session.query(Show).join(Artist).filter
                                            (Show.venue_id == self.id).filter(Show.start_time > datetime.now()).all()),
                'past_shows_count': len(db.session.query(Show).join(Artist).filter
                                        (Show.venue_id == self.id).filter(Show.start_time < datetime.now()).all())
                }

    def __repr__(self):
        return f'<venues {self.id} {self.name}>'

# Show

class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    venue = db.relationship('Venue')
    artist = db.relationship('Artist')

    def __repr__(self):
        return '<shows {}{}>'.format(self.artist_id, self.venue_id)

    def todict_show_venue(self):
        return {'id': self.id,
                'venue': [v.to_dict() for v in Venue.query.filter(Venue.id == self.venue_id).all()][0],
                'artist': [a.to_dict() for a in Artist.query.filter(Artist.id == self.artist_id).all()][0],
                'start_time': self.start_time.strftime("%m/%d/%Y, %H:%M:%S")
                }


engine = create_engine('postgres://Ammar@localhost:5432/fyyur')

db.metadata.create_all(engine)
