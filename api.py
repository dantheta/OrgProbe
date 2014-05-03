
import sys
import json
import logging
import datetime
import requests

__all__ = ['RegisterProbeRequest','PrepareProbeRequest','StatusIPRequest','RequestHttptRequest','ConfigRequest','ResponseHttptRequest']


class APIError(Exception): pass

class APIRequest(object):
	HTTPS=True
	HOST = 'api.bowdlerize.co.uk'
	PORT = 443
	VERSION='1.2'

	SEND_TIMESTAMP=True
	SIG_KEYS = []
	ENDPOINT = None
	METHOD = 'POST'

	def __init__(self, signer, *urlargs, **kw):
		self.args = kw
		self.urlargs = urlargs
		self.signer = signer

	def get_url(self):
		urlargs = '/'.join(self.urlargs)
		return "{0}://{1}:{2}/{3}/{4}{5}{6}".format(
			'https' if self.HTTPS else 'http',
			self.HOST,
			self.PORT,
			self.VERSION,
			self.ENDPOINT,
			'/' if urlargs else '',
			urlargs)

	def timestamp(self):
		return datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


	def get_signature(self):
		return self.signer.get_signature(self.args, self.SIG_KEYS)

	def execute(self):
		if self.SEND_TIMESTAMP:
			self.args['date'] = self.timestamp()
		if self.SIG_KEYS and self.signer:
			self.args['signature'] = self.get_signature()
		logging.info("Sending args: %s", self.args)
		try:
			url = self.get_url()
			logging.info("Opening ORG Api connection to: %s", url)
			if self.METHOD == 'GET':
				rq = requests.get(url, params=self.args)
			else:
				rq = requests.post(url, data=self.args)
		except Exception,v:
			logging.error("API Error: %s", v)
			raise 

		logging.info("ORG Api Request Complete: %s", rq.status_code)
		try:
			if rq.status_code == 500:
				raise APIError(rq.status_code)
			return rq.status_code, rq.json()
		except ValueError:
			print >>sys.stderr, rq.content

class PrepareProbeRequest(APIRequest):
	ENDPOINT = 'prepare/probe'
	SIG_KEYS = ['email','date']

class RegisterProbeRequest(APIRequest):
	ENDPOINT = 'register/probe'
	SEND_TIMESTAMP=False
	SIG_KEYS = ['probe_uuid']
	
class StatusIPRequest(APIRequest):
	ENDPOINT = 'status/ip'
	SIG_KEYS = ['date']
	METHOD = 'GET'

class RequestHttptRequest(APIRequest):
	ENDPOINT = 'request/httpt'
	SIG_KEYS = ['probe_uuid']
	METHOD = 'GET'
	SEND_TIMESTAMP=False

class ConfigRequest(APIRequest):
	ENDPOINT = 'config/latest'
	SIG_KEYS = []
	METHOD = 'GET'
	SEND_TIMESTAMP=False

class ResponseHttptRequest(APIRequest):
	ENDPOINT = 'response/httpt'
	SIG_KEYS = ["probe_uuid", "url", "status", "date", "config"]
	METHOD = "POST"
	SEND_TIMESTAMP = True
