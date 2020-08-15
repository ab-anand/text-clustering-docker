import time
import zipfile
from io import BytesIO

import pandas as pd
import numpy as np
from flask import Flask, request, make_response, send_file
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer
from flasgger import Swagger
from cleaning import cleanse_text

app = Flask(__name__)
app.config['SWAGGER'] = {
    "swagger_version": "2.0",
    # headers are optional, the following are default
    # "headers": [
    #     ('Access-Control-Allow-Origin', '*'),
    #     ('Access-Control-Allow-Headers', "Authorization, Content-Type"),
    #     ('Access-Control-Expose-Headers', "Authorization"),
    #     ('Access-Control-Allow-Methods', "GET, POST, PUT, DELETE, OPTIONS"),
    #     ('Access-Control-Allow-Credentials', "true"),
    #     ('Access-Control-Max-Age', 60 * 60 * 24 * 20),
    # ],
    # another optional settings
    # "url_prefix": "swaggerdocs",
    # "subdomain": "docs.mysite,com",
    # specs are also optional if not set /spec is registered exposing all views
    "specs": [
        {
            "version": "2.0.0",
            "title": "Clustering API",
            "endpoint": 'v2_spec',
            "route": '/v2/spec',
            "description": "This API will help you bin individual data points into groups in a guided and unguided manner"
            # rule_filter is optional
            # it is a callable to filter the views to extract

            # "rule_filter": lambda rule: rule.endpoint.startswith(
            #    'should_be_v1_only'
            # )
        }
    ]
}
Swagger(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/cluster', methods=['POST'])
def cluster():
    """
    This API will help you generate clusters based on keywords present in unstructured text
    Call this api passing the following parameters -
        Dataset Path - Choosing the file
        Column Name based on which clustering needs to be done
        Number of Clusters
    ---
    tags:
      - Clustering API
    parameters:
      - name: dataset
        in: formData
        type: file
        required: true
        description: The fully qualified path of the dataset without the extension.
      - name: col
        in: query
        type: string
        required: true
        description: The column name on which the clustering needs to be done
      - name: no_of_clusters
        in: query
        type: integer
        required: true
        description: The number of clusters
    responses:
     200:
       description: A list of predictions
       schema:
         id: CLUSTERING
         properties:
           prediction:
             type: application/octet-stream
             description: A zipped file of predictions
             default: []
    """

    data = pd.read_csv(request.files['dataset'])
    unstructured = 'text'
    if 'col' in request.args:
        unstructured = request.args.get('col')

    no_of_clusters = 2
    if 'no_of_clusters' in request.args:
        no_of_clusters = int(request.args.get('no_of_clusters'))

    data = data.fillna('NULL')

    data['clean_sum'] = data[unstructured].apply(cleanse_text)
    vectorizer = CountVectorizer(analyzer='word',
                                 stop_words='english')
    counts = vectorizer.fit_transform(data['clean_sum'])
    
    kmeans = KMeans(n_clusters=no_of_clusters)

    data['cluster_num'] = kmeans.fit_predict(counts)
    data = data.drop(['clean_sum'], axis=1)

    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    data.to_excel(writer, sheet_name='Clusters',
                  encoding='utf-8', index=False)

    clusters = []
    for i in range(np.shape(kmeans.cluster_centers_)[0]):
        data_cluster = pd.concat([pd.Series(vectorizer.get_feature_names()),
                                  pd.DataFrame(kmeans.cluster_centers_[i])], axis=1)
        data_cluster.columns = ['keywords', 'weights']
        data_cluster = data_cluster.sort_values(by=['weights'], ascending=False)
        data_clust = data_cluster.head(n=10)['keywords'].tolist()
        clusters.append(data_clust)
    pd.DataFrame(clusters).to_excel(writer, sheet_name='Top_Keywords', encoding='utf-8')

    # Pivot
    data_pivot = data.groupby(['cluster_num'], as_index=False).size()
    data_pivot.name = 'size'
    data_pivot = data_pivot.reset_index()
    data_pivot.to_excel(writer, sheet_name='Cluster_Report', encoding='utf-8')

    # insert chart
    workbook = writer.book
    worksheet = writer.sheets['Cluster_Report']
    chart = workbook.add_chart({'type': 'column'})
    chart.add_series({
        'values': '=Cluster_Report!$D$2:$D'+str(no_of_clusters+1)
    })
    worksheet.insert_chart('E2', chart)

    writer.save()
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        names = ['cluster_output.xlsx']
        files = [output]
        for i in range(len(files)):
            data = zipfile.ZipInfo(names[i])
            data.date_time = time.localtime(time.time())
            data.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(data, files[i].getvalue())
    memory_file.seek(0)

    response = make_response(send_file(memory_file, as_attachment=True,
                                       attachment_filename='cluster_output.zip'))
    response.headers['Content-Disposition'] = 'attachment;filename=cluster_output.zip'
    response.headers['Access-Control-Allow-Origin'] = '*'

    return response


if __name__ == '__main__':
    app.run()
