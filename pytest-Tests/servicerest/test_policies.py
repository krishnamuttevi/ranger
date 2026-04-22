import requests
import json
import pytest
from  servicerest.Utility.main import get_request_data ,base_url,get_updated_request_data ,get_variable ,compare_response_data,return_random_str ,admin_auth ,headers,keyadmin_auth,str_variable_dict,variable_dict
from requests.auth import HTTPBasicAuth
import time
import os
from servicerest.conftest import user1, user2,user3,user4,user5

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Gets Tests_Ranger root
test_data_path = os.path.join(BASE_DIR,"Utility", "test_jsons")
data_folder_path = os.path.join(BASE_DIR, "Utility", "variable_jsons")
variables_data_path = data_folder_path





def test_get_policies_count_by_admin():
    request_url = base_url + '/plugins/policies/count'
    # logger.info("The request url is :- %s", request_url)
    resp = requests.get(request_url, verify=False, auth=admin_auth, headers=headers)
    # logger.info("The resp status code is :- %s", resp.status_code)
    # logger.info("The resp content is :- %s", resp.content)
    assert resp.status_code == 200, "Expected status code not returned"

def test_get_policies_count_by_different_roles():
    request_url = base_url + '/plugins/policies/count'
    resp1= requests.get(request_url, verify=False, auth=keyadmin_auth, headers=headers)
    assert resp1.status_code == 200, "Expected status code not returned"
    resp2= requests.get(request_url, verify=False, auth=HTTPBasicAuth(str_variable_dict['user2'], 'Test@12345'), headers=headers)
    assert resp2.status_code == 200, "Expected status code not returned"
    assert int(resp1.text.strip())>=int (resp2.text.strip()), "Different roles do not have expected view of policies count"

# @pytest.mark.L1
# @TaskReporter.report_test()
def test_get_policies_by_admin():
    request_url = base_url + '/plugins/policies'
    # logger.info("The request url is :- %s", request_url)
    resp = requests.get(request_url, verify=False, auth=admin_auth, headers=headers)
    # logger.info("The resp status code is :- %s", resp.status_code)
    # logger.info("The resp content is :- %s", resp.content)
    assert resp.status_code == 200, "Expected status code not returned"

def test_different_roles_has_different_view_of_policies():
    request_url = base_url + '/plugins/policies'
    resp_admin = requests.get(request_url, verify=False, auth=admin_auth, headers=headers)
    resp_keyadmin = requests.get(request_url, verify=False, auth=keyadmin_auth, headers=headers)
    resp_user2 = requests.get(request_url, verify=False, auth=HTTPBasicAuth(str_variable_dict['user2'], "Test@12345"), headers=headers)

    assert resp_admin.status_code == 200 and resp_keyadmin.status_code == 200 and resp_user2.status_code == 200, "Expected status code not returned"

    policies_admin = resp_admin.json()
    policies_keyadmin = resp_keyadmin.json()
    policies_user2 = resp_user2.json()

    assert len(policies_admin) >= len(policies_keyadmin) , "Different roles do not have expected view of policies"
    assert len(policies_admin) >= len(policies_user2) , "Different roles do not have expected view of policies"

def test_query_parameters_in_get_policies_api():
    request_url=base_url+'plugins/policies?startIndex=1&maxRows=50&sortBy=id&sortType=desc'
    resp = requests.get(request_url, verify=False, auth=admin_auth, headers=headers)
    resp=resp.json()
    request_url=base_url+'plugins/policies?startIndex=1&maxRows=50&sortBy=id&sortType=asc'
    resp1 = requests.get(request_url, verify=False, auth=admin_auth, headers=headers)
    assert resp.get('policies',[])[0].get('id')>=resp1.get('policies',[])[0].get('id') , "Sorting not working as expected"
    request_url = base_url + 'plugins/policies?startIndex=0&maxRows=50&sortBy=id&sortType=asc'
    resp3= requests.get(request_url, verify=False, auth=admin_auth, headers=headers)
    assert resp3.get('policies',[])[0].get('id')<=resp1.get('policies',[])[0].get('id')

# @TaskReporter.report_test()
def test_get_policies_by_auditor():
    request_url = base_url + '/plugins/policies'
    # logger.info("The request url is :- %s", request_url)
    resp = requests.get(request_url, verify=False, auth=HTTPBasicAuth(str_variable_dict['auditor_user'],'Test@12345'), headers=headers)
    # logger.info("The resp status code is :- %s", resp.status_code)
    # logger.info("The resp content is :- %s", resp.content)
    assert resp.status_code == 200, "Expected status code not returned"

