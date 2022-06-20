#import datetime, NumPy, and Pandas
import datetime as dt
import numpy as np
import pandas as pd
#SQLAlchemy dependencies 
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
# import the dependencies that we need for Flask
from flask import Flask, jsonify

#Set Up the Database

#access and query our SQLite database file
engine = create_engine("sqlite:///hawaii.sqlite")
#reflect the database into our classes
Base = automap_base()
Base.prepare(engine, reflect=True)
#create a variable for each of the classes
Measurement = Base.classes.measurement
Station = Base.classes.station
#create a session link from Python to our database 
session = Session(engine)

#Set Up Flask

# create a Flask application called "app".
app = Flask(__name__)

#Create the Welcome Route

#define the welcome route 
@app.route("/")
# create a function where the return statement will have f-strings as a reference to all of the other routes
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')

#Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    #calculates the date one year ago from the most recent date in the database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #write a query to get the date and precipitation for the previous year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
      filter(Measurement.date >= prev_year).all()
    #create a dictionary with the date as the key and the precipitation as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

#Stations Route
@app.route("/api/v1.0/stations")
def stations():
    #create a query that will allow us to get all of the stations in our database
    results = session.query(Station.station).all()
    #convert our unraveled results into a list
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

#Monthly Temperature Route
@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps=temps)
    
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)