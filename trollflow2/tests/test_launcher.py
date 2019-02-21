#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 Pytroll developers
#
# Author(s):
#
#   Martin Raspaud <martin.raspaud@smhi.se>
#   Panu Lahtinen <pnuu+git@iki.fi>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import unittest
import yaml
try:
    from unittest import mock
except ImportError:
    import mock
import datetime as dt

yaml_test1 = """common:
  something: foo
  min_coverage: 5.0
product_list:
  euron1:
    areaname: euron1
    min_coverage: 20.0
    priority: 1
    products:
      ctth:
        productname: cloud_top_height
        output_dir: /tmp/satdmz/pps/www/latest_2018/
        formats:
          - format: png
            writer: simple_image
          - format: jpg
            writer: simple_image
            fill_value: 0
        fname_pattern: "{platform_name:s}_{start_time:%Y%m%d_%H%M}_{areaname:s}_ctth.{format}"

  germ:
    areaname: germ
    fname_pattern: "{start_time:%Y%m%d_%H%M}_{areaname:s}_{productname}.{format}"
    products:
      cloudtype:
        productname: cloudtype
        output_dir: /tmp/satdmz/pps/www/latest_2018/
        formats:
          - format: png
            writer: simple_image

  omerc_bb:
    areaname: omerc_bb
    output_dir: /tmp
    products:
      ct:
        productname: ct
        formats:
          - format: nc
            writer: cf
      cloud_top_height:
        productname: cloud_top_height
        formats:
          - format: tif
            writer: geotiff
"""

class TestGetAreaPriorities(unittest.TestCase):

    def test_get_area_priorities(self):
        from trollflow2.launcher import get_area_priorities
        prodlist = yaml.load(yaml_test1)

        priorities = get_area_priorities(prodlist)
        self.assertTrue(1 in priorities)
        self.assertTrue(isinstance(priorities[1], list))
        self.assertTrue('euron1' in priorities[1])
        self.assertTrue(999 in priorities)
        self.assertTrue(isinstance(priorities[999], list))
        self.assertTrue('omerc_bb' in priorities[999])
        self.assertTrue('germ' in priorities[999])


class TestMessageToJobs(unittest.TestCase):

    def test_message_to_jobs(self):
        from trollflow2.launcher import message_to_jobs
        prodlist = yaml.load(yaml_test1)
        msg = mock.MagicMock()
        msg.data = {'uri': 'foo'}

        jobs = message_to_jobs(msg, prodlist)
        self.assertEqual(set(jobs.keys()), {1, 999})
        for i in jobs.keys():
            self.assertEqual(set(jobs[i].keys()),
                             {'input_filenames', 'input_mda', 'product_list'})
            self.assertEqual(jobs[i]['input_filenames'], ['foo'])
            self.assertEqual(jobs[i]['input_mda'], msg.data)
            self.assertEqual(set(jobs[i]['product_list'].keys()),
                             {'common', 'product_list'})
        self.assertEqual(set(jobs[1]['product_list']['product_list'].keys()),
                         set(['euron1']))
        self.assertEqual(set(jobs[999]['product_list']['product_list'].keys()),
                         set(['germ', 'omerc_bb']))


def suite():
    """The test suite for test_writers."""
    loader = unittest.TestLoader()
    my_suite = unittest.TestSuite()
    my_suite.addTest(loader.loadTestsFromTestCase(TestGetAreaPriorities))
    my_suite.addTest(loader.loadTestsFromTestCase(TestMessageToJobs))

    return my_suite


if __name__ == '__main__':
    unittest.main()
