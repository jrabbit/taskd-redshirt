import unittest
import subprocess

import mock

from redshirt import version, self_health_check, health_check, get_version, index, __version__, add_user

class TestMetaRoutes(unittest.TestCase):

    def test_version(self):
        self.assertEqual(version(), __version__)

    @mock.patch('socket.gethostname')
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
    @mock.patch("redshirt.check_output")
    def test_add_user(self, patched_check_output):
        patched_check_output.return_value = "New user key: 570472ff-43b5-43f9-8544-e3b2fa5cc6f2\nCreated user '{}' for organization '{}'\n".format(self.user, self.org)
        self.assertEqual(add_user(self.org, self.user), "570472ff-43b5-43f9-8544-e3b2fa5cc6f2")
        patched_check_output.assert_called_with(["taskd", "add", "user", self.org, self.user])


class TestTaskInfo(unittest.TestCase):
    @mock.patch('redshirt.check_output')
    def test_version(self, patched_check_output):
        patched_check_output.return_value = "\n\x1b[1mtaskd 1.2.0\x1b[0m e2d145b built for linux\nCopyright (C) 2010 - 2016 G\xc3\xb6teborg Bit Factory.\n\nTaskd may be copied only under the terms of the MIT license, which may be found in the taskd source kit.\nDocumentation for taskd can be found using 'man taskd' or at http://taskwarrior.org\n\n"
        out = get_version()
        expected = {'git_rev': 'e2d145b', 'platform': 'linux', 'version': '1.2.0'}
        self.assertEqual(out, expected)
        patched_check_output.assert_called_with(["taskd", "-v"])

    @mock.patch('psutil.process_iter')
    def test_health_check(self, patched_process_iter):
        # patched_process_iter.side_effect = {"taskd"
        health_check()
        patched_process_iter.assert_called_with()



class IntegrationTest(unittest.TestCase):
    pass
    # def setUp(self):
    #     subprocess.check_output(["taskd", "add", "org", self.org], env={"TASKDDATA": "/var/lib/taskd"})

    # def tearDown(self):
    #     subprocess.check_output(["taskd", "remove", "org", self.org], env={"TASKDDATA": "/var/lib/taskd"})
