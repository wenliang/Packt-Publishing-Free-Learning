import requests
import time

class AnticatpchaException(Exception):
    def __init__(self, error_id, error_code, error_description, *args):
        super(AnticatpchaException, self).__init__(error_description)
        self.error_id = error_id
        self.error_code = error_code


class NoCaptchaTaskProxylessTask(object):
    type = "NoCaptchaTaskProxyless"
    websiteURL = None
    websiteKey = None
    websiteSToken = None

    def __init__(self, website_url, website_key, website_s_token=None):
        self.websiteURL = website_url
        self.websiteKey = website_key
        self.websiteSToken = website_s_token

    def serialize(self):
        result = {'type': self.type,
                  'websiteURL': self.websiteURL,
                  'websiteKey': self.websiteKey}
        if self.websiteSToken:
            result.update({'websiteSToken': self.websiteSToken})
        return result


class Job(object):
    client = None
    task_id = None
    _last_result = None

    def __init__(self, client, task_id):
        self.client = client
        self.task_id = task_id

    def _update(self):
        self._last_result = self.client.getTaskResult(self.task_id)

    def check_is_ready(self):
        self._update()
        return self._last_result['status'] == 'ready'

    def get_solution_response(self):  # TODO: Support different captcha solutions
        return self._last_result['solution']['gRecaptchaResponse']

    def join(self):
        while not self.check_is_ready():
            time.sleep(3)


class AnticaptchaClient(object):
    client_key = None
    CREATE_TASK_URL = "https://api.anti-captcha.com/createTask"
    TASK_RESULT_URL = "https://api.anti-captcha.com/getTaskResult"
    SOFT_ID = 0  # TODO: Update to provide motivation for constant maintenance of the application. This does not increase the cost of using the application.
    language_pool = "en"

    def __init__(self, client_key, language_pool="en"):
        self.client_key = client_key
        self.language_pool = language_pool
        self.session = requests.Session()

    def check_response(self, response):
        if response.get('errorId', False):
            raise AnticatpchaException(response['errorId'],
                                       response['errorCode'],
                                       response['errorDescription'])

    def createTask(self, task):
        request = {"clientKey": self.client_key,
                   "task": task.serialize(),
                   "softId": self.SOFT_ID,
                   "languagePool": self.language_pool,
                   }
        response = self.session.post(self.CREATE_TASK_URL, json=request).json()
        self.check_response(response)
        return Job(self, response['taskId'])

    def getTaskResult(self, task_id):
        request = {"clientKey": self.client_key,
                   "taskId": task_id}
        response = self.session.post(self.TASK_RESULT_URL, json=request).json()
        self.check_response(response)
        return response

