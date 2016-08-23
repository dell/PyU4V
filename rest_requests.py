import requests
import json
import time
from requests.auth import HTTPBasicAuth

# Disable warnings from untrusted server certificates
try:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except Exception:
    print("Ignore messages related to insecure SSL certificates")


class Restful:
    def __init__(self, username, password, verifySSL=False, cert=None):

        self.session = requests.session()
        self.session.headers = {'content-type': 'application/json',
                                'accept': 'application/json'}
        self.session.auth = HTTPBasicAuth(username, password)
        self.session.verify = verifySSL
        self.session.cert = cert

    def print_json(self, json_obj):
        """Takes a REST response and formats the output for
        ease of reading

        :param json_obj: the unformatted json response object
        :returns formatted and printed json object
        """
        print(json.dumps(json_obj, sort_keys=False, indent=2))

    def get(self, target_uri, request_object=None):
        """Performs a GET request on the target URI, if there is
        an associated payload for the GET request, process params
        for inclusion in request payload

        :param target_uri: the REST targeted resource
        :param request_object: (optional) if included, the JSON
        request body which included additional filter params
        :returns: targeted resource JSON object
        """
        tries = 3
        while tries >= 0:
            try:
                try:
                    # if there is no additional GET parameters
                    if request_object == None:
                        response = self.session.get(headers=self.session.headers,
                                                    auth=self.session.auth,
                                                    verify=self.session.verify,
                                                    url=target_uri)

                    else:  # included GET parameters in request_object
                        response = self.session.get(headers=self.session.headers,
                                                    auth=self.session.auth,
                                                    verify=self.session.verify,
                                                    url=target_uri,
                                                    data=json.dumps(request_object,
                                                                    sort_keys=True,
                                                                    indent=4))

                    # deserialize response object to a python object
                    try:
                        response_object = json.loads(response.text)
                        return response_object

                    # if response cannot be deserialized, return dict
                    except:
                        print('DICT EXCEPTION')
                        return dict()

                except:
                    if tries == 0:
                        # If we keep failing, raise the exception for the outer exception
                        # handling to deal with
                        print('3 attempts unsuccessful - error')
                        raise
                    else:
                        # Wait a few seconds before retrying and hope the problem goes away
                        print('Attempt', tries)
                        time.sleep(2)
                        tries -= 1
                        continue

            except requests.HTTPError as error:
                # print('HTTP Error: ', error)
                raise
            except requests.URLRequired as error:
                # print('URL Error: ', error)
                raise
            except requests.ConnectionError as error:
                # print('Connection Error: ', error)
                raise

    def post(self, target_uri, request_object):
        """Performs a POST request on the target URI, if there is
        an associated payload for the GET request, process params
        for inclusion in request payload

        :param target_uri: the REST targeted resource
        :param request_object: the JSON request body
        which included additional filter params
        :returns: JSON object containing success message or
        failure message
        """
        tries = 3
        while tries >= 0:
            try:
                try:
                    response = self.session.post(url=target_uri,
                                                 headers=self.session.headers,
                                                 auth=self.session.auth,
                                                 verify=self.session.verify,
                                                 data=json.dumps(request_object,
                                                                 sort_keys=True,
                                                                 indent=4))

                    # deserialize response object to a python object
                    try:
                        response_object = json.loads(response.text)
                        return response_object
                    except:
                        print("API POST did not return JSON response")

                except:
                    if tries == 0:
                        # If we keep failing, raise the exception for the outer exception
                        # handling to deal with
                        print('3 attempts unsuccessful - error')
                        raise
                    else:
                        # Wait a few seconds before retrying and hope the problem goes away
                        print('Attempt', tries)
                        time.sleep(2)
                        tries -= 1
                        continue

            except requests.HTTPError as error:
                # print('HTTP Error: ', error)
                raise
            except requests.URLRequired as error:
                # print('URL Error: ', error)
                raise
            except requests.ConnectionError as error:
                # print('Connection Error: ', error)
                raise

    def put(self, target_uri, request_object=None):

        tries = 3
        while tries >= 0:
            try:
                try:
                    response = self.session.put(url=target_uri,
                                                stream=True,
                                                headers=self.session.headers,
                                                auth=self.session.auth,
                                                verify=self.session.verify,
                                                data=json.dumps(request_object,
                                                                sort_keys=True,
                                                                indent=4))

                    # deserialize response object to a python object
                    try:
                        response_object = json.loads(response.text)
                        return response_object
                    except:
                        print("API POST did not return JSON response")

                except:
                    if tries == 0:
                        # If we keep failing, raise the exception for the outer exception
                        # handling to deal with
                        print('3 attempts unsuccessful - error')
                        raise
                    else:
                        # Wait a few seconds before retrying and hope the problem goes away
                        print('Attempt', tries)
                        time.sleep(2)
                        tries -= 1
                        continue

            except requests.HTTPError as error:
                # print('HTTP Error: ', error)
                raise
            except requests.URLRequired as error:
                # print('URL Error: ', error)
                raise
            except requests.ConnectionError as error:
                # print('Connection Error: ', error)
                raise

    def delete(self, target_uri):

        tries = 3
        while tries >= 0:
            try:
                try:
                    response = self.session.delete(url=target_uri,
                                                   stream=True,
                                                   headers=self.session.headers,
                                                   auth=self.session.auth,
                                                   verify=self.session.verify,
                                                   timeout=100)

                    return response.status_code

                except:
                    if tries == 0:
                        # If we keep failing, raise the exception for the outer exception
                        # handling to deal with
                        print('3 attempts unsuccessful - error')
                        raise
                    else:
                        # Wait a few seconds before retrying and hope the problem goes away
                        print('Attempt', tries)
                        time.sleep(2)
                        tries -= 1
                        continue

            except requests.HTTPError:
                # print('HTTP Error: ', error)
                raise
            except requests.URLRequired:
                # print('URL Error: ', error)
                raise
            except requests.ConnectionError:
                # print('Connection Error: ', error)
                raise
            
    def close_session(self):
        """
        Close the current rest session
        """
        return self.session.close()
