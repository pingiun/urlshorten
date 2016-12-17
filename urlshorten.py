import random
import re
import os

from flask import Flask, redirect
from flask_restful import reqparse, Resource, Api

import sqlalchemy.exc
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('url', required=True, help="The long url to shorten")
parser.add_argument('secret', type=bool, help="Make a secret URL")

_url_regex = re.compile(r'^((https?|ftp):\/\/[^\s/$.?#].[^\s]*)$')

_text = 'DsU~CF6hjX2u5QpolMWaNmLr8keVqzR0_3tn7HdOyJbZ.TI1AgfExB4SP9GiwYcvK-'
_base = len(_text)

def number_to_text(number):
	text = ""
	if number == 0:
		text += _text[0]
	while number:
		text += _text[number % _base]
		number = number // _base
	return text

def text_to_number(tekst):
	number = 0
	for i, character in enumerate(tekst):
		number += _text.index(character) * _base ** i
	return number

def valid_url(url):
	return bool(_url_regex.match(url))

engine = create_engine(os.environ["DB_URL"], echo=True)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

class ShortenedUrl(Base):
	__tablename__ = "shortenedurls"

	id = Column(Integer, primary_key=True)
	url = Column(String)

	def __repr__(self):
		return "/{} = {}".format(number_to_text(self.id), self.url)

class SecretShortenedUrl(Base):
	__tablename__ = "secreturls"

	id = Column(String, primary_key=True)
	url = Column(String)

	def __repr__(self):
		return "/{} = {}".format(self.id, self.url)

Base.metadata.create_all(bind=engine)

def get_url(url_id):
	if url_id.startswith('+'):
		return get_secret_url(url_id)

	urlid = text_to_number(url_id)
	url = ShortenedUrl.query.filter(ShortenedUrl.id == urlid).first()
	return url.url

def add_url(url):
	newurl = ShortenedUrl(url=url)
	db_session.add(newurl)
	db_session.commit()
	if number_to_text(newurl.id) == 'urls':
		return -1
	return newurl.id

def get_secret_url(url_id):
	url = SecretShortenedUrl.query.filter(SecretShortenedUrl.id == url_id).first()
	return url.url

def add_secret_url(url):
	urlid = ""
	tries = 0
	length = 5
	while SecretShortenedUrl.query.filter(SecretShortenedUrl.id == urlid).first() or urlid == "":
		if tries > 10:
			length += 1
		urlid = '+' + ''.join([random.choice(_text) for _ in range(length)])
		tries += 1
	
	newurl = SecretShortenedUrl(id=urlid, url=url)
	db_session.add(newurl)
	db_session.commit()
	return urlid

@app.route('/<string:url_id>')
def redirect_short_url(url_id):
	try:
		return redirect(get_url(url_id))
	except:
		return "404 Not found", 404

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

class ShortUrl(Resource):
	def get(self, url_id):
		try:
			return {'status': 200, 'message': get_url(url_id)}
		except:
			return {'status': 404, 'message': 'Not Found'}, 404

class ShortUrlList(Resource):
	def get(self):
		try:
			urls = ShortenedUrl.query.all()
			allurls = {number_to_text(url.id): url.url for url in urls}
		except Exception as e:
			return {'status': 500, 'message': str(e)}, 500
		else:
			return {'status': 200, 'message': allurls}

	def post(self):
		args = parser.parse_args()
		if not args['url']:
			return {'status': 400, 'message': 'Use the argument `url`'}, 400
		if not valid_url(args['url']):
			return {'status': 400, 'message': 'Not a valid url'}, 400
		
		if args['secret']:
			try:
				urlid = add_secret_url(args['url'])
			except Exception as e:
				return {'status': 500, 'message': str(e)}, 500
			else:
				return {'status': 200, 'message': urlid}
			
		try:
			urlid = -1
			while urlid == -1:
				urlid = add_url(args['url'])
		except Exception as e:
			return {'status': 500, 'message': str(e)}, 500
		else:
			return {'status': 200, 'message': number_to_text(urlid)}

api.add_resource(ShortUrl, '/urls/<string:url_id>')
api.add_resource(ShortUrlList, '/urls')

if __name__ == '__main__':
	app.run(debug=True)