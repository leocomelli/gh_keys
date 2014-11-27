#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import requests
from ansible.module_utils.basic import *

EXAMPLES = '''
  List public keys for a user
  gh-keys:
    user: leocomelli

  List your public keys
  gh-keys:
    user: leocomelli
    passwd: secret

  Get a single public key
  gh_keys:
    user: leocomelli
    passwd: secret
    key_id: 123456

  Add a public key
  gh_keys:
    user: leocomelli
    passwd: secret
    title: new-key
    key: 'ssh-rsa AAA...'

  Remove a public key
  gh_keys:
    user: leocomelli
    passwd: secret
    key_id: 123456
    state: absent
    
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

    return { "keys": response.text }

  def get_key(self):
    self.validate_fileds('add_key', ['key_id', 'passwd'])    

    url = GH_API_URL %  "user/keys/%s" % self.key_id
    response = requests.get(url, auth=(self.user, self.passwd)) 

    return { "key": response.text }

  def add_key(self):
    self.validate_fileds('add_key', ['title', 'key', 'passwd'])

    url = GH_API_URL %  "user/keys"
    data = json.dumps({ 'title' : self.title, 'key' : self.key })
    response = requests.post(url, auth = (self.user, self.passwd), data = data) 

    return { "key": response.text }

  def remove_key(self):
    self.validate_fileds('remove_key', ['key_id', 'passwd'])

    url = GH_API_URL %  "user/keys/%s" % self.key_id
    response = requests.delete(url, auth=(self.user, self.passwd)) 

    return { "key": response.text }

  def validate_fileds(self, action, fields):
    for field in fields:
      if getattr(self, field) is None:
        raise ValueError(field + " cannot be null for action [" + action + "]")

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
    module.exit_json(result=result)
  except ValueError as err:
    module.fail_json(msg=err.args)

if __name__ == '__main__':
  main()
