vagrant@e01:~/st-kilda-pier/etc/ansible$ ansible-playbook -i inventories/vcluster/ node_add.yml -kK

vagrant@e01:~/st-kilda-pier/etc/ansible$ ansible all -i inventories/vcluster/ -m ping

vagrant@e01:~/st-kilda-pier/etc/ansible$ ansible-playbook -i inventories/vcluster/ docker_install.yml 