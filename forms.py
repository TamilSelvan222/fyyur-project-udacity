from datetime import datetime
import re
from flask_wtf import FlaskForm
from wtforms import DateField, FieldList, FormField, StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, SubmitField, TimeField, ValidationError
from wtforms.validators import DataRequired, URL
from enums import State,Genre


def is_valid_phone(number):
    '''validate phonenumber like:
    1234567890 - no space
    123.456.7890 - dot separator
    123-456-7890 - dash separator
    123 456 7890 - space separator
    patterns:
    000 = [0-9]{3}
    0000= [0-9]{4}
    -. = ?[-. ]
    '''
    regex = re.compile(r'^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')
    return regex.match(number)

def validate_phone(self,field):
    if not is_valid_phone(field.data):
        raise ValidationError('Invalid phone number.')

def validate_genres(self,field):
    if not set(field.data).issubset(dict(Genre.choices()).keys()):
       raise ValidationError('Invalid genres.')

def validate_state(self,field):
    if field.data not in dict(State.choices()).keys():
       raise ValidationError('Invalid State.')

def validate(self, **Kwargs):
    return super(VenueForm,self).validate(**Kwargs)
    
def validate(self, **Kwargs):
    return super(ArtistForm,self).validate(**Kwargs)
    
class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(),validate_state],
        choices=State.choices()
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone',validators=[DataRequired(),validate_phone]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired(),validate_genres],
        choices=Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website_link = StringField(
        'website_link'
    )

    seeking_talent = BooleanField( 'Looking for Talent' )

    seeking_description = StringField(
        'seeking_description'
    )



class ArtistForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(),validate_state],
        choices=State.choices()
    )
    phone = StringField(
        'phone',validators=[DataRequired(),validate_phone]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired(),validate_genres],
        choices=Genre.choices()
     )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[URL()]
     )

    website_link = StringField(
        'website_link'
     )

    seeking_venue = BooleanField('Looking for Venues')

    seeking_description = StringField(
            'seeking_description'
     )

class AvailabilityEntryForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    start_time = TimeField('Start Time', format='%H:%M', validators=[DataRequired()])

class AvailabilityForm(FlaskForm):
    entries = FieldList(FormField(AvailabilityEntryForm), min_entries=1)
    submit = SubmitField('Update Availability')


class SearchForm(FlaskForm):
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    submit = SubmitField('Search') 