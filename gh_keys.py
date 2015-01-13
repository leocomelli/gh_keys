#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import base64

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
    choices: [ list_keys, get_key, add_key, remove_key ]

  user:
    description: Github username.
    required: true

  password:
    description: Github password. If 2FA is enabled for your account, you should generate a new personal access token. Required for get_key, add_key and remove_key 
    required: false 

  title:
    description: Title of the new ssh key. Required for add_key
    required: false

  key:
    description: The path of file that contains the public key. Required for add_key
    required: false

  key_id:
    description: The key id provided by Github. Required for get_key and remove_key
    required: false

author: Leonardo Comelli
'''

EXAMPLES = '''
# Example from Ansible Playbooks

# Lists limit informations about all keys of non-authenticated user
- gh_keys: action=list_keys user=leocomelli

# Lists all informations about all keys of authenticated user
- gh_keys: action=list_keys user=leocomelli password=secret

# Gets a single public key (authetication required)
- gh_keys: action=get_key user=leocomelli password=secret key_id=8767854

# Adds a new public key (authentication required)
- gh_keys: action=add_key user=leocomelli password=secret title=my_new_key key=/home/leocomelli/.ssh/id_rsa.pub

# Removes an existing ssh key
- gh_keys: action=remove_key user=leocomelli password=secret key_id=8767854
'''

GH_API_URL = "https://api.github.com/%s"

class GHKeys(object):

  def __init__(self, module):
    self.module = module
    self.action = module.params['action']
    self.user   = module.params['user']
    self.password = module.params['password']
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
    if self.password is None:
      url = GH_API_URL % "users/%s/keys" % self.user
      response, info = fetch_url(self.module, url)
    else:
      url = GH_API_URL % "user/keys"
      headers = self.get_auth_header(self.user, self.password)
      response, info = fetch_url(self.module, url, headers=headers)
    
    return response.read(), info
 
  def get_key(self):
    self.validate_fileds('get_key', ['key_id', 'password'])    

    url = GH_API_URL %  "user/keys/%s" % self.key_id
    headers = self.get_auth_header(self.user, self.password)
    response, info = fetch_url(self.module, url, headers=headers)

    return response.read(), info

  def add_key(self):
    self.validate_fileds('add_key', ['title', 'key', 'password'])

    with open(self.key, 'r') as content_file:
      content = content_file.read()

    url = GH_API_URL %  "user/keys"
    headers = self.get_auth_header(self.user, self.password)
    data = json.dumps({ 'title' : self.title, 'key' : content })
    response, info = fetch_url(self.module, url, headers=headers, data=data)

    return response.read(), info

  def remove_key(self):
    self.validate_fileds('remove_key', ['key_id', 'password'])

    url = GH_API_URL %  "user/keys/%s" % self.key_id
    headers = self.get_auth_header(self.user, self.password)
    response, info = fetch_url(self.module, url, headers=headers, method='DELETE')

    return response.read(), info

  def get_auth_header(self, user, password):
    auth = base64.encodestring('%s:%s' % (user, password)).replace('\n', '')
    headers = {
      'Authorization': 'Basic %s' % auth,
    }
    return headers

  def validate_fileds(self, action, fields):
    for field in fields:
      if getattr(self, field) is None:
        raise ValueError(field + " cannot be null for action [" + action + "]")

def main():
  module = AnsibleModule(
    argument_spec = dict(
      password = dict(),
      title    = dict(),
      key      = dict(),
      key_id   = dict(),
      user     = dict(required=True),
      action   = dict(required=True, choices=['list_keys', 'get_key', 'add_key', 'remove_key']),
    )
  )  

  gh_keys = GHKeys(module)
  try:
    response, info = gh_keys.work()
    #if 'message' in result:
    #  raise RuntimeError(result)

    module.exit_json(changed=True, stdout=response)
  except (RuntimeError, ValueError), err:
    print err.args
    #module.fail_json(msg=err.args)

from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

if __name__ == '__main__':
  main()
