#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import imp
import os

imp.load_source('gh_keys', os.path.join(os.path.dirname(__file__), os.path.pardir, 'gh_keys.py'))
from gh_keys import GHKeys
from ansible_fake import AnsibleFake

class GHKeysIntegTest(unittest.TestCase):
  '''
  The name of methods starts with test_0<n>, where <n> is a sequencial number to enforce the order of execution.
  '''

  added_key_id = None   

  def setUp(self):
    if os.getenv('gh_user') is None and os.getenv('gh_password') is None:
      raise ValueError('The environment variable are required [ gh_user and gh_password] to run the integration tests')


  def test_01_should_add_new_key(self):
    module = AnsibleFake({
    	'action'   : 'add_key',
    	'user'     : os.getenv('gh_user'),
    	'password' : os.getenv('gh_password'),
    	'title'    : 'test-ghkeys',
    	'key'      : 'test_key.pub'
    	})
    gh_keys = GHKeys(module)    
    result = gh_keys.perform_by_action()
 
    #print result

    global added_key_id
    added_key_id = eval(result.replace('true', '"true"'))['id']
    self.assertIsNotNone(added_key_id) 

  def test_02_should_identify_that_key_already_exists(self):
    module = AnsibleFake({
    	'action'   : 'add_key',
    	'user'     : os.getenv('gh_user'),
    	'password' : os.getenv('gh_password'),
    	'title'    : 'test-ghkeys',
    	'key'      : 'test_key.pub'
    	})
    gh_keys = GHKeys(module)
    with self.assertRaises(RuntimeError):    
      result = gh_keys.perform_by_action()

  def test_03_should_get_key(self):
    global added_key_id

    module = AnsibleFake({
      'action'   : 'get_key',
      'user'     : os.getenv('gh_user'),
      'password' : os.getenv('gh_password'),
      'key_id'   : added_key_id
      })
    gh_keys = GHKeys(module)    
    result = gh_keys.perform_by_action()

    #print result

    self.assertIsNotNone(eval(self.convert_bool_to_str(result))['key'])    

  def test_04_should_list_keys_no_authenticated_user(self):
    module = AnsibleFake({
      'action' : 'list_keys',
      'user'   : os.getenv('gh_user')
      })

    gh_keys = GHKeys(module)    
    result = gh_keys.perform_by_action()

    #print result

    global added_key_id

    has_key = False
    keys = eval(self.convert_bool_to_str(result))
    for key in keys:
      if key['id'] == added_key_id:
        has_key = True

    self.assertTrue(has_key)

  def test_05_should_list_keys_authenticated_user(self):
    module = AnsibleFake({
      'action'   : 'list_keys',
      'user'     : os.getenv('gh_user'),
      'password' : os.getenv('gh_password'),
      })

    gh_keys = GHKeys(module)    
    result = gh_keys.perform_by_action()

    #print result

    global added_key_id

    has_key = False
    keys = eval(self.convert_bool_to_str(result))
    for key in keys:
      if key['id'] == added_key_id:
        has_key = True

    self.assertTrue(has_key)

  def test_06_should_remove_key(self):
    global added_key_id

    module = AnsibleFake({
      'action'   : 'remove_key',
      'user'     : os.getenv('gh_user'),
      'password' : os.getenv('gh_password'),
      'key_id'   : added_key_id
      })

    gh_keys = GHKeys(module)
    result = gh_keys.perform_by_action()    

    print result

    # Verify!
    module = AnsibleFake({
      'action'   : 'get_key',
      'user'     : os.getenv('gh_user'),
      'password' : os.getenv('gh_password'),
      'key_id'   : added_key_id
      })
    gh_keys = GHKeys(module)    
    with self.assertRaises(RuntimeError):
      result = gh_keys.perform_by_action()
 
  def convert_bool_to_str(self, value):
    return value.replace('true', '"true"').replace('false', '"false"')

from ansible.module_utils.basic import *
if __name__ == '__main__':
  unittest.main()
