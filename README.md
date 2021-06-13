# TICKET BOOKING SYSTEM - HAPTIK ASSIGNEMENT

## SETUP and RUN

- Make a `python3` virtual environment and `active` it.
- Run `pip install -r requirements.txt`
- Run `python main.py`
- POSTMAN Import `POSTMAN_COLLECTION.json` in postman to get list of APIs

## API Docs

### `/cities`
#### `GET` - Get City list
#### `POST` - Creates a city
- `{'name' : <CITY NAME>}`

### `/movies`
#### `GET` - Get Movie list
#### `POST` - Creates a movie
- `{'name' : <MOVIE NAME>}`

### `/theaters`
#### `GET` - Get Theater list
#### `POST` - Creates a theater
- `{"name" : "<THEATER NAME>", "city" : "<CITY ID>","num_seats" : "<NUMBER OF SEATS PER HALL>"}`

### `/add-movie/<theater_id>`
#### `POST` - Add movies to theater
- `{"movies" : [<MOVIE IDS>]}`

### `/users`
#### `GET` - Get Users list
#### `POST` - Creates a user
- `{"name" : "<USER NAME>", "email" : <USER EMAIL>}`

### `/user/<user_id>`
#### `GET` - Get User details, including bookings if any.

### `/bookings`
#### `POST` - Ticket booking for a user, based on theater and movie.
- `{"user" : "<USER ID>", "theater" : "<THEATER ID>", "seat_num" : "<SEAT NUMBER>"}`

### `/theaters/<CITY_ID>/<MOVIE_ID>`
#### `GET` - Search theater based on city and movie

### `/highest-bookings/<MONTH-YEAR>`
#### `GET` - Get Top booked theater for this month-year.