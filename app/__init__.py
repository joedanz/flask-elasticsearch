import os
import json
import time
import urllib2
from flask import Flask
from flask import g, render_template, request
from flask_esclient import ESClient

app = Flask(__name__)
#app.config['ELASTICSEARCH_URL'] = 'http://127.0.0.1:9200/'
app.config['ELASTICSEARCH_URL'] = 'http://elasticsearch.ticc.net:9200/'
app.config['DEBUG'] = True
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
          "bookurl": book[1],
          "content": res.read()
        }
        esclient.connection.index("gutenberg","book",body=data,docid=id)
        time.sleep(1)
    esclient.connection.refresh(index="gutenberg")
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form['search']
    #res = esclient.connection.search(indexes=["gutenberg"], query_body={"query": {"match_all": {}}})
    res = esclient.connection.search(indexes=["gutenberg"], query_body={"query": {"multi_match" : { "query": search_term, "fields": ["title", "content"] }}})
    return render_template('results.html', res=res, term=search_term)

@app.route('/search/<search_term>', methods=['GET'])
def search_history(search_term):
    res = esclient.connection.search(indexes=["gutenberg"], query_body={"query": {"multi_match" : { "query": search_term, "fields": ["title", "content"] }}})
    return render_template('results.html', res=res, term=search_term)

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
