from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime
import random
import json
import threading
import logging
logging.basicConfig(filename="app.log", filemode="w+", level="DEBUG", format='%(asctime)s - %(module)s - %(funcName)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)

######### DATABASE SIMULATIONS START #########

# MINIMAL DATABASE FIELDS ARE USED TO GET ALL THE REQUIERED DATA IN ASSIGNMENT

######### TABLES #########
app.config['cities'] = {}
app.config['theaters'] = {}
app.config['users'] = {}
app.config['bookings'] = {}
app.config['movies'] = {}
######### TABLES #########

######### DATA CLASSES #########

# Parent Class for CRUD operations
class CRUD:

    @classmethod
    def create(cls, data):
        params = cls.__init__.__code__.co_varnames
        kwrgs = {}
        for param in params:
            if not param=='self':
                kwrgs[param] = data[param]
        return cls(**kwrgs).save()

    @classmethod
    def get_all(cls):
        return [table_data.serialize() for table_data in app.config[cls.table_name].values()]

    @classmethod
    def get_by_id(cls, id):
        return app.config[cls.table_name][id].serialize()

    @classmethod
    def get_obj_by_id(cls, id):
        return app.config[cls.table_name][id]

    @classmethod
    def update(cls, id, data):
        obj = app.config[cls.table_name][id]
        for k,v in data.items():
            setattr(obj, k, v)

    @classmethod
    def delete(cls, id):
        del app.config[cls.table_name][id]

class City(CRUD):
    table_name = 'cities'

    def __init__(self, name):
        self.id = None
        self.name = name
        self.theaters = [] # ONE TO MANY with THEATERS

    def save(self):
        self.id = str(uuid.uuid4())
        app.config[self.table_name][self.id] = self
        return self.id

    def serialize(self):
        return {
            "id":self.id,
            "name":self.name
        }

    # def __repr__(self):
    #     return f"{self.name}"

class Theater(CRUD):
    table_name = 'theaters'

    def __init__(self, name, city, num_seats):
        self.id = None
        self.name = name
        self.city = city # FORIEGN KEY TO CITY
        self.seats = num_seats
        self.movies = {} # MANY TO MANY with MOVIES

    def save(self):
        self.id = str(uuid.uuid4())
        app.config[self.table_name][self.id] = self
        app.config[City.table_name][self.city].theaters.append(self)
        return self.id

    def add_movie(self, movie_id):
        self.movies[movie_id] = self.seats
        app.config[Movie.table_name][movie_id].theaters.append(self)

    def serialize(self):
        return {
            "id":self.id,
            "name":self.name,
            #"seats":self.seats,
            "city":app.config[City.table_name][self.city].serialize(),
            "movies":[{**app.config[Movie.table_name][movie].serialize(), **{'seats_left' : seats}} for movie, seats in self.movies.items()]
        }

    # def __repr__(self):
    #     return f"{self.name} - {self.movies}"

class Movie(CRUD):
    table_name = 'movies'

    def __init__(self, name):#, genre, duration):
        self.id = None
        self.name = name
        #self.genre = genre
        #self.duration = duration
        self.theaters = [] # MANY TO MANY with THEATERS

    def save(self):
        self.id = str(uuid.uuid4())
        app.config[self.table_name][self.id] = self
        return self.id

    def serialize(self):
        return {
            "id":self.id,
            "name":self.name
        }
    
    # def __repr__(self):
    #     return self.name

class Booking(CRUD):
    table_name = 'bookings'

    def __init__(self, user, theater, movie, seat_num):
        self.id = None
        self.user = user # FORIEGN KEY TO USER
        self.theater = theater # FORIEGN KEY TO THEATER
        self.movie = movie # FORIEGN KEY TO MOVIE
        self.booking_date = datetime.now()
        self.seat_num = seat_num

    def save(self):
        self.id = str(uuid.uuid4())
        app.config[self.table_name][self.id] = self
        app.config[User.table_name][self.user].bookings.append(self)
        Theater.get_obj_by_id(self.theater).movies[self.movie] = Theater.get_obj_by_id(self.theater).movies[self.movie] - 1
        return self.id

    def serialize(self):
        return {
            "id":self.id,
            "user":self.user,
            "theater":app.config[Theater.table_name][self.theater].serialize(),
            "movie":app.config[Movie.table_name][self.movie].serialize(),
            "booking_date":self.booking_date.strftime("%Y-%m-%d %H:%M:%S"),
            "seat_num":self.seat_num
        }

    # def __repr__(self):
    #     return f"{self.user} - {self.theater} - {booking_date} - {self.seat_num}"

class User(CRUD):
    table_name = 'users'

    def __init__(self, name, email):
        self.id = None
        self.name = name
        self.email = email
        self.bookings = [] # ONE TO MANY TO BOOKING

    def save(self):
        self.id = str(uuid.uuid4())
        app.config[self.table_name][self.id] = self
        return self.id

    def serialize(self):
        return {
            "id":self.id,
            "name":self.name,
            "bookings":[booking.serialize() for booking in self.bookings]
        }
    
    # def __repr__(self):
    #     return self.name

######### DATA CLASSES #########

######### TEST DATA #########
movies = ['Star Trek', 'Nightmare on Elm Street', 'Contact', 'Star Wars', 'Batman', 'Sholey', 'Master (Tamil)']

for movie in movies:
    Movie(movie).save()
movies = list(app.config['movies'].keys())

data = {'New Delhi' : {'pvr vegas mall' : [movies[0],movies[1],movies[5]], 'pvr vikaspuri' : [movies[1], movies[2]]}, 'Chandigarh' : {'pvr dlf,panchkula' : [movies[5],movies[6]], 'pvr sector 17' : [movies[0], movies[3]], 'pvr sector 19' : [movies[4], movies[5]]}, 'Mumbai' : {'pvr pheonix' : [movies[0],movies[6]], 'pvr icon' : [movies[1], movies[5]], 'pvr le reve' : [movies[2], movies[4]], 'pvr goregaon west' : [movies[3]]}}

for key, value in data.items():
    city = City(key).save()
    for theater_name, movies in value.items():
        theater = Theater(theater_name,city,random.randint(90, 100)).save()
        for movie in movies:
            app.config['theaters'][theater].add_movie(movie)

######### TEST DATA #########

######### DATABASE SIMULATIONS END #########

# Send booking confirmation email to user
def send_booking_confirmation_email(booking):
    user = app.config[User.table_name][booking["user"]]
    threading.Thread(target=logging.debug, args=[f'Email sent to user {user.name} at {user.email}, for booking on {booking["booking_date"]}, movie {booking["movie"]["name"]} at {booking["theater"]["name"]}']).start()

@app.route('/cities', methods=['GET', 'POST'])
def cities():
    if request.method=='GET':
        return jsonify(City.get_all())
    else:
        data = request.json
        id = City.create(data)
        return jsonify(City.get_by_id(id))

@app.route('/movies', methods=['GET', 'POST'])
def movies():
    if request.method=='GET':
        return jsonify(Movie.get_all())
    else:
        data = request.json
        id = Movie.create(data)
        return jsonify(Movie.get_by_id(id))

@app.route('/theaters', methods=['GET', 'POST'])
def theaters():
    if request.method=='GET':
        return jsonify(Theater.get_all())
    else:
        data = request.json
        id = Theater.create(data)
        return jsonify(Theater.get_by_id(id))

@app.route('/add-movie/<theater_id>', methods=['POST'])
def add_movie(theater_id):
    movie_ids = request.json['movies']
    try:
        theater = app.config[Theater.table_name][theater_id]
        for movie in movie_ids:
            theater.add_movie(movie)
        return jsonify(Theater.get_by_id(theater_id))
    except:
        return {"msg" : "Something went wrong"}, 500

@app.route('/users', methods=['GET','POST'])
def users():
    if request.method=='GET':
        return jsonify(User.get_all())
    else:
        data = request.json
        id = User.create(data)
        return jsonify(User.get_by_id(id))

@app.route('/user/<id>', methods=['GET'])
def get_user_detail(id):
    try:
        return jsonify(User.get_by_id(id))
    except:
        return {"msg" : "Something went wrong"}, 500

@app.route('/bookings', methods=['POST'])
def bookings():
    data = request.json
    id = Booking.create(data)
    send_booking_confirmation_email(app.config[Booking.table_name][id].serialize())
    return jsonify(Booking.get_by_id(id))

# GET HIGHEST BOOKED THEATER (Complexity will on O(n) as it is not indexedin DB(simulated).)
@app.route('/highest-bookings/<month_year>', methods=['GET'])
def highest_bookings(month_year):
    theater_freq = {}
    for booking in app.config[Booking.table_name].values():
        #import pdb; pdb.set_trace();
        if month_year==booking.booking_date.strftime("%m-%Y"):
            if booking.theater in theater_freq:
                theater_freq[booking.theater] = theater_freq[booking.theater]+1
            else:
                theater_freq[booking.theater] = 1
    result = {'theater':'', "bookings":0}
    for theater, bookings in theater_freq.items():
        if bookings > result['bookings']:
            result = {'theater':theater, "bookings":bookings}
    reresult['theater'] = Theater.get_by_id(reresult['theater'])
    return jsonify(result)

# GET THEATERS BASED ON CITY AND MOVIE
@app.route('/theaters/<city_id>/<movie_id>', methods=['GET'])
def city_movie_theaters(city_id, movie_id):
    try:
        theaters = []
        for theater in City.get_obj_by_id(city_id).theaters:
            if movie_id in theater.movies:
                theaters.append(theater.serialize())
        return jsonify(theaters)
    except:
        return {"msg" : "Something went wrong"}, 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5001', use_reloader=True)