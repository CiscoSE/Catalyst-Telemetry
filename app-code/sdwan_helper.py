"""
Copyright (c) 2021 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

import json

import requests


class RestApiLib:
    def __init__(self, vmanage_host, vmanage_port, username, password):
        self.vmanage_host = vmanage_host
        self.vmanage_port = vmanage_port
        self.session = {}
        self.login(self.vmanage_host, username, password)

    def login(self, vmanage_host, username, password):
        """Login to vmanage"""

        base_url = '%s:%s/' % (self.vmanage_host, self.vmanage_port)

        login_action = '/j_security_check'

        # Format data for loginForm
        login_data = {'j_username': username, 'j_password': password}

        # Url for posting login data
        login_url = base_url + login_action

        # URL for retrieving client token
        token_url = base_url + 'dataservice/client/token'

        sess = requests.session()

        # If the vmanage has a certificate signed by a trusted authority
        # change verify to True.
        login_response = sess.post(url=login_url, data=login_data,
                                   verify=False)
        if b'<html>' in login_response.content:
            print("Login Failed")
            exit(0)

        # Update token to session headers

        login_token = sess.get(url=token_url, verify=False)

        if login_token.status_code == 200:
            if b'<html>' in login_token.content:
                print("Login Token Failed")
                exit(0)

            sess.headers['X-XSRF-TOKEN'] = login_token.content
            self.session[vmanage_host] = sess

    def get_request(self, mount_point):
        """GET request"""
        url = "%s:%s/dataservice/%s" % (
            self.vmanage_host, self.vmanage_port, mount_point)
        print(url)

        response = self.session[self.vmanage_host].get(url, verify=False)

        return response

    def post_request(self, mount_point, payload,
                     headers={'Content-type': 'application/json',
                              'Accept': 'application/json'}):
        """POST request"""
        url = "%s:%s/dataservice/%s" % (
            self.vmanage_host, self.vmanage_port, mount_point)
        # print(url)
        payload = json.dumps(payload)
        # print (payload)

        response = self.session[self.vmanage_host].post(url=url, data=payload,
                                                        headers=headers,
                                                        verify=False)
        # print(response.text)
        # exit()
        # data = response
        return response
