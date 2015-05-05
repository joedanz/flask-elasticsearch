import os
import json
import urllib2
from flask import Flask
from flask import g, render_template, request
from flask_esclient import ESClient

app = Flask(__name__)
#app.config['ELASTICSEARCH_URL'] = 'http://127.0.0.1:9200/'
app.config['ELASTICSEARCH_URL'] = 'http://Hackerati-ES-LB-US-East-741975459.us-east-1.elb.amazonaws.com:9200/'
esclient = ESClient(app)

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/seed')
def add_document():
    esclient.connection.delete_index("gutenberg")
    include('booklist.py')
    id = 0
    for book in g.books:
        id += 1
        req = urllib2.Request(book[1])
        res = urllib2.urlopen(req)
        data = {
          "title": book[0],
          "url": book[1],
          "content": res.read()
        }
        esclient.connection.index("gutenberg","book",body=data,docid=id)
        esclient.connection.refresh(index="gutenberg")
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form['search']
    #res = esclient.connection.search(indexes=["gutenberg"], query_body={"query": {"match_all": {}}})
    res = esclient.connection.search(indexes=["gutenberg"], query_body={"query": {"multi_match" : { "query": search_term, "fields": ["title", "content"] }}})
    return render_template('results.html', res=res)

@app.route('/search/<search_term>', methods=['GET'])
def search_history(search_term):
    res = esclient.connection.search(indexes=["gutenberg"], query_body={"query": {"multi_match" : { "query": search_term, "fields": ["title", "content"] }}})
    return render_template('results.html', res=res)

@app.route('/health')
def health():
    urlToCall = app.config['ELASTICSEARCH_URL'] + '_cluster/health?pretty=true'
    try:
        req = urllib2.Request(urlToCall)
        res = urllib2.urlopen(req)
        return render_template('health.html', res=res.read())
    except:
        return render_template('health.html', res="ERROR: Can't find any ElasticSearch servers.")

@app.route('/history')
def history():
    return render_template('history.html')

def include(filename):
    if os.path.exists(filename):
        execfile(filename)

if __name__ == '__main__':
    app.run(debug=True)
