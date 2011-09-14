from google.appengine.ext import db

class Talk(db.Model):
	name = db.StringProperty(required=True)
	speaker = db.StringProperty(required=True)
	votes = db.IntegerProperty(required=True)

class Vote(db.Model):
	netid = db.StringProperty(required=True)
	direction = db.StringProperty(required=True)
	talk_id = db.IntegerProperty(required=True)