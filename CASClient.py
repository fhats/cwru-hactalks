import re
import urllib

from flask import redirect
from flask import request
from google.appengine.api import urlfetch

import logging

class CASClient(object):
	"""Lifted from https://sp.princeton.edu/oit/sdp/CAS/Wiki%20Pages/Python.aspx .
	Thanks, Princeton!"""

	def __init__(self):
		self.cas_url = 'https://login.case.edu/cas/'

	def Authenticate(self):
		# If the request contains a login ticket, try to validate it
		if request.args.has_key('ticket'):
			netid = self.Validate(request.args['ticket'])
			if netid != None:
				return netid
		# No valid ticket; redirect the browser to the login page to get one
		login_url = self.cas_url + 'login' \
			+ '?service=' + urllib.quote(self.ServiceURL())
		return redirect(login_url)

	def Validate(self, ticket):
		val_url = self.cas_url + "validate" + \
			'?service=' + urllib.quote(self.ServiceURL()) + \
			'&ticket=' + urllib.quote(ticket)
		req = urlfetch.fetch(val_url)	# returns 2 lines
		logging.warning(req.status_code)
		r = req.content.strip().split("\n")

		logging.warning(r)

		if len(r) == 2 and re.match("yes", r[0]) != None:
			return r[1].strip()
		return None

	def ServiceURL(self):
		return request.base_url