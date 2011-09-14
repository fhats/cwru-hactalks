import os
import re
import urllib
from functools import wraps

from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from google.appengine.ext import db
from werkzeug.wrappers import BaseResponse

from CASClient import CASClient
from models import Talk, Vote

app = Flask(__name__)

def log_warn(s):
	app.logger.warning(s)

def with_netid(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		C = CASClient()
		netid = C.Authenticate()
		if isinstance(netid, BaseResponse):
			return netid
		return f(netid, *args, **kwargs)
	return decorated_function
		
@app.route("/vote/<int:talk_id>/<direction>", methods=['POST', 'GET'])
@with_netid
def vote(netid, talk_id, direction):
	app.logger.info(dir(netid))
	app.logger.info(netid)
	votes = Vote.all()
	votes.filter('talk_id =', talk_id)
	votes.filter('netid =', netid)
	
	votes_res = votes.fetch(1)

	netid = str(netid)

	if len(votes.fetch(1)) < 1 or (votes_res[0].direction != 'up' and votes_res[0].direction != 'down'):
		# User has not voted before
		new_vote = Vote(direction=direction, netid=str(netid), talk_id=talk_id)
		talk = Talk.get_by_id(talk_id)
		
		if direction == 'up':
			talk.votes += 1
		elif direction == 'down':
			talk.votes -= 1

		talk.put()
		new_vote.put()
		app.logger.info("Did a vote")
		return redirect(url_for('index'))
	elif votes_res[0].direction != direction:
		# The user has voted and is changing
		vote = votes_res[0]
		vote.direction = direction
		talk = Talk.get_by_id(talk_id)
		if direction == 'up':
			talk.votes += 2
		elif direction == 'down':
			talk.votes -= 2
		talk.put()
		vote.put()
		app.logger.info("Did a exist vote")
		return redirect(url_for('index'))
	else:
		# User is not allowed to vote
		return redirect(url_for('index'))

@app.route("/talk/create", methods=['POST'])
def create_talk():
	name = request.form['name']
	speaker = request.form['speaker']
	talk = Talk(votes=0, name=name, speaker=speaker)
	talk.name = name
	talk.speaker = speaker
	talk.votes = 0
	talk.put()
	return redirect(url_for('create_talk_form'))

@app.route("/talk/create", methods=['GET'])
@with_netid
def create_talk_form(netid):
	if netid not in ('fxh32', 'cxw158', 'jas404', 'srj15'):
		return redirect(url_for('index'))
	
	return render_template('create_talk_form.html')

@app.route("/talk/delete/<int:talk_id>")
@with_netid
def delete_talk(netid, talk_id):
	if netid not in ('fxh32', 'cxw158', 'jas404', 'srj15'):
		return redirect(url_for('index'))

	talk = Talk.get_by_id(talk_id)
	talk.delete()

	return redirect(url_for('index'))

@app.route("/talks/view")
def view_talks():
	talks = Talk.all()
	talks.order('-votes')

	# Convenient statistics
	max_votes = max([abs(talk.votes) for talk in talks])

	return render_template('view.html', talks=talks, max_votes=max_votes)

@app.route("/")
@with_netid
def index(netid):
	talks = Talk.all()
	all_votes = Vote.all()
	votes = all_votes.filter('netid =', netid)
	return render_template('index.html', talks=talks, votes=votes, ticket=request.args['ticket'], netid=netid)

if __name__ == "__main__":
	from google.appengine.ext.webapp.util import run_wsgi_app

	run_wsgi_app(app)