# @TaskReporter.report_test()
def test_get_policies_by_keyadmin():
    request_url = base_url + '/plugins/policies'
    # logger.info("The request url is :- %s", request_url)
    resp = requests.get(request_url, verify=False, auth=keyadmin_auth, headers=headers)
    # logger.info("The resp status code is :- %s", resp.status_code)
    # logger.info("The resp content is :- %s", resp.content)
    assert resp.status_code == 200, "Expected status code not returned"

def test_get_policies_by_ROLE_USER():
    request_url = base_url + '/plugins/policies'
    # logger.info("The request url is :- %s", request_url)
    resp = requests.get(request_url, verify=False, auth=HTTPBasicAuth(str_variable_dict['user3'],'Test@12345'), headers=headers)
    # logger.info("The resp status code is :- %s", resp.status_code)
    # logger.info("The resp content is :- %s", resp.content)
    assert resp.status_code == 200, "Expected status code not returned"


def test_create_policy_by_admin():
    request_url = base_url + '/plugins/policies'
    request_data = get_request_data('test_create_policy.json', str_variable_dict, test_data_path)

    # logger.info("The request url is :- %s", request_url)
    # logger.info("The request data is :- %s", request_data)
    resp = requests.post(request_url, verify=False, auth=admin_auth, headers=headers, data=json.dumps(request_data))
    resp_json = resp.json()
    resp_id = resp_json.get('id')
    # logger.infon().get('id')
    # logger.in("The resp content is :- %s", resp.content)
    assert resp.status_code == 200, "Expected status code not returned"
    assert request_data.get('name') == resp_json.get('name'), "Expected name not returned in response , policy with random different name created instead"

    """
    Test Same policy should not be created again 
    """
    resp= requests.post(request_url, verify=False, auth=admin_auth, headers=headers, data=json.dumps(request_data))
    assert resp.status_code == 400, "Same policy with same resource and name  created again"

    """
    Test same  policy with same resource and different name should not be created again 
    """
    timestamp=time.time()
    original_name=request_data['name']
    request_data['name'] = f'Test policy modified+{timestamp}'
    resp= requests.post(request_url, verify=False, auth=admin_auth, headers=headers, data=json.dumps(request_data))
    assert resp.status_code == 400, "Same policy with same resource and different name  created again"
    """
    Test same policy with the same name and different resource should be created
    """
    request_data['resources']['path']['values'] = [f'/test_path_{timestamp}']
    request_data['name'] = original_name
    resp= requests.post(request_url, verify=False, auth=admin_auth, headers=headers, data=json.dumps(request_data))
    assert resp.status_code == 400, "Same policy with same name and different resource  created again"

def test_create_policy_by_auditor():
    request_url = base_url + '/plugins/policies'
    request_data = get_request_data('test_create_policy.json', str_variable_dict, test_data_path)
    # logger.info("The request url is :- %s", request_url)
    # logger.info("The request data is :- %s", request_data)
    resp = requests.post(request_url, verify=False, auth=HTTPBasicAuth(str_variable_dict['auditor_user'],"Test@12345"), headers=headers, data=json.dumps(request_data))
    # logger.info("The resp status code is :- %s", resp.status_code)
    # logger.info("The resp content is :- %s", resp.content)
    assert resp.status_code == 403, "Expected status code not returned"


def test_create_policy_by_keyadmin():
    request_url = base_url + '/plugins/policies'
    request_data = get_request_data('test_create_policy.json', str_variable_dict, test_data_path)
    # logger.info("The request url is :- %s", request_url)
    # logger.info("The request data is :- %s", request_data)
    resp = requests.post(request_url, verify=False, auth=keyadmin_auth, headers=headers, data=json.dumps(request_data))
    # logger.info("The resp status code is :- %s", resp.status_code)
    # logger.info("The resp content is :- %s", resp.content)
    assert resp.status_code == 400, "Expected status code not returned"



# @TaskReporter.report_test()
def test_create_policy_by_ROLE_USER():
    request_url = base_url + '/plugins/policies'
    request_data = get_request_data('test_create_policy.json', str_variable_dict, test_data_path)
    # logger.info("The request url is :- %s", request_url)
    # logger.info("The request data is :- %s", request_data)
    resp = requests.post(request_url, verify=False, auth=HTTPBasicAuth(str_variable_dict['user3'],'Test@12345'), headers=headers, data=json.dumps(request_data))
    # logger.info("The resp status code is :- %s", resp.status_code)
    # logger.info("The resp content is :- %s", resp.content)
    assert resp.status_code == 403, "Expected status code not returned,user with ROLE_USER should not be able to create policy"


