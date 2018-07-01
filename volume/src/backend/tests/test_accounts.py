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

class AccountsTest(TestCase):
    def create_app(self):
        return app

    def setUp(self):
        self.id = "u1"
        self.pw = "u1"
        res = self.client.post("/v1/accounts", data={
            'id' : self.id,
            'pw' : self.pw,
            'level': 'U'
        })
        print_response(self, res)
        self.assertEqual(res.status_code, HTTPStatus.CREATED)
        account = Account.get_account(self.id)
        account.active = "Y"
        db.session.add(account)
        db.session.commit()

        res = self.client.post("/v1/tokens", data = {
            'id' : self.id,
            'pw' : self.pw
        })
        print_response(self, res)
        self.assertEqual(res.status_code, HTTPStatus.CREATED)
        self.access_token = res.json['access_token']
        self.refresh_token = res.json['refresh_token']
        return

    def tearDown(self):
        res = self.client.delete("/v1/accounts/{}".format(self.id),
            headers = { 'Authorization' : "Bearer {}".format(self.access_token) }
        )
        print_response(self, res)
        self.assertEqual(res.status_code, HTTPStatus.OK)

        res = self.client.delete("/v1/tokens",
            headers = { 'Authorization' : "Bearer {}".format(self.access_token) }
        )
        print_response(self, res)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        return

    def test_put(self):
        res = self.client.put("/v1/accounts/{}".format(self.id),
            headers = { 'Authorization' : "Bearer {}".format(self.access_token) },
            data = {
                'pw' : self.pw,
                'active' : "Y" })
        print_response(self, res)
        self.assertEqual(res.status_code, HTTPStatus.OK)

    def test_get(self):
        res = self.client.get("/v1/accounts/{}".format(self.id),
            headers = { 'Authorization' : "Bearer {}".format(self.access_token) })
        print_response(self, res)
        self.assertEqual(res.status_code, HTTPStatus.OK)

if __name__ == '__main__':
    unittest.main()
