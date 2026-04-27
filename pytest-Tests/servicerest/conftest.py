from contextlib import nullcontext

import pytest
import os
import requests
import json
import logging
from datetime import datetime

from  Utility.main import get_request_data ,base_url,get_updated_request_data ,get_variable ,compare_response_data,return_random_str,global_dict,admin_auth,headers,str_variable_dict,variable_dict


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
test_data_path = os.path.join(BASE_DIR,"Utility", "test_jsons")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
variables_data_path=os.path.join(BASE_DIR, "Utility", "variable_jsons")
# setting test user before running the tests and unsetting it after the tests are done


def setup_logging():
    log_filename = f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_filepath = os.path.join(LOGS_DIR, log_filename)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filepath),
            logging.StreamHandler()  # Also print to console
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()

def create_test_user(roles=None):
    """Helper function to create a test user with specified roles"""
    if roles is None:
        roles = ["ROLE_SYS_ADMIN"]

    request_data = get_request_data('create_user_for_test.json', global_dict, variables_data_path)

    # Update with roles
    fields_to_update = {
        "userRoleList": roles
    }

    updated_data = get_updated_request_data(request_data, fields_to_update)

    request_url = base_url + "/xusers/secure/users"
    resp = requests.post(request_url, verify=False, auth=admin_auth, headers=headers, data=json.dumps(updated_data))
    return resp.json()


# Create user objects with different roles
user1 = create_test_user(["ROLE_SYS_ADMIN"])
user2 = create_test_user(["ROLE_USER"])
user3 = create_test_user(["ROLE_USER"])
user4 = create_test_user(["ROLE_ADMIN_AUDITOR"])
user5 = create_test_user(["ROLE_KEY_ADMIN_AUDITOR"])
auditor_user= create_test_user(["ROLE_ADMIN_AUDITOR"])


@pytest.fixture(scope="session", autouse=True)
def setup_module():
    global resp_for_repeated_use
    variable_specifier_list = [
        ('plugin_definition_1_id', 'POST', '/plugins/definitions', 'plugin_definition_1_id.json', 'id'),
        ('plugin_definition_1', 'GET', '/plugins/definitions/{plugin_definition_1_id}', None, 'same'),
        ('plugin_definition_1_name', 'GET', '/plugins/definitions/{plugin_definition_1_id}', None, 'name'),
        ('policy_1_id', 'POST', '/plugins/policies', 'policy_1_id.json', 'id'),
        ('policy_1', 'GET', '/plugins/policies/{policy_1_id}', None, 'same'),
        ('policy_1_guid', 'GET', '/plugins/policies/{policy_1_id}', None, 'guid'),
        ('policy_1_resource', 'GET', '/plugins/policies/{policy_1_id}', None, 'resources,path,values,0'),
        ('service_1_id', 'POST', '/plugins/services', 'service_1_id.json', 'id'),
        ('service_1', 'GET', '/plugins/services/{service_1_id}', None, 'same'),
        ('service_1_name', 'GET', '/plugins/services/{service_1_id}', None, 'name'),
        ('policy_2_id', 'POST', '/plugins/policies', 'policy_2_id.json', 'id'),
        ('policy_3_id', 'POST', '/plugins/policies', 'policy_3_id.json', 'id')]

    for variable_specification in variable_specifier_list:
        variable_name = variable_specification[0]
        variable_dict[variable_name] = get_variable(variable_specification, str_variable_dict, variables_data_path)
        str_variable_dict[variable_name] = str(variable_dict[variable_name])
    request_url_for_repeated_use = base_url + '/plugins/policies/{policy_1_id}'
    request_url_for_repeated_use = request_url_for_repeated_use.format(**str_variable_dict)
    resp_for_repeated_use = requests.get(request_url_for_repeated_use, verify=False, auth=admin_auth, headers=headers)
    yield

# str_variable_dict['user20'] = user20
str_variable_dict['user1'] = user1.get('name')
str_variable_dict['user2'] = user2.get('name')
str_variable_dict['user3'] = user3.get('name')
str_variable_dict['user4'] = user4.get('name')
str_variable_dict['user5'] = user5.get('name')
str_variable_dict['auditor_user'] = auditor_user.get('name')



@pytest.fixture(scope="session")
def setup_for_import_export_policies():
    # create source hbase service
    request_url = base_url + '/plugins/services'
    request_data = get_request_data('test_create_hbase_service.json', str_variable_dict, test_data_path)


    source_service_name = request_data['name']
    resp = requests.post(request_url, verify=False, auth=admin_auth, headers=headers, data=json.dumps(request_data))

    # create destination hbase service
    request_data = get_request_data('test_create_hbase_service.json', str_variable_dict, test_data_path)

    resp = requests.post(request_url, verify=False, auth=admin_auth, headers=headers, data=json.dumps(request_data))
    destination_service_name = request_data['name']

    # create a policy in source service
    request_url = base_url + '/plugins/policies'
    request_data = get_request_data('test_create_hbase_policy.json', str_variable_dict, test_data_path)
    request_data['service'] = source_service_name
    policy_name_in_source_service = request_data['name']
    resp = requests.post(request_url, verify=False, auth=admin_auth, headers=headers, data=json.dumps(request_data))
    request_data['service'] = destination_service_name
    # policies in  source and destination have the same resource path and name
    policy_name_in_destination_service = request_data['name']
    resp = requests.post(request_url, verify=False, auth=admin_auth, headers=headers, data=json.dumps(request_data))
    # in the setup the path of both source policy and destination policy is same also the name is same
    destination_pre_existing_policy_id = resp.json().get('id')

    request_url = base_url + '/plugins/policies/exportJson?serviceName={}&checkPoliciesExists=true'.format(
        source_service_name)

    local_header = {
        'Accept': '*/*',
        'Content-Type': 'application/json',
        'X-XSRF-HEADER': 'valid'
    }

    exported_policies_from_source = requests.get(request_url, verify=False, auth=admin_auth, headers=local_header)
    exported_policies_from_source = exported_policies_from_source.json()

    assert resp.status_code == 200, "Export failed during setup"

    # Return the actual JSON content

    return {
        "source_service_name": source_service_name,
        "destination_service_name": destination_service_name,
        "exported_policies_from_source": exported_policies_from_source,
        "policy_name_in_source_service": policy_name_in_source_service,
        "policy_name_in_destination_service": policy_name_in_destination_service,
    }




@pytest.fixture(scope="session")
def create_policy_for_test():
    request_url = base_url + '/plugins/policies'
    request_data = get_request_data('test_create_policy.json', str_variable_dict, test_data_path)

    resp = requests.post(request_url, verify=False, auth=admin_auth, headers=headers, data=json.dumps(request_data))
    assert resp.status_code == 200, "Failed to create policy"

    policy_json = resp.json()
    policy_id = policy_json.get('id')

    return{
        "policy_id": policy_id,
        "policy_json": policy_json
    }





