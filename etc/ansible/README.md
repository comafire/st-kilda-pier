vagrant@e01:~/st-kilda-pier/etc/ansible$ ansible-playbook -i inventories/vcluster/ node_add.yml -kK

vagrant@e01:~/st-kilda-pier/etc/ansible$ ansible all -i inventories/vcluster/ -m ping

vagrant@e01:~/st-kilda-pier/etc/ansible$ ansible-playbook -i inventories/vcluster/ docker_install.yml  

vagrant@e01:~/st-kilda-pier/etc/ansible$ ansible-playbook -i inventories/vcluster/ docker_swarm_create.yml 

```
# import_playbook 은 playbook 에서 root 위치 여야함, 아닐경우 아래와 같은 에러 발생
# ERROR! this task 'import_playbook' has extra params, which is only allowed in the following modules: add_host, meta, raw, shell, win_command, include_tasks, script, include, group_by, include_role, win_shell, set_fact, import_tasks, include_vars, command, import_role

Limiting Playbook/Task Runs
When writing Ansible, sometimes it is tedious to make a change in a playbook or task, then run the playbook It can sometimes be very helpful to run a module directly as shown above, but only against a single development host.

Limit to one or more hosts
This is required when one wants to run a playbook against a host group, but only against one or more members of that group.

Limit to one host

ansible-playbook playbooks/PLAYBOOK_NAME.yml --limit "host1"
Limit to multiple hosts

ansible-playbook playbooks/PLAYBOOK_NAME.yml --limit "host1,host2"
Negated limit. NOTE: Single quotes MUST be used to prevent bash interpolation.

ansible-playbook playbooks/PLAYBOOK_NAME.yml --limit 'all:!host1'
Limit to host group

ansible-playbook playbooks/PLAYBOOK_NAME.yml --limit 'group1'
```