from __future__ import with_statement
from invoke import task
import env, utils

@task
def install(c, locale):
    if locale == 'en_US.UTF-8':
        pack = 'language-pack-en'
    elif locale == 'ko_KR.UTF-8':
        pack = 'language-pack-ko'
    else:
        print("only support en/ko langauge pack")
        return

    for k, v in env.hosts.iteritems():
        cmd = "ssh -o StrictHostKeyChecking=no {}@{} ".format(env.SKP_USER, v["ipv4"])
        cmd += "sudo apt-get install -y {}; sudo locale-gen {}; sudo dpkg-reconfigure locales".format(pack, locale)
        utils.run_with_exit(c, cmd)

        cmd = "ssh -o StrictHostKeyChecking=no {}@{} ".format(env.SKP_USER, v["ipv4"])
        cmd += "sudo update-locale LC_ALL={} LANG={} LC_MESSAGES=POSIX".format(locale, locale)
        utils.run_with_exit(c, cmd)
