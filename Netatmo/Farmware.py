import os
import json
import requests

#test
class Farmware():
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self):
        self.api_url = 'https://my.farmbot.io/api/'
        try:
            api_token = os.environ['API_TOKEN']
        except KeyError:
            raise ValueError('API_TOKEN not set')

        self.headers = {'Authorization': 'Bearer ' + api_token, 'content-type': "application/json"}

    # ------------------------------------------------------------------------------------------------------------------
    def handle_error(self, response):
        if response.status_code != 200:
            raise ValueError(
                "{} {} returned {}".format(response.request.method, response.request.path_url, response.status_code))
        return

    # ------------------------------------------------------------------------------------------------------------------
    def log(self, message, message_type='info'):

        try:
            log_message = '[{}] {}'.format(APP_NAME, message)
            node = {'kind': 'send_message', 'args': {'message': log_message, 'message_type': message_type}}
            response = requests.post(os.environ['FARMWARE_URL']+'api/v1/celery_script', data=json.dumps(node), headers=self.headers)
            self.handle_error(response)
            message = log_message
        except: pass

        print(message)

    # ------------------------------------------------------------------------------------------------------------------
    def get(self, enpoint):
        response = requests.get(self.api_url + enpoint, headers=self.headers)
        self.handle_error(response)
        return response.json()

    # ------------------------------------------------------------------------------------------------------------------
    def put(self, enpoint, data):
        response = requests.put(self.api_url + enpoint, headers=self.headers, data=json.dumps(data))
        self.handle_error(response)
        return response.json()

    # ------------------------------------------------------------------------------------------------------------------
    def execute_sequence(self, sequence, debug=False, message=''):
        if sequence['id'] != -1:
            if message != None:
                self.log('{}Executing sequence: {}({})'.format(message, sequence['name'], sequence['id']))
            if not debug:
                node = {'kind': 'execute', 'args': {'sequence_id': sequence['id']}}
                response = requests.post(os.environ['FARMWARE_URL'] + 'api/v1/celery_script', data=json.dumps(node),
                                         headers=self.headers)
                self.handle_error(response)

    # ------------------------------------------------------------------------------------------------------------------
    def move_absolute(self, location, offset, debug=False, message=''):

        if message!=None:
            self.log('{}Moving absolute: {} {}'.format(message, str(location), "" if offset=={'y': 0, 'x': 0, 'z': 0} else str(offset)))

        node = {'kind': 'move_absolute', 'args':
            {
                'location': {'kind': 'coordinate', 'args': location},
                'offset': {'kind': 'coordinate', 'args': offset},
                'speed': 300
            }
                }

        if not debug:
            response = requests.post(os.environ['FARMWARE_URL'] + 'api/v1/celery_script', data=json.dumps(node),
                                     headers=self.headers)
            self.handle_error(response)


