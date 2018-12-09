from __future__ import with_statement
from invoke import task
import env, utils

@task
def install(c):
    cmds = [
        "wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | sudo apt-key add -",
        "wget -q https://www.virtualbox.org/download/oracle_vbox.asc -O- | sudo apt-key add -",
        'sudo add-apt-repository "deb [arch=amd64] http://download.virtualbox.org/virtualbox/debian $(lsb_release -cs) contrib"',
        "sudo apt update",
        "sudo apt install virtualbox virtualbox-ext-pack",
        # "sudo apt install vagrant",
        "wget -c https://releases.hashicorp.com/vagrant/2.0.3/vagrant_2.0.3_x86_64.deb -P /tmp",
        "sudo dpkg -i /tmp/vagrant_2.0.3_x86_64.deb",
        "vagrant plugin install vagrant-disksize"
    ]
    for cmd in cmds:
        utils.run_with_exit(c, cmd)
