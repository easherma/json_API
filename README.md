# json_API
flask example of aggregating data from remote URL
In this case, we are grabbing data Philedalphia's data portal on oil well inspections. **Groovy!**

## Features
* Groups data and creates some summary data for each client: ```/client_id/43513/ ```
* This data also has a geographic component, so we use the Folium library to generate a leaflet map on demand and attach some attributes to it. **Fantastic!**

## Setup

The app uses Python (3.6) and some libraries, most notably Flask and Folium.

* clone the repo
* create a virtualenv.
* ```pip install -r requirements.txt```
* ```export FLASK_APP=app.py``` (set instead of export if on Windows) & ```flask run```

This will run a local server, here are some example endpoints:
* ``` http://localhost:5000/client_id/ ``` a rough list of permalinks by client_id. Clicking on each will take you to the map endpoint for that client.
* ``` http://localhost:5000/client_id/43513 ``` summary data as a JSON object
* ``` http://localhost:5000/client_id/43513/map ``` gets all the points for a given client and makes a map like so:

![Screenshot](static/folium.PNG)

## Testing

```python test.py```
