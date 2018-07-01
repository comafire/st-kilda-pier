import sys
from datetime import datetime, timedelta

def print_response(obj, res):
    print("\n[TEST CASE] {}.{}(), STATUS_CODE: {}, JSON: {}\n".format(obj.__class__.__name__, sys._getframe(1).f_code.co_name, res.status_code, res.json))
