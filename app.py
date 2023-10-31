# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask,jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Var. needed in  the whole app
recent_date =  dt.date(2017, 8, 23)
last_date = recent_date - dt.timedelta(days=365)

@app.route("/")
def Homepage():

    """List of all available api routes"""
    return (

    f"Welcome to my SQL-Alchemy API App <br/>"
    f"Here are all the Available Routes:<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/Start/yyyy-mm-dd<br/>"
    f"/api/v1.0/startend/yyyy-mm-dd/yyyy-mm-dd<br/>"
    f"NOTE: If you don't input an end_date, the api app will calculates stats through this end_date 2017-08-23 <br>" 

    )

@app.route("/api/v1.0/precipitation")
def Precipitation():
    
    # Perform a query to retrieve the data and precipitation scores
    query_retrieve = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= last_date ).\
    filter(measurement.date < recent_date).all()

    # Convert the list to Dictionary
    precipitation_list = []
    for date,prcp  in query_retrieve:
        prec_dict = {}
        prec_dict["date"] = date
        prec_dict["prcp"] = prcp
               
        precipitation_list.append(prec_dict)

    #Return a JSON list 
    return jsonify(precipitation_list)

@app.route("/api/v1.0/stations")
def Stations():
    # List of all the stations
    stations_ = session.query(station.station).order_by(station.station).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(stations_))

    #Return a JSON list 
    return jsonify(all_stations)

@app.route("//api/v1.0/tobs")
def Tobs():
    # List the stations and their counts in descending order.
    stations_activity_count = session.query(measurement.station, func.count(measurement.date)).group_by(measurement.station).\
        order_by(func.count(measurement.date).desc()).all()
    
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    temperature_observation = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == (stations_activity_count[0][0])).\
        filter(measurement.date >= last_date ).\
        filter(measurement.date <= recent_date).all()

    # Convert the list to Dictionary
    temperature = []
    for date,tobs in temperature_observation:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        
        temperature.append(temp_dict)
    #Return a JSON list 
    return jsonify(temperature)

@app.route("/api/v1.0/Start/<start>")
def Start(start, end='2017-08-23'):
    #For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
    Station_temp_summary = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()
    
    # Convert the list to Dictionary
    start_date_temps = []
    for min, avg, max in Station_temp_summary:
        start_date_T_dict = {}
        start_date_T_dict["min_temp"] = min
        start_date_T_dict["max_temp"] = max
        start_date_T_dict["avg_temp"] = avg

        start_date_temps.append(start_date_T_dict) 

    #Return a JSON list 
    return jsonify(start_date_temps)

@app.route("/api/v1.0/startend/<start>/<end>")
def Start_End_Date(start, end='2017-08-23'):
    #For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
    Station_temp_summary = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()
    
    # Convert the list to Dictionary
    start_end_date_temps = []
    for min, avg, max in Station_temp_summary:
        start_end_date_T_dict = {}
        start_end_date_T_dict["min_temp"] = min
        start_end_date_T_dict["max_temp"] = max
        start_end_date_T_dict["avg_temp"] = avg

        start_end_date_temps.append(start_end_date_T_dict) 

    #Return a JSON list 
    return jsonify(start_end_date_temps)
session.close()

if __name__ == '__main__':
    app.run(debug=True)
