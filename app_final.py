import numpy as np
import datetime as dt
import sqlalchemy

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


engine = create_engine("sqlite:///hawaii.sqlite")

#Database to new model
Base = automap_base()

#Reflect tables
Base.prepare(engine, reflect=True)

#Reference to tables
Measurement=Base.classes.measurement
Station=Base.classes.station

#Flask setup
app = Flask(__name__)


#Flask routes

#List of all available routes
@app.route("/")
def home():
    return(
        f"Welcome!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/<start><br/>"
        f"/api/v1.0/temp/<start>/<end>"
    )

#Dictionary of date and precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    session=Session(engine)
    results=session.query(Measurement.date,Measurement.prcp).all()
    session.close()

    all_precipitation=[]
    for date, prcp in results:
        precipitation_dict={}
        precipitation_dict[date]= prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

#List of all stations
@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)

    results=session.query(Measurement.station).distinct().all()

    session.close()

    all_stations=list(np.ravel(results))

    return jsonify(all_stations)

#List of temperature for the previous year of the most-active station
@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)

    query_date=dt.date(2017, 8, 23)-dt.timedelta(days=365)

    results=session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= query_date,Measurement.station=="USC00519281").all()

    session.close()

    last_yr_temp=list(np.ravel(results))

    return jsonify(last_yr_temp)

#List of min.,avg. and max temp for start date range and/or start-end date range
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def t_start_end(start=None, end=None):

    session=Session(engine)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()

        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)

    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    session=Session(engine)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    temps = list(np.ravel(results))
    return jsonify(temps)

    

if __name__ == "__main__":
    app.run(debug=True)

