import unittest

# your test cases
import urllib
from flask_testing import TestCase

from http import HTTPStatus

from passlib.hash import pbkdf2_sha256 as sha256

# add parent module path
import sys
sys.path.append('..')
from utils.common import print_response

from run import app
from run import db
from models.account import Account
from models.token import RevokedToken

class Tokens(TestCase):
    def create_app(self):
        return app

    def setUp(self):
        self.id = "admin"
        self.pw = "admin"
        res = self.client.post("/v1/tokens", data = {
            'id' : self.id,
            'pw' : self.pw
        })
        print_response(self, res)
        self.assertEqual(res.status_code, HTTPStatus.CREATED)
        self.id = res.json['id']
        self.level = res.json['level']
        self.access_token = res.json['access_token']
        self.refresh_token = res.json['refresh_token']

    def tearDown(self):
        res = self.client.delete("/v1/tokens",
            headers = { 'Authorization' : "Bearer {}".format(self.access_token) }
        )
        print_response(self, res)
        self.assertEqual(res.status_code, HTTPStatus.OK)

    def test_put(self):
        res = self.client.put("/v1/tokens",
            headers = { 'Authorization' : "Bearer {}".format(self.refresh_token) }
        )
        print_response(self, res)
        self.assertEqual(res.status_code, HTTPStatus.OK)

if __name__ == '__main__':
    unittest.main()
