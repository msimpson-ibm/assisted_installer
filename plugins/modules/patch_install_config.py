#!/usr/bin/python

# Copyright: (c) 2023, Alberto Gonzalez <alberto.gonzalez@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import requests
import json

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.rhpds.assisted_installer.plugins.module_utils import access_token


DOCUMENTATION = r'''
---
module: patch_install_config

short_description: Override values in the install config.

version_added: "1.0.0"

description: Override values in the install config.

options:
    cluster_id:
        description: ID of the cluster
        required: true
        type: str

    offline_token:
        description: Offline token from console.redhat.com
        required: false
        type: str

    client_id:
        description: RH Service Account Client ID
        required: false
        type: str

    client_sercret:
        description: RH Service Account Client Secret
        required: false
        type: str

    install_config_params:
        description: Install config overrides (string with json)
        required: true
        type: str


author:
    - Alberto Gonzalez (@agonzalezrh)
'''

EXAMPLES = r'''
- name: Override values in the install config.
  register: r_patch_install_config
  rhpds.assisted_installer.patch_install_config:
    cluster_id: "{{ newcluster.result.id }}"
    offline_token: "{{ offline_token }}"
    install_config_params: '{"fips":true}'
'''

RETURN = r'''
result:
    description: Result from the API call
    type: dict
    returned: always
'''


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        cluster_id=dict(type='str', required=True),
        offline_token=dict(type='str', required=False),
        client_id=dict(type='str', required=False),
        client_secret=dict(type='str', required=False),
        install_config_params=dict(type='str', required=True),
    )

    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=5)
    session.mount('https://', adapter)

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_together=[['client_id', 'client_secret']]
    )

    if module.params['offline_token']:
        response = access_token._get_access_token(module.params['offline_token'])
    elif module.params['client_id'] and module.params['client_secret']:
        response = access_token._get_access_token(client_id=module.params['client_id'], client_secret=module.params['client_secret'])
    else:
        module.fail_json(msg="You must provide either offline_token or both client_id and client_secret.", **result)

    if response.status_code != 200:
        module.fail_json(msg='Error getting access token ', **response.json())
    result['access_token'] = response.json()["access_token"]

    headers = {
        "Authorization": "Bearer " + response.json()["access_token"],
        "Content-Type": "application/json",
        "Accept": "'application/json'"
    }
    response = session.patch(
        "https://api.openshift.com/api/assisted-install/v2/clusters/" + module.params['cluster_id'] + "/install-config",
        headers=headers,
        data=json.dumps(module.params["install_config_params"])
    )
    if len(str(response.content)) > 5:
        module.fail_json(msg='Request failed: ' + str(response.content))
    else:
        result['result'] = str(response.content)

    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
