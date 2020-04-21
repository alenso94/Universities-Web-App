from flask import Flask, request,jsonify, abort
from cassandra.cluster import Cluster
import json
import requests
import requests_cache
from json2html import *

cluster = Cluster(contact_points=['172.17.0.2'],port=9042)
session = cluster.connect()
requests_cache.install_cache('universities_api_cache', backend='sqlite', expire_after=36000)

app = Flask(__name__)

@app.route('/')
def hello():
    return('<h1>Welcome to Universities Data<!!/h1>')

@app.route('/universities', methods=['GET'])
def viewalluniversities():
    rows = session.execute( """Select * From Universities.stats""")
    result=[]
    for r in rows:
        result.append(
            {
                "Id":r.id,
                "Domain":r.domains,
                "Country":r.country,
                "WebPages":r.web_pages,
                "Name":r.name,
                "AlphaTwoCode":r.alpha_two_code
            }
        )
    if len(result) == 0:
        abort(404, description="No data found!!")
    else:
        return jsonify(result)

@app.route('/universities/name/<name>', methods=['GET'])
def viewunibyname(name):
    rows = session.execute( """Select * From Universities.stats where name='{}'""".format(name))
    result=[]
    for r in rows:
        result.append(
            {
                "Id":r.id,
                "Domain":r.domains,
                "Country":r.country,
                "WebPage":r.web_pages,
                "Name":r.name,
                "AlphaTwoCode":r.alpha_two_code
            }
        )
    if len(result) == 0:
        abort(404, description="No such University!! Please check the spelling!!")
    else:
        return jsonify(result)

@app.route('/universities/country/<country>', methods=['GET'])
def viewunibycountry(country):
    rows = session.execute( """Select * From Universities.stats where country='{}' ALLOW FILTERING""".format(country))
    result=[]
    for r in rows:
        result.append(
            {
                "Id":r.id,
                "Domain":r.domains,
                "Country":r.country,
                "WebPage":r.web_pages,
                "Name":r.name,
                "AlphaTwoCode":r.alpha_two_code
            }
        )
    if len(result) == 0:
        abort(404, description="No such Country!! Please check the spelling!!")
    else:
        return jsonify(result)

@app.route('/universities/all', methods=['GET'])
def viewalluni():
    universities_url_template ='http://universities.hipolabs.com/search'
    resp = requests.get(universities_url_template)
    if resp.ok:
        response=resp.json()
        return json2html.convert(response)
    else:
        print(resp.reason)

@app.route('/universities/all/view/<country>/<name>', methods=['GET'])
def viewallunibycountryandname(country,name):
    universities_url_template ='http://universities.hipolabs.com/search?&country={co}&name={na}'
    universities_url = universities_url_template.format(co = country, na = name)
    resp = requests.get(universities_url)
    if resp.ok:
        response=resp.json()
        return json2html.convert(response)
    else:
        print(resp.reason)

@app.route('/universities', methods = ['POST'])
def adduniversity():
    rows = session.execute( """Select * From Universities.stats where name='{}' ALLOW FILTERING""".format(request.json['name']))
    result=[]
    for r in rows:
        result.append(
            {
                "Id":r.id,
                "Domain":r.domains,
                "Country":r.country,
                "WebPage":r.web_pages,
                "Name":r.name,
                "AlphaTwoCode":r.alpha_two_code
            }
        )
    if len(result) != 0:
        abort(406, description="{} already exist in the database!!".format(request.json['name']))
    elif not request.json or not 'id' in request.json \
            or not 'domains' in request.json \
            or not 'country' in request.json \
            or not 'web_pages' in request.json \
            or not 'name' in request.json \
            or not 'alpha_two_code' in request.json:
        abort(400, 'Not enough parameters!! Check your parameters!!')
    else:
        session.execute("""INSERT INTO Universities.stats(id,domains,country,web_pages,name,alpha_two_code) VALUES({},'{}','{}','{}','{}','{}')""".format(int(request.json['id']), request.json['domains'], request.json['country'],  request.json['web_pages'],  request.json['name'],  request.json['alpha_two_code']))
        return jsonify({'message':'University added: /universities/{}'.format(request.json['name'])}),201

@app.route('/universities', methods = ['PUT'])
def updateuniversity():
    rows = session.execute( """Select * From Universities.stats where name='{}' ALLOW FILTERING""".format(request.json['name']))
    result=[]
    for r in rows:
        result.append(
            {
                "Id":r.id,
                "Domain":r.domains,
                "Country":r.country,
                "WebPage":r.web_pages,
                "Name":r.name,
                "AlphaTwoCode":r.alpha_two_code
            }
        )
    if len(result) == 0:
        abort(404, description="{} does not exist in the database!! Please check the spelling!!".format(request.json['name']))
    elif not request.json or not 'web_pages' in request.json \
            or not 'name' in request.json:
        abort(400, 'Not enough parameters!! Check your parameters!!')
    else:
        session.execute("""UPDATE Universities.stats SET web_pages='{}' WHERE name='{}'""".format(request.json['web_pages'], request.json['name']))
        return jsonify({'message':'University updated: /universities/{}'.format(request.json['name'])}),200

@app.route('/universities', methods = ['DELETE'])
def deleteuniversity():
    rows = session.execute( """Select * From Universities.stats where name='{}' ALLOW FILTERING""".format(request.json['name']))
    result=[]
    for r in rows:
        result.append(
            {
                "Id":r.id,
                "Domain":r.domains,
                "Country":r.country,
                "WebPage":r.web_pages,
                "Name":r.name,
                "AlphaTwoCode":r.alpha_two_code
            }
        )
    if len(result) == 0:
        abort(404, description="{} does not exist in the database!! Please check the spelling!!".format(request.json['name']))
    else:
        session.execute("""DELETE FROM Universities.stats WHERE name='{}'""".format(request.json['name']))
        return jsonify({'message':'University deleted: /universities/{}'.format(request.json['name'])}),200


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

@app.errorhandler(400)
def resource_not_found(e):
    return jsonify(error=str(e)), 400

@app.errorhandler(406)
def not_acceptable(e):
    return jsonify(error=str(e)), 406

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, ssl_context=('cert.pem','key.pem'))
