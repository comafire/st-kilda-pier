import airflow
from airflow import models, settings
from airflow.contrib.auth.backends.password_auth import PasswordUser

user = PasswordUser(models.User())
user.username = 'admin'
user.email = 'comafire@gmail.com'
#user.password = unicode("admin", "utf-8")
user._set_password = "admin"
session = settings.Session()
session.add(user)
session.commit()
session.close()
exit()
