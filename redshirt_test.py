import unittest
import subprocess
import psutil

try:
    from unittest.mock import patch, mock_open, NonCallableMagicMock
except ImportError:
    from mock import patch, mock_open, NonCallableMagicMock

from redshirt import *
from redshirt import __version__

class TestMetaRoutes(unittest.TestCase):

    def test_version(self):
        self.assertEqual(version(), __version__)

    @patch('socket.gethostname')
    def test_index(self, patched_gethostname):
        host = "hal"
        patched_gethostname.return_value = host
        out = index()
        patched_gethostname.assert_called_with()
        self.assertEqual(out, "<h1>Welcome to redshirt on {}.<h1>".format(host))

    def test_self_hc(self):
        self.assertEqual(self_health_check(), "OK")

class TestUserCreateStory(unittest.TestCase):
    org = "Testusers"
    user = "Timmy"
    @patch("redshirt.check_output")
    def test_add_user(self, patched_check_output):
        patched_check_output.return_value = "New user key: 570472ff-43b5-43f9-8544-e3b2fa5cc6f2\nCreated user '{}' for organization '{}'\n".format(self.user, self.org)
        self.assertEqual(add_user(self.org, self.user), "570472ff-43b5-43f9-8544-e3b2fa5cc6f2")
        patched_check_output.assert_called_with(["taskd", "add", "user", self.org, self.user])

    @patch("redshirt.check_output")
    def test_rm_user(self, patched_check_output):
        patched_check_output.return_value = ""
        self.assertEqual(remove_user(self.user, self.org), "OK")
        patched_check_output.assert_called_with(["taskd", "remove", "user", self.org, self.user])

    @patch("redshirt.check_output")
    def test_add_org(self, patched_check_output):
        new_org = "TeamRocket"
        self.assertEqual(add_org(new_org), "OK")
        patched_check_output.assert_called_with(["taskd", "add", "org", new_org])
    
    @patch("redshirt.check_output")
    def test_rm_org(self, patched_check_output):
        new_org = "TeamRocket"
        self.assertEqual(rm_org(new_org), "OK")
        patched_check_output.assert_called_with(["taskd", "remove", "org", new_org])

class TestTaskInfo(unittest.TestCase):
    @patch('redshirt.check_output')
    def test_version(self, patched_check_output):
        patched_check_output.return_value = "\n\x1b[1mtaskd 1.2.0\x1b[0m e2d145b built for linux\nCopyright (C) 2010 - 2016 G\xc3\xb6teborg Bit Factory.\n\nTaskd may be copied only under the terms of the MIT license, which may be found in the taskd source kit.\nDocumentation for taskd can be found using 'man taskd' or at http://taskwarrior.org\n\n"
        out = get_version()
        expected = {'git_rev': 'e2d145b', 'platform': 'linux', 'version': '1.2.0'}
        self.assertEqual(out, expected)
        patched_check_output.assert_called_with(["taskd", "-v"])

    @patch('redshirt._get_proc')
    def test_health_check(self, patched_get_proc):
        # patched_process_iter.side_effect = {"taskd"
        patched_get_proc.return_value = [psutil.Process()]
        self.assertEqual(health_check(), {"status": "running"})

class TestCerts(unittest.TestCase):

    # https://stackoverflow.com/questions/37265706/how-can-i-use-mock-open-with-a-python-unittest-decorator
    @patch('redshirt.request')
    def test_install_cert(self, patched_request):
        with patch('redshirt.open', mock_open(read_data="this is a test cert"), create=True):
            self.assertEqual(install_cert(), "OK")

class IntegrationTest(unittest.TestCase):
    pass
    # def setUp(self):
    #     subprocess.check_output(["taskd", "add", "org", self.org], env={"TASKDDATA": "/var/lib/taskd"})

    # def tearDown(self):
    #     subprocess.check_output(["taskd", "remove", "org", self.org], env={"TASKDDATA": "/var/lib/taskd"})
