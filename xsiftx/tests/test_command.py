"""
Unit tests for xisftx command line interface
"""
import os
import shutil
import sys
import tempfile
import unittest

from mock import patch

from .util import nostderr
from xsiftx.command_line import execute
from xsiftx.util import XsiftxException


class TestCommandLine(unittest.TestCase):
    """
    Test options of command line
    """

    EDX_ROOT = '/edx/app/edxapp/edx-platform'
    EDX_VENV = '/edx/app/edxapp/venvs/edxapp'

    def test_args(self):
        """
        Test all the argument variations available
        """
        with nostderr():
            with self.assertRaises(SystemExit) as cm:
                execute()
            exit_exception = cm.exception
            self.assertEqual(exit_exception.code, 2)

            with self.assertRaises(SystemExit) as cm:
                sys.argv = ['xsiftx', 'sifter',]
                execute()
            exit_exception = cm.exception
            self.assertEqual(exit_exception.code, 2)

            with self.assertRaises(SystemExit) as cm:
                sys.argv = ['xsiftx', '-v', 'sfutt', 'sifter',]
                execute()
            exit_exception = cm.exception
            self.assertEqual(exit_exception.code, 2)

            with self.assertRaises(SystemExit) as cm:
                sys.argv = ['xsiftx', '-e', 'sfutt', 'sifter',]
                execute()
            exit_exception = cm.exception
            self.assertEqual(exit_exception.code, 2)

    def test_bad_sifter(self):
        """
        Test exit code on non-existent sifter
        """
        with nostderr():
            with self.assertRaises(SystemExit) as cm:
                sys.argv = ['xsiftx', '-v', 'blah', '-e', 'stuff', 'dontexist',]
                execute()
            exit_exception = cm.exception
            self.assertEqual(exit_exception.code, -1)

    def test_bad_course_bad_env(self):
        """
        Test bad course
        """
        with self.assertRaisesRegexp(XsiftxException,
                                     'No such file or dir.*') as cm:
            sys.argv = ['xsiftx',
                        '-v', 'blah', 
                        '-e', 'stuff',
                        '-c', 'course',
                        'test_sifters',]
            execute()

    @unittest.skipUnless(os.environ.get('XSIFTX_TEST_EDX', None),
                         'Requires an edx environment and XSIFTX_TEST_EDX '
                         'environment variable set.')
    def test_bad_course_good_env(self):
        """
        With proper parameters, test an invalid course
        """
        with nostderr():
            with self.assertRaises(SystemExit) as cm:
                sys.argv = ['xsiftx',
                            '-v', self.EDX_VENV, 
                            '-e', self.EDX_ROOT,
                            '-c', 'not_a_course',
                            'test_sifters',]
                execute()
            exit_exception = cm.exception
            self.assertEqual(exit_exception.code, -2)

    @unittest.skipUnless(os.environ.get('XSIFTX_TEST_EDX', None),
                         'Requires an edx environment and XSIFTX_TEST_EDX '
                         'environment variable set.')
    def test_valid_sifter_run(self):
        """
        Mock the location of the settings, but run valid sifter
        """
        temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, temp_dir)
        with patch('xsiftx.util.get_settings') as mock_settings:
            mock_settings.return_value = {
                'use_s3': False,
                'aws_key': '',
                'root_path': temp_dir,
                'bucket': '',
                'aws_key_id': ''
            }
            sys.argv = ['xsiftx',
                        '-v', self.EDX_VENV, 
                        '-e', self.EDX_ROOT,
                        'test_sifters',]
            execute()
            self.assertTrue(mock_settings.called)

