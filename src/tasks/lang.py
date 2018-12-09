from __future__ import with_statement
from invoke import task
import sys, env, utils

@task
def install(c, role, locale="en_US.UTF-8"):
    if locale == 'en_US.UTF-8':
        pack = 'language-pack-en'
    elif locale == 'ko_KR.UTF-8':
        pack = 'language-pack-ko'
    else:
        print("only support en/ko langauge pack")
        sys.exit(-1)

    for k, v in env.hosts.iteritems():
        if role not in v["roles"]:
            continue

        cmd = "ssh -o StrictHostKeyChecking=no {}@{} ".format(env.SKP_USER, v["ipv4"])
        cmd += "sudo apt-get install --no-install-recommends -y locales {} ".format(pack)
        utils.run_with_exit(c, cmd)

        cmd = "ssh -o StrictHostKeyChecking=no {}@{} ".format(env.SKP_USER, v["ipv4"])
        cmd += '"sudo sed -i -e \'s/# {} UTF-8/{} UTF-8/\' /etc/locale.gen && sudo locale-gen"'.format(locale, locale)
        utils.run_with_exit(c, cmd)

        cmd = "ssh -o StrictHostKeyChecking=no {}@{} ".format(env.SKP_USER, v["ipv4"])
        cmd += "sudo update-locale LC_ALL={} LANG={} LC_MESSAGES=POSIX".format(locale, locale)
        utils.run_with_exit(c, cmd)
