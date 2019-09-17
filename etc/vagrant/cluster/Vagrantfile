# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.

ENV["LC_ALL"] = "en_US.UTF-8"

n_nodes = 5

Vagrant.configure("2") do |config|

  config.vm.define "e01" do |host|
    host.vm.box = "ubuntu/bionic64"
    host.vm.hostname = "e01"
    host.vm.network "public_network", ip: "192.168.0.50"
    #host.vm.network "private_network", ip: "10.0.0.50"
    host.vm.provider "virtualbox" do |vb|
      vb.gui = false
      vb.cpus = 1
      vb.memory = "2048"
    end
    host.disksize.size = '16GB'
    host.vm.synced_folder "../../../", "/home/vagrant/st-kilda-pier", owner: "vagrant", group: "vagrant"

    # SSH enable password login
    host.vm.provision "shell", inline: "sed -i -e 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config"
    host.vm.provision "shell", inline: "service ssh restart"
    
    # Install ansible, sshpass, invoke
    host.vm.provision "shell", inline: "apt-get update"
    host.vm.provision "shell", inline: "apt-get install -y apt-transport-https ca-certificates curl software-properties-common"
    host.vm.provision "shell", inline: "apt-get install -y python3 python3-pip python3-setuptools virtualenv sshpass"
    host.vm.provision "shell", inline: "pip3 install invoke ansible"
  end

  (1..n_nodes).each do |i|
    config.vm.define "c#{'%02d' % i}" do |host|
      host.vm.box = "ubuntu/bionic64"
      host.vm.hostname = "c#{'%02d' % i}"
      host.vm.network "public_network", ip: "192.168.0.5#{i}"
      #host.vm.network "private_network", ip: "10.0.0.5#{i}"
      host.vm.provider "virtualbox" do |vb|
        vb.gui = false
        vb.cpus = 1
        vb.memory = "2048"
      end
      host.disksize.size = '16GB'
      host.vm.synced_folder "../../../", "/home/vagrant/st-kilda-pier", owner: "vagrant", group: "vagrant"

      # SSH enable password login
      host.vm.provision "shell", inline: "sed -i -e 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config"
      host.vm.provision "shell", inline: "service ssh restart"
    end
  end

end