# @pytest.mark.L1
# @TaskReporter.report_test()
def test_create_policies_using_apply_by_admin():
    request_url = base_url + '/plugins/policies/apply'
    request_data = get_request_data('test_create_policies_using_apply.json', str_variable_dict, test_data_path)
    # logger.info("The request url is :- %s", request_url)
    # logger.info("The request data is :- %s", request_data)
    resp = requests.post(request_url, verify=False, auth=admin_auth, headers=headers, data=json.dumps(request_data))
    # logger.info("The resp status code is :- %s", resp.status_code)
    # logger.info("The resp content is :- %s", resp.content)
    assert resp.status_code == 200, "Expected status code not returned"



# # @pytest.mark.L1
# # @TaskReporter.report_test()
def test_edit_policy_using_id_by_admin():
    request_url = base_url + '/plugins/policies/{policy_1_id}'
    request_url = request_url.format(**str_variable_dict)

    request_data = variable_dict["policy_1"]
    fields_to_update = {"description": "Modified description"}
    request_data = get_updated_request_data(request_data=request_data, fields_to_update=fields_to_update)
    # logger.info("The request url is :- %s", request_url)
    # logger.info("The request data is :- %s", request_data)
    resp = requests.put(request_url, verify=False, auth=admin_auth, headers=headers, data=json.dumps(request_data))
    # logger.info("The resp status code is :- %s", resp.status_code)
    # logger.info("The resp content is :- %s", resp.content)
    assert resp.status_code == 200, "Expected status code not returned"

def test_import_export_policy():
    """
    Tested for HBASE service
    """
    # create source hbase service
    request_url = base_url + '/plugins/services'
    request_data = get_request_data('test_create_hbase_service.json', str_variable_dict, test_data_path)
    source_service_name= request_data['name']
    resp = requests.post(request_url, verify=False, auth=admin_auth, headers=headers, data=json.dumps(request_data))

    # create destination hbase service
    request_data = get_request_data('test_create_hbase_service.json', str_variable_dict, test_data_path)
    resp= requests.post(request_url, verify=False, auth=admin_auth, headers=headers, data=json.dumps(request_data))
    destination_service_name= request_data['name']

    # create a policy in source service
    request_url = base_url + '/plugins/policies'
    request_data = get_request_data('test_create_hbase_policy.json', str_variable_dict, test_data_path)
    request_data['service'] = source_service_name
    resp = requests.post(request_url, verify=False, auth=admin_auth, headers=headers, data=json.dumps(request_data))

    # export the policy using export api
    request_url = base_url + '/plugins/policies/exportJson?serviceName={}&checkPoliciesExists=true'.format(
        source_service_name)

    local_header = {
        'Accept': '*/*',
        'Content-Type': 'application/json',
        'X-XSRF-HEADER': 'valid'
    }

    resp = requests.get(request_url, verify=False, auth=admin_auth, headers=local_header)
    assert resp.status_code == 200, "Expected status code not returned , export policies not working as expected "



    # 1. Capture the exported JSON data
    exported_data = resp.json()

    # 1. Define the import endpoint and parameters
    import_url = base_url + '/plugins/policies/importPoliciesFromFile'
    import_params = {
        'updateIfExists': 'true',
        'isOverride': 'false',
        'importType': 'hbase'
    }

    # 2. Prepare the Service Mapping
    # Maps the 'service' name found inside the JSON file to your new destination service
    services_mapping = {source_service_name: destination_service_name}

    #  Construct the Multipart Payload
    files = {
        'file': (
            'exported_policies.json',
            json.dumps(exported_data),
            'application/json'
        ),
        'servicesMapJson': (
            'servicesMapJson.json',
            json.dumps(services_mapping),
            'application/json'
        )
    }

    # 4. Headers
    # IMPORTANT: Remove 'Content-Type'. The 'requests' library adds it with the boundary automatically.
    import_headers = {
        'Accept': 'application/json',
        'X-XSRF-HEADER': 'valid'
    }

    # 5. Execute the Request
    import_resp = requests.post(
        import_url,
        verify=False,
        auth=admin_auth,
        headers=import_headers,
        params=import_params,
        files=files
    )

    # 6. Result Check
    assert import_resp.status_code == 204, f"Import failed: {import_resp.text}"
