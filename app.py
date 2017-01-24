import pandas as pd
from flask import Flask, jsonify

app = Flask(__name__)
app.config.from_object(__name__)

# client_id/<here>
# @app.route('/clinet_id/')
# def get_list():
#     url = 'https://data.pa.gov/resource/vsaj-gjez.json'



@app.route('/client_id/<int:client_id>')
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

    return jsonify(result.to_dict())
