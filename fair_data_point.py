'''
* Copyright (c) 2017 The Hyve B.V.
* This code is licensed under the GNU General Public License,
* version 3.
* Author: Ruslan Forostianov
'''

import falcon
from transmart_fair_metadata import TransmartFairMetadata
 
class TurtleRdf(object):
	def __init__(self, producer):
		self.producer = producer

	def on_get(self, req, resp, param1 = None):
		resp.status = falcon.HTTP_200
		resp.content_type = 'text/turtle'
		if param1 is None:
			g = self.producer()
		else:
			g = self.producer(param1)
		resp.body = g.serialize(format = 'turtle')

transmart_fair_metadata = TransmartFairMetadata()
api = falcon.API()
api.add_route('/', TurtleRdf(transmart_fair_metadata.repository))
api.add_route('/studies', TurtleRdf(transmart_fair_metadata.catalog))
api.add_route('/studies/{param1}', TurtleRdf(transmart_fair_metadata.dataset))
api.add_route('/studies/{param1}/data', TurtleRdf(transmart_fair_metadata.distribution))