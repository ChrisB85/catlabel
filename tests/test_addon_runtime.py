from __future__ import annotations

import os
import unittest
from unittest import mock

from catlabel.core.paths import data_dir, fonts_dir
from catlabel.__main__ import browser_launch_enabled


class DataDirectoryTests(unittest.TestCase):
    def test_defaults_to_relative_data_directory(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(data_dir(), "data")
            self.assertEqual(fonts_dir(), os.path.join("data", "fonts"))

    def test_follows_environment_override(self) -> None:
        with mock.patch.dict(os.environ, {"CATLABEL_DATA_DIR": "/data"}, clear=True):
            self.assertEqual(data_dir(), "/data")
            self.assertEqual(fonts_dir(), os.path.join("/data", "fonts"))

    def test_blank_override_is_ignored(self) -> None:
        with mock.patch.dict(os.environ, {"CATLABEL_DATA_DIR": ""}, clear=True):
            self.assertEqual(data_dir(), "data")


class BrowserLaunchTests(unittest.TestCase):
    def test_enabled_by_default(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertTrue(browser_launch_enabled())

    def test_disabled_by_environment(self) -> None:
        with mock.patch.dict(os.environ, {"CATLABEL_NO_BROWSER": "1"}, clear=True):
            self.assertFalse(browser_launch_enabled())

    def test_blank_value_leaves_it_enabled(self) -> None:
        with mock.patch.dict(os.environ, {"CATLABEL_NO_BROWSER": ""}, clear=True):
            self.assertTrue(browser_launch_enabled())


if __name__ == "__main__":
    unittest.main()
