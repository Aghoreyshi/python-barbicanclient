# Copyright (c) 2013 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import cStringIO
import os
import sys
import unittest2 as unittest

from mock import MagicMock

from barbicanclient import keep


class KeepTest(unittest.TestCase):
    def setUp(self):
        self.auth_endpoint = "http://keystone-int.cloudkeep.io:5000/v2.0/"
        self.username = 'demo'
        self.password = 'password'
        self.tenant = 'demo'
        self.endpoint = "http://localhost:9311/v1/"
        self.token = 'test'
        self.Keep = keep.Keep()
        self.keep_argstr = ("--auth_endpoint {0} --user {1} --password {2} " +
                            "--tenant {3} --endpoint {4} --token {5} ").format(
                                self.auth_endpoint, self.username,
                                self.password, self.tenant, self.endpoint,
                                self.token)

        self.mock_conn = MagicMock(name='Connection Mock')
        self.Connection = self.mock_conn(self.auth_endpoint, self.username,
                                         self.password, self.tenant,
                                         self.endpoint, self.token)

    def keep(self, argstr):
        """Based on Keystone client's shell method in test_shell.py"""
        orig = sys.stdout
        clean_env = {}
        _old_env, os.environ = os.environ, clean_env.copy()
        argstr = self.keep_argstr + argstr
        try:
            sys.stdout = cStringIO.StringIO()
            _keep = self.Keep
            _keep.execute(argv=argstr.split(), conn=self.Connection)
        except SystemExit:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.assertEqual(exc_value.code, 0)
        finally:
            out = sys.stdout.getvalue()
            sys.stdout.close()
            sys.stdout = orig
            os.environ = _old_env
        return out

    def test_help(self):
        args = "-h"
        self.assertIn('usage: ', self.keep(args))

    def test_no_args(self):
        args = ""
        with self.assertRaises(AssertionError) as e:
            self.assertIn('usage: ', self.keep(args))
            self.assertIn('2 != 0', str(e))

    def test_create_secret(self):
        args = "secret create"
        self.keep(args)
        self.Connection.create_secret.\
            assert_called_once_with(None, None, None, None, 'aes', 256, 'cbc',
                                    None)


if __name__ == '__main__':
    unittest.main()
