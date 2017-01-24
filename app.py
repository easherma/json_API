import pandas as pd
from flask import Flask, jsonify, json
import folium

app = Flask(__name__)
app.config.from_object(__name__)

def get_stats(client_id):
    url = 'https://data.pa.gov/resource/vsaj-gjez.json?client_id='+str(client_id)
    df_init = pd.read_json(url, convert_dates=['inspection_date'])
    df = df_init.loc[:, ['client_id', 'county', 'inspection_date']]
    df['count'] = 0
    aggs = {
    'client_id': {'client_id':'max'},
    'count': 'count',
    'inspection_date': {
        'min_inspection_date':'min',
        'max_inspection_date': 'max'
    },
    'county': {
        'counties':lambda county: county.unique().tolist()
    }
}
    #pass dict of aggregate values, group by client_id
    data = df.groupby(['client_id']).agg(aggs)
    #clean up the unnecessary hierarchical indexes
    data.columns = data.columns.droplevel(0)
    data = data.reset_index(0, drop=True)

    #order columns
    result = data[['client_id','count','min_inspection_date', 'max_inspection_date', 'counties']]

    return result.iloc[0].to_json()

def get_points(client_id):
    url = 'https://data.pa.gov/resource/vsaj-gjez.json?$select=client_id,latitude,longitude&client_id='+str(client_id)
    print url
    points = pd.read_json(url)
    return points


@app.route('/client_id/<int:client_id>')
def detail_view(client_id):
    return get_stats(client_id)


@app.route('/client_id/<int:client_id>/map')
def make_map(client_id):
    raw_points = get_points(client_id)
    points = raw_points.drop_duplicates()
    client_map = folium.Map(zoom_start=12)
    sw = (points['latitude'].min(), points['longitude'].min())
    ne = (points['latitude'].max(), points['longitude'].max())
    client_map.fit_bounds([sw, ne])

    for point in points.itertuples():
        print point.latitude, point.longitude
        folium.Marker([point.latitude, point.longitude], popup="Client ID:" + str(point.client_id)).add_to(client_map)

    return client_map
