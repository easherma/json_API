import pandas as pd
from flask import Flask, jsonify, json, render_template, url_for, make_response
import folium

app = Flask(__name__)
app.config.from_object(__name__)

def get_stats(client_id):
    """
    Use Socrata API to query data, aggregate with pandas
    """
    url = 'https://data.pa.gov/resource/vsaj-gjez.json?client_id='+str(client_id)
    df_init = pd.read_json(url, convert_dates=['inspection_date'], dtype=False)
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
    result = data[['client_id', 'count', 'min_inspection_date', 'max_inspection_date', 'counties']]
    #truncate timestamps for display
    result['min_inspection_date'] = result['min_inspection_date'].dt.strftime('%m/%d/%Y')
    result['max_inspection_date'] = result['max_inspection_date'].dt.strftime('%m/%d/%Y')
    #cast count to int (Flask dosen't like numpy int64)
    result['count'] = result['count'].astype(int)
    result_json = result.iloc[0]
    return result_json

def get_points(client_id):
    """
    retrive spatial data and some attributes for a given client
    """
    url = 'https://data.pa.gov/resource/vsaj-gjez.json?$select=client_id,latitude,longitude,farm,client&client_id='+str(client_id)
    points = pd.read_json(url)
    return points

@app.route('/client_id/')
def list_view():
    """
    'browseable' list of map view hyperlink for each client
    """
    url = 'https://data.pa.gov/resource/vsaj-gjez.json?$select=client_id'
    raw_client_list = pd.read_json(url)
    client_list = raw_client_list.drop_duplicates().to_dict()
    return render_template('client_list.html', client_list=client_list)

@app.route('/client_id/<int:client_id>')
def detail_view(client_id):
    """
    display summary data for a client
    """
    stats = get_stats(client_id)
    #return render_template('detail_view.html', detail_view= json_format)
    return  jsonify(json.loads(stats.to_json()))

@app.route('/client_id/<int:client_id>/map')
def make_map(client_id):
    """
    generates html of a leaflet map of client data
    """
    raw_points = get_points(client_id)
    points = raw_points.drop_duplicates()
    client_map = folium.Map(zoom_start=12)
    south_west_bound = (points['latitude'].min(), points['longitude'].min())
    north_east_bound = (points['latitude'].max(), points['longitude'].max())
    client_map.fit_bounds([south_west_bound, north_east_bound])

    for point in points.itertuples():
        detail_url = url_for('detail_view', client_id=point.client_id)
        html = '<embed src=http://localhost:5000%s>' % detail_url
        iframe = folium.element.IFrame(html=html, width=300, height=100)
        folium.Marker([point.latitude, point.longitude], popup=point.farm).add_to(client_map)

    map_container = folium.element.Figure()
    map_container.html.add_child(folium.element.Element("<h1>%s</h1>" % point.client))
    map_container.add_child(client_map)
    html_map = client_map.save('./templates/%s_map.html' % client_id)

    return render_template('%s_map.html' % client_id)
