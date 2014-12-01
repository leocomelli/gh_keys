#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import imp
import os
import ast
import json

imp.load_source('github_keys', os.path.join(os.path.dirname(__file__), os.path.pardir, 'github_keys.py'))
from github_keys import GHKeys
from ansible_fake import AnsibleFake


class GHKeysUnitTest(unittest.TestCase):
	
  def exec_validation_tests(self, params):
    module = AnsibleFake(params)
    gh_keys = GHKeys(module)

    with self.assertRaises(ValueError) as err:
      result = gh_keys.work()

    return err.exception.args[0]  	

  # Add Key

  def test_should_throws_an_exception_when_action_addkey_and_title_null(self):
    err_msg = self.exec_validation_tests({'action' : 'add_key', 'key' : 'ssh-rsa AAA...', 'passwd' : 'secret'})
    self.assertEqual(err_msg, 'title cannot be null for action [add_key]')      

  def test_should_throws_an_exception_when_action_addkey_and_key_null(self):
    err_msg = self.exec_validation_tests({'action' : 'add_key', 'title' : 'my_pubkey', 'passwd' : 'secret'})
    self.assertEqual(err_msg, 'key cannot be null for action [add_key]')

  def test_should_throws_an_exception_when_action_addkey_and_passwd_null(self):
    err_msg = self.exec_validation_tests({'action' : 'add_key', 'title' : 'my_pubkey', 'key' : 'ssh-rsa AAA...'})
    self.assertEqual(err_msg, 'passwd cannot be null for action [add_key]')  
 
  # Get Key

  def test_should_throws_an_exception_when_action_getkey_and_passwd_null(self):
    err_msg = self.exec_validation_tests({'action' : 'get_key', 'key_id' : 9999})
    self.assertEqual(err_msg, 'passwd cannot be null for action [get_key]')

  def test_should_throws_an_exception_when_action_getkey_and_key_id_null(self):
    err_msg = self.exec_validation_tests({'action' : 'get_key', 'passwd' : 'secret'})
    self.assertEqual(err_msg, 'key_id cannot be null for action [get_key]')

  # Remove Key

  def test_should_throws_an_exception_when_action_removekey_and_passwd_null(self):
    err_msg = self.exec_validation_tests({'action' : 'remove_key', 'key_id' : 9999})
    self.assertEqual(err_msg, 'passwd cannot be null for action [remove_key]')

  def test_should_throws_an_exception_when_action_removekey_and_key_id_null(self):
    err_msg = self.exec_validation_tests({'action' : 'remove_key', 'passwd' : 'secret'})
    self.assertEqual(err_msg, 'key_id cannot be null for action [remove_key]')

if __name__ == '__main__':
  unittest.main()