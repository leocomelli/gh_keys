#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import imp
import os

imp.load_source('github_keys', os.path.join(os.path.dirname(__file__), os.path.pardir, 'github_keys.py'))
from github_keys import GHKeys
from ansible_fake import AnsibleFake


class GHKeysIntegTest(unittest.TestCase):
  '''
  The name of methods starts with test_0<n>, where <n> is a sequencial number to enforce the order of execution.
  '''

  added_key_id = None   

  def setUp(self):
    if os.getenv('gh_user') is None and os.getenv('gh_passwd') is None:
      raise ValueError('The environment variable are required [ gh_user and gh_passwd] to run the integration tests')


  def test_01_should_add_new_key(self):
    module = AnsibleFake({
    	'action' : 'add_key',
    	'user'   : os.getenv('gh_user'),
    	'passwd' : os.getenv('gh_passwd'),
    	'title'  : 'test-ghkeys',
    	'key'    : 'test_key.pub'
    	})
    gh_keys = GHKeys(module)    
    result = gh_keys.work()
 
    print result

    global added_key_id
    added_key_id = eval(result.replace('true', '"true"'))['id']
    self.assertIsNotNone(added_key_id)

  def test_02_should_identify_that_key_already_exists(self):
    module = AnsibleFake({
    	'action' : 'add_key',
    	'user'   : os.getenv('gh_user'),
    	'passwd' : os.getenv('gh_passwd'),
    	'title'  : 'test-ghkeys',
    	'key'    : 'test_key.pub'
    	})
    gh_keys = GHKeys(module)    
    result = gh_keys.work()

    print result

    error_message = eval(self.convert_bool_to_str(result))['errors'][0]['message']
    self.assertEqual(error_message, 'key is already in use')

  def test_03_should_get_key(self):
    global added_key_id

    module = AnsibleFake({
      'action' : 'get_key',
      'user'   : os.getenv('gh_user'),
      'passwd' : os.getenv('gh_passwd'),
      'key_id' : added_key_id
      })
    gh_keys = GHKeys(module)    
    result = gh_keys.work()

    print result

    self.assertIsNotNone(eval(self.convert_bool_to_str(result))['key'])    

  def test_04_should_list_keys_no_authenticated_user(self):
    module = AnsibleFake({
      'action' : 'list_keys',
      'user'   : os.getenv('gh_user')
      })

    gh_keys = GHKeys(module)    
    result = gh_keys.work()

    print result

    global added_key_id

    has_key = False
    keys = eval(self.convert_bool_to_str(result))
    for key in keys:
      if key['id'] == added_key_id:
        has_key = True

    self.assertTrue(has_key)

  def test_05_should_list_keys_authenticated_user(self):
    module = AnsibleFake({
      'action' : 'list_keys',
      'user'   : os.getenv('gh_user'),
      'passwd' : os.getenv('gh_passwd'),
      })

    gh_keys = GHKeys(module)    
    result = gh_keys.work()

    print result

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
      'action' : 'remove_key',
      'user'   : os.getenv('gh_user'),
      'passwd' : os.getenv('gh_passwd'),
      'key_id' : 123#added_key_id
      })

    gh_keys = GHKeys(module)    
    result = gh_keys.work()

    print result

    # Verify!
    module = AnsibleFake({
      'action' : 'get_key',
      'user'   : os.getenv('gh_user'),
      'passwd' : os.getenv('gh_passwd'),
      'key_id' : added_key_id
      })
    gh_keys = GHKeys(module)    
    result = gh_keys.work()

    with self.assertRaises(KeyError):
      eval(self.convert_bool_to_str(result))['key']      
 
  def convert_bool_to_str(self, value):
    return value.replace('true', '"true"').replace('false', '"false"')

if __name__ == '__main__':
  unittest.main()