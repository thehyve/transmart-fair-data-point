'''
* Copyright (c) 2017 The Hyve B.V.
* This code is licensed under the GNU General Public License,
* version 3.
* Author: Ruslan Forostianov
'''

import json
from urllib.request import urlopen, Request
from urllib.parse import urlencode

'''
    TranSMART REST API
'''
class TransmartApi(object):
    
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password
        self.access_token = None
    
    def get_studies(self, study_id = ''):
        url = '/v1/studies/' + study_id
        studies = self._json(url, access_token = self._get_access_token())
        return studies

    def _json(self, url, post_data = None, access_token = None):
        headers = {}
        headers['Accept'] = 'application/%s;charset=UTF-8' % ('json')
        if access_token is not None:
            headers['Authorization'] = 'Bearer ' + access_token
        req = Request(self.host + url, headers = headers)
        if post_data is None:
            res = urlopen(url = req)
        else:
            encoded_post_data = urlencode(post_data).encode("utf-8")
            res = urlopen(url = req, data = encoded_post_data)
        content = res.read()
        return json.loads(content)
    
    def _get_access_token(self):
        if self.access_token is None:
            url = '/oauth/token'
            params = {
                'grant_type' : 'password',
                'client_id'  : 'glowingbear-js',
                'client_secret' : '',
                'username' : self.user,
                'password' : self.password
            }
            access_token_dic = self._json(url, params)
            self.access_token = access_token_dic['access_token']
        return self.access_token