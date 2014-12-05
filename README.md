# Ansible Module - Github Keys

An Ansible module to manage github public keys. The Github lets you add many public ssh keys, this is way that Github uses to identify trusted computers, without involving passwords.

## Features:

* Lists keys for non-authenticated user;
* Lists keys for authenticated user;
* Adds a new public ssh key;
* Gets a public ssh key by GH id;
* Removes an existing public ssh key.


## Sample

	# file: gh_keys.yml

	- hosts: devel
  	  user: root

      tasks:
        - name: Generate a new public key
          user:
            name: root
            generate_ssh_key: yes
            ssh_key_bits: 2048

        - name: Add a new GH public key
          gh_keys:
            action: add_key
            user: leocomelli
            passwd: secret
            title: devel
            key: /root/.ssh/id_rsa.pub
          register: keys

        - debug:
            var: keys.stdout

## Usage

### To execute

The extra module are found in the path specified by ANSIBLE_LIBRARY or the --module-path command line option.

	export ANSIBLE_LIBRARY=~/ansible/modules/gh_keys
	ansible-playbook gh_keys.yml -i hosts

or

	ansible-playbook gh_keys.yml -i hosts --module-path=~/ansible/modules/gh_keys/gh_keys.py


### Lists keys of a non-authenticated user

	...
	- gh_keys:
	    action: list_keys
	    user: leocomelli

    # output
    # [{"id":999999999,"key":"ssh-rsa AAA..."}]

### Lists keys of an authenticated user

	...
	- gh_keys:
	    action: list_keys
	    user: leocomelli
	    passwd: secret

	# output
	# [{"id":999999999,"key":"ssh-rsa AAA...","url":"https://api.github.com/user/keys/999999999","title":"test-ghkeys","verified":true}]

### Adds a new public ssh key (authentication required)

	...
	- gh_keys:
	  action: add_key
	  user: leocomelli
	  passwd: secret
	  title: my-new-pkey
	  key: /home/leocomelli/.ssh/id_rsa.pub

	# output
	# {"id":9999999991,"key":"ssh-rsa AAA2...","url":"https://api.github.com/user/keys/9999999991","title":"my-new-pkey","verified":true}

### Gets a public ssh key by GH id (authentication required)

	...
	- gh_keys:
	  action: get_key
	  user: leocomelli
	  passwd: secret
	  key_id: 9999999991

	# output
	# {"id":9999999991,"key":"ssh-rsa AAA2...","url":"https://api.github.com/user/keys/9999999991","title":"my-new-pkey","verified":true}

### Removes an existing public ssh key (authentication required)

	...
	- gh_keys:
	  action: remove_key
	  user: leocomelli
	  passwd: secret
	  key_id: 9999999991

	# output
	# N/A

## Authentication

The user and passwd fields are used in authentication process. To execute the most action you should be authenticated in GH, in the other words you must informed your GH password. If 2FA (two-facto authentication) features will be enabled for your account, you must generate a new personal access token (Settings > Application > Personal access token > Generate new token).

## Runnning Tests

### Manual

What I need to do to execute the manual test of gh_keys module?

	git clone git@github.com:ansible/ansible.git --recursive
	source ansible/hacking/env-setup
	chmod +x ansible/hacking/test-module

	sudo -E /ansible/hacking/test-module -m github_keys.py -a "action=list_keys user=leocomelli"

More infos [click here](http://docs.ansible.com/developing_modules.html)

### Automatic (unit/integration)

What I need to do to run the unit tests of gh_keys module?

	git clone git@github.com:leocomelli/ansible-ghkeys.git
	PYTHONPATH=$PWD python test/github_keys_unittest.py

What I need to do to run the integration tests of gh_keys module?

The integration tests require the GH user and passwod, because the tests will actually create a public ssh key in your GH account. These fields should be informed by environment variables (gh_user and gh_passwd).

	git clone git@github.com:leocomelli/ansible-ghkeys.git

	export gh_user=leocomelli
	export gh_passwd=secret

	PYTHONPATH=$PWD python test/github_keys_integtest.py

## License

(The MIT License)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the 'Software'), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.