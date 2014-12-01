#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import requests
from ansible.module_utils.basic import *

DOCUMENTATION = '''
---
module: gh_keys
version_added: n/a
short_description: Manages github ssh keys.
description:
    - The module manages the ssh key for a specific user through Github API v3.
options:
  action:
    description: This tells the gh_keys module what you want it to do.
    required: true
    choices: 
      list_keys:
        description: lists keys for authenticated or non-authenticated user. If the passwd field is informed, the module returns all keys and all data about its (In this case, the module will send the authentication data in request). Otherwise, the module returns only some data about the ssh keys of non-authenticated user.
        required_fields: [user | user & passwd]
      get_key:
        description: gets a specific key by github ssh-key-id
        required_fields: [user & passwd & key_id]
      add_key:
        description: adds a new public ssh key
        required_fields: [user & passwd & title & key]
      remove_key:
        description: removes a specific key by github ssh-key-id
        required_fields: [user & passwd & key_id]
  user:
    description: Github username.
    required: true
  passwd:
    description: Github password. If 2FA is enabled for your account, you should generate a new personal access token. 
    required: for actions: list_keys (your), get_key, add_key, remove_key
  title:
    description: Title of the new ssh key
    required: for add_key action
  key:
    description: The path of file that contains the public key
    required: for add_key action
  key_id:
    description: The key id provided by Github
    required: for get_key and remove_key actions
author: Leonardo Comelli
'''

EXAMPLES = '''
# Example from Ansible Playbooks

# Lists limit informations about all keys of non-authenticated user
- gh_keys: action=list_keys user=leocomelli

# Lists all informations about all keys of authenticated user
- gh_keys: action=list_keys user=leocomelli passwd=secret

# Gets a single public key (authetication required)
- gh_keys: action=get_key user=leocomelli passwd=secret key_id=8767854

# Adds a new public key (authentication required)
- gh_keys: action=add_key user=leocomelli passwd=secret title=my_new_key key=/home/leocomelli/.ssh/id_rsa.pub

# Removes an existing ssh key
- gh_keys: action=remove_key user=leocomelli passwd=secret key_id=8767854
'''

GH_API_URL = "https://api.github.com/%s"

class GHKeys(object):

  def __init__(self, module):
    self.action = module.params['action']
    self.user   = module.params['user']
    self.passwd = module.params['passwd']
    self.title  = module.params['title']
    self.key    = module.params['key']
    self.key_id = module.params['key_id']
  
  def work(self):
    return {
      'list_keys'  : self.list_keys,
      'get_key'    : self.get_key,
      'add_key'    : self.add_key,
      'remove_key' : self.remove_key
    }[self.action]()

  def list_keys(self):
    if self.passwd is None:
      url = GH_API_URL % "users/%s/keys" % self.user
      response = requests.get(url)  
    else:
      url = GH_API_URL % "user/keys"
      response = requests.get(url, auth=(self.user, self.passwd))  

    return response.text

  def get_key(self):
    self.validate_fileds('get_key', ['key_id', 'passwd'])    

    url = GH_API_URL %  "user/keys/%s" % self.key_id
    response = requests.get(url, auth=(self.user, self.passwd)) 

    return response.text

  def add_key(self):
    self.validate_fileds('add_key', ['title', 'key', 'passwd'])

    with open(self.key, 'r') as content_file:
      content = content_file.read()

    url = GH_API_URL %  "user/keys"
    data = json.dumps({ 'title' : self.title, 'key' : content })
    response = requests.post(url, auth = (self.user, self.passwd), data = data) 

    return response.text

  def remove_key(self):
    self.validate_fileds('remove_key', ['key_id', 'passwd'])

    url = GH_API_URL %  "user/keys/%s" % self.key_id
    response = requests.delete(url, auth=(self.user, self.passwd)) 

    return response.text

  def validate_fileds(self, action, fields):
    for field in fields:
      if getattr(self, field) is None:
        raise ValueError(field + " cannot be null for action [" + action + "]")


def convert_bool_to_str(value):
  return value.replace('true', '"true"').replace('false', '"false"')

def main():
  module = AnsibleModule(
    argument_spec = dict(
      passwd = dict(),
      title  = dict(),
      key    = dict(),
      key_id = dict(),
      user   = dict(required=True),
      action = dict(required=True, choices=['list_keys', 'get_key', 'add_key', 'remove_key']),
    )
  )  

  gh_keys = GHKeys(module)
  try:
    result = gh_keys.work()
    changed = False if eval(convert_bool_to_str(result)).has_key('message') else True
    module.exit_json(changed=changed, result=result)
  except ValueError as err:
    module.fail_json(msg=err.args)

if __name__ == '__main__':
  main()
