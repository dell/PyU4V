import requests
import json
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
        print(json.dumps(json_obj, sort_keys=False, indent=2))

    def get(self, target_url, request_object=None):
        """Call the get request on the given url resource

        :param target_url: the target url
        :param request_object: the payload for the request, optional
        :return: response object, or None
        """
        response = None
        try:
            if request_object == None:
                response = self.session.get(url=target_url)
            else: # request_object is something
                response = self.session.get(url=target_url,
                                            data=json.dumps(request_object,
                                                            sort_keys=True,
                                                            indent=4))

        except Exception:
            print ("Can't GET to API server URL:  " + target_url)
            exit(1)

        #take the raw response text and deserialize it into a python object.
        try:
            response_object = json.loads(response.text)
        except Exception:
            response_object =None

        return response_object

    def post(self, target_url, request_object):
        """Call the post (create) request on the given url resource

        :param target_url: the target url
        :param request_object: the payload for the request
        :return: response object, or None
        """
        try:
            response = self.session.post(url=target_url,
                                        data=json.dumps(request_object,
                                                        sort_keys=True,
                                                        indent=4))

            #take the raw response text and deserialize it into a python object.
            try:
                response_object = json.loads(response.text)
            except Exception:
                response_object = None
            return response_object

        except Exception:
            print("Exception: Can't POST to API server URL:  " + target_url)
            exit(1)

    def put(self, target_url, request_object):
        """Call the put (edit) request on the given url resource

        :param target_url: the target url
        :param request_object: the payload for the request
        :return: response, if one returned
        """
        try:
            response = self.session.put(url=target_url,
                                        stream=True,
                                        data=json.dumps(request_object,
                                                        sort_keys=True,
                                                        indent=4))
            if response.status_code == 204:
                return None

            else:
                # take the raw response text and deserialize it into a python object.
                response = json.loads(response.text)
                return response

        except Exception as e:
            print (e)

    def delete(self, target_url):
        """Call the delete request on the given url resource

        :param target_url: the target url
        :return: status code - 204 if successful
        """
        try:
            response = self.session.delete(url=target_url,
                                           stream=True)
            return response.status_code

        except Exception as e:
            print(e)

    def close_session(self):
        """Close the current rest session
        """
        return self.session.close()

