import json

f = open('openapi.json')
data = json.load(f)
data = data.get('paths')
# print (json.dumps(data, indent=4, sort_keys=True))
keys = (data.keys())


def generate_get_functions(category, api_connection, api_version):
    """
    Generate functions for all GET calls for specified API resource.
    :param category: API resource to generate links for -- str

    returns: whole bunch of functions in a file eventually.
    """
    for uri_link in keys:
        if f'102/{category}' in uri_link:
            if 'get' in data.get(f'{uri_link}').keys():
                uri_detail = data.get(f'{uri_link}')
                function_name = (
                    (uri_detail.get('get').get('summary')).replace(" ", "_"))
                function_name = str(function_name).lower()
                function_description = (
                    uri_detail.get('get').get('summary'))
                param_list = []
                param_name_list = []
                path_params_list = []
                query_params_list = []
                query_params = "{"
                uri_parameters = (uri_detail.get('get').get(
                    'parameters'))
                if uri_parameters is None:
                    uri_parameters = []
                if len(uri_parameters) > 0:
                    for parameter in uri_parameters:
                        param_name_list.append(parameter.get('name'))
                        param_list.append(
                            f"param {parameter.get('name')}: "
                            f"{parameter.get('description')}"
                            f" -- {parameter.get('schema').get('type')}")
                        if parameter.get('in') == 'query':
                            query_params_list.append(parameter.get('name'))
                            query_params = (
                                    query_params + (
                                        f"\'{parameter.get('name')}\': "
                                        f"{parameter.get('name')},"))
                        elif parameter.get('in') == 'path':
                            path_params_list.append(parameter.get('name'))
                query_params = query_params + '}'
                path_param_name_list_string = ",".join(path_params_list)
                new_list = [s + '=None' for s in query_params_list]
                query_params_list = new_list
                query_params_list_string = ",".join(query_params_list)
                function_definition = (f"def {function_name} ("
                                       f"{path_param_name_list_string}")
                if len(query_params_list) > 0:
                    function_definition = function_definition + (
                        f", {query_params_list_string}):")
                else:
                    function_definition = function_definition + \
                                          ",array_id=None ):"
                print(function_definition)
                print(f"    \"\"\"{function_description}.")
                print()
                for param in param_list:
                    print(f"    :{param}")
                print("    :param array_id: The storage array ID -- string")
                print("    \"\"\"")
                print(f"    array_id = array_id if array_id else "
                      f"{api_connection}.array_id")
                print(f'    query_params = {query_params}')
                uri_link = uri_link.replace(api_version, "{self.version}")
                base_return = (
                    f"    return {api_connection}.common.get_request("
                    f"target_uri=f\""
                    f"{uri_link}\", "
                    f"resource_type=None, params=query_params)")
                print(base_return)
                print()


generate_get_functions(category='replication', api_connection='self',
                       api_version='102')
