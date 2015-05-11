import os
import json
import urllib2
from flask import Flask
from flask import render_template, request
from elasticsearch import Elasticsearch

app = Flask(__name__)
#app.config['ELASTICSEARCH_URL'] = 'http://127.0.0.1:9200/'
app.config['ELASTICSEARCH_URL'] = 'http://52.4.204.9:9200/'
app.config['DEBUG'] = True
es = Elasticsearch([app.config['ELASTICSEARCH_URL']])

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/seed')
def add_document():
    books = [
        ["Pride and Prejudice","http://d2yzl2mysmkr1m.cloudfront.net/pg1342.txt"],
        ["Alice's Adventures in Wonderland","http://d2yzl2mysmkr1m.cloudfront.net/pg11.txt"],
        ["Adventures of Huckleberry Finn","http://d2yzl2mysmkr1m.cloudfront.net/pg76.txt"],
        ["The Importance of Being Earnest","http://d2yzl2mysmkr1m.cloudfront.net/pg844.txt"],
        ["The Adventures of Tom Sawyer","http://d2yzl2mysmkr1m.cloudfront.net/pg74.txt"],
        ["A Doll's House","http://d2yzl2mysmkr1m.cloudfront.net/pg2542.txt"],
        ["Metamorphosis","http://d2yzl2mysmkr1m.cloudfront.net/pg5200.txt"],
        ["The Yellow Wallpaper","http://d2yzl2mysmkr1m.cloudfront.net/pg1952.txt"],
        ["A Tale of Two Cities","http://d2yzl2mysmkr1m.cloudfront.net/pg98.txt"],
        ["Ulysses","http://d2yzl2mysmkr1m.cloudfront.net/pg4300.txt"],
        ["The Kama Sutra of Vatsyayana","http://d2yzl2mysmkr1m.cloudfront.net/pg27827.txt"],
        ["The Picture of Dorian Gray","http://d2yzl2mysmkr1m.cloudfront.net/pg174.txt"],
        ["Frankenstein; Or, The Modern Prometheus","http://d2yzl2mysmkr1m.cloudfront.net/pg84.txt"],
        ["Grimms' Fairy Tales","http://d2yzl2mysmkr1m.cloudfront.net/pg2591.txt"],
        ["The Prince","http://d2yzl2mysmkr1m.cloudfront.net/pg1232.txt"],
        ["The Adventures of Sherlock Holmes","http://d2yzl2mysmkr1m.cloudfront.net/pg1661.txt"],
        ["A Modest Proposal","http://d2yzl2mysmkr1m.cloudfront.net/pg1080.txt"],
        ["Moby Dick; Or, The Whale","http://d2yzl2mysmkr1m.cloudfront.net/pg2701.txt"],
        ["Great Expectations","http://d2yzl2mysmkr1m.cloudfront.net/pg1400.txt"],
        ["Narrative of the Life of Frederick Douglass, an American Slave","http://d2yzl2mysmkr1m.cloudfront.net/pg23.txt"],
    ]
    es.indices.delete(index="gutenberg", ignore=404)
    es.indices.create(index="gutenberg", ignore=400)
    id = 0
    for book in books:
        id += 1
        req = urllib2.Request(book[1])
        res = urllib2.urlopen(req)
        data = {
          "title": book[0],
          "bookurl": book[1],
          "content": res.read()
        }
        es.index(index="gutenberg",doc_type="book",id=id,body=data)
    es.indices.refresh(index="gutenberg")
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form['search']
    #res = es.search(index="gutenberg", body={"query": {"match_all": {}}})
    try:
        res = es.search(index="gutenberg", size=20, body={"query": {"multi_match" : { "query": search_term, "fields": ["title", "content"] }}})
        return render_template('results.html', res=res, term=search_term)
    except:
        return render_template('health.html', res="ERROR: Can't find any ElasticSearch servers.")

@app.route('/search/<search_term>', methods=['GET'])
def search_history(search_term):
    try:
        res = es.search(index="gutenberg", size=20, body={"query": {"multi_match" : { "query": search_term, "fields": ["title", "content"] }}})
        return render_template('results.html', res=res, term=search_term)
    except:
        return render_template('health.html', res="ERROR: Can't find any ElasticSearch servers.")

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

if __name__ == '__main__':
    app.run(debug=True)
