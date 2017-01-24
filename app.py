import pandas as pd
from flask import Flask, jsonify, json, render_template, url_for, make_response
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
    #truncate timestamps for display
    result['min_inspection_date']=result['min_inspection_date'].dt.strftime('%d/%m/%Y')
    result['max_inspection_date']=result['max_inspection_date'].dt.strftime('%d/%m/%Y')
    #result = data.to_dict(orient='records')
    #print data.to_dict(orient='records')
    result_json=result.iloc[0].to_json()


    #response=jsonify(json.loads(result_dict))

    #return jsonify(client_id=data1['client_id'], count=data1['count'], min_inspection_date= data['min_inspection_date'], counties=data['counties'])
    return result_json

def get_points(client_id):
    url = 'https://data.pa.gov/resource/vsaj-gjez.json?$select=client_id,latitude,longitude,farm,client&client_id='+str(client_id)
    print url
    points = pd.read_json(url)
    return points

@app.route('/client_id/')
def list_view():
    url='https://data.pa.gov/resource/vsaj-gjez.json?$select=client_id'
    #TODO drop_duplicates
    raw_client_list=pd.read_json(url)
    client_list = raw_client_list.drop_duplicates().to_dict()
    print client_list
    return render_template('client_list.html', client_list=client_list)



@app.route('/client_id/<int:client_id>')
def detail_view(client_id):
    response=json.loads(get_stats(client_id))
    #print response
    data ={
        'client_id':response['client_id'],
        'count': response['count'],
        'min_inspection_date': response['min_inspection_date'],
        'max_inspection_date': response['max_inspection_date'],
        'counties': response['counties']
        }
    print data
    return jsonify(**data)


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
        #html = """<a href="{{ url_for('detail_view', client_id=point.client_id)}}">{{ point.client_id }}</a>"""
        detail_url = url_for('detail_view', client_id=point.client_id)
        #html = '<a href=http://localhost:5000/client_id/265476>goto</a>'
        html = '<embed src=http://localhost:5000%s>' % detail_url


        #m = folium.Map(height=500)
        print html
        iframe = folium.element.IFrame(html=html, width=300, height=100)
        popup = folium.Popup(iframe, max_width=2650)
        folium.Marker([point.latitude, point.longitude], popup=point.farm).add_to(client_map)
        #folium.Marker([point.latitude, point.longitude], popup=html.add_to(client_map)
    f = folium.element.Figure()
    f.html.add_child(folium.element.Element("<h1>%s</h1>" % point.client))
    f.add_child(client_map)
    html_map = client_map.save('./templates/%s_map.html' % client_id)

    return render_template('%s_map.html' % client_id)
