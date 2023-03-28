# -*- coding: utf-8 -*-
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    author: Hugo F. Gonzalez @hugonz
    name: sqlite
    short_description: sqlite inventory source
    description:
        - Get inventory hosts from a local sqlite database file
        - Uses a YAML configuration file that ends with sqlite.(yml|yaml)
        - The inventory_hostname is always the 'Name' of the virtualbox instance.
        - Interpret a canonical DB structure for using this plugin out of the box or customize it for a custom DB.
    extends_documentation_fragment:
      - constructed
      - inventory_cache
    options:
        plugin:
            description: token that ensures this is a source file for the 'sqlite' plugin
            required: true
            choices: ['sqlite']
        db_url:
            description: The SQLite filename in url form sqlite:///<filename>
            type: string
            required: true
        running_only:
            description: toggles showing all vms vs only those currently running
            type: boolean
            default: false
        settings_password_file:
            description: provide a file containing the settings password (equivalent to --settingspwfile)
        network_info_path:
            description: property path to query for network information (ansible_host)
            default: "/VirtualBox/GuestInfo/Net/0/V4/IP"
        query:
            description: create vars from virtualbox properties
            type: dictionary
            default: {}
'''

EXAMPLES = '''
# file must be named vbox.yaml or vbox.yml
simple_config_file:
    plugin: community.general.virtualbox
    settings_password_file: /etc/virtulbox/secrets
    query:
      logged_in_users: /VirtualBox/GuestInfo/OS/LoggedInUsersList
    compose:
      ansible_connection: ('indows' in vbox_Guest_OS)|ternary('winrm', 'ssh')
# add hosts (all match with minishift vm) to the group container if any of the vms are in ansible_inventory'
plugin: community.general.virtualbox
groups:
  container: "'minis' in (inventory_hostname)"
'''
import os

from subprocess import Popen, PIPE

from ansible.errors import AnsibleParserError
from ansible.module_utils.common.text.converters import to_bytes, to_native, to_text
from ansible.module_utils.common._collections_compat import MutableMapping
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
from ansible.module_utils.common.process import get_bin_path

from ansible.plugins.inventory import BaseInventoryPlugin

class InventoryModule(BaseInventoryPlugin):

    NAME = 'sqlite'  # used internally by Ansible, it should match the file name but not required

    def verify_file(self, path):
        ''' return true/false if this is possibly a valid file for this plugin to consume '''
        valid = False
        if super(InventoryModule, self).verify_file(path):
            # base class verifies that file exists and is readable by current user
            if path.endswith(('sqlite.yaml', 'sqlite.yml')):
                valid = True
        return valid


