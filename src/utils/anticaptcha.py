import requests
import time

from .logger import get_logger
logger = get_logger(__name__)


class AnticaptchaException(Exception):
    pass


class Anticaptcha(object):
    """
    anti-captcha.com client which helps to solve reCaptchas
    More info concerning the API: https://anti-captcha.com/apidoc/
    """
    api_url = 'https://api.anti-captcha.com'
    create_task_url = api_url + '/createTask'
    get_task_result_url = api_url + '/getTaskResult'
    # During busy periods, may need to wait more than 2 mins to solve Captcha.
    timeout_time_sec = 180  # timeout

    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()

    def __post_request(self, url, **kwargs):
        response = self.session.post(url, **kwargs).json()
        if response.get('errorId'):
            raise AnticaptchaException("Error {0} occured: {1}".format(
                response.get('errorCode'),
                response.get('errorDescription')
            ))
        return response

    def __create_noproxy_task(self, website_url, website_key):
        content = {
            'clientKey': self.api_key,
            'task': {
                "type": "NoCaptchaTaskProxyless",
                "websiteURL": website_url,
                "websiteKey": website_key
            }
        }
        response = self.__post_request(self.create_task_url, json=content)
        return response.get('taskId')

    def __wait_for_task_result(self, task_id):
        start_time = time.time()
        content = {
            'clientKey': self.api_key,
            'taskId': task_id
        }
        while (time.time() - start_time) < self.timeout_time_sec:
            response = self.__post_request(self.get_task_result_url, json=content)
            if response.get('status') == 'ready':
                return response
            time.sleep(1)
        raise AnticaptchaException('Timeout {} reached '.format(self.timeout_time_sec))

    def solve_recaptcha(self, website_url, website_key):
        task_id = self.__create_noproxy_task(website_url, website_key)
        logger.info('TaskId created: {}'.format(task_id))
        logger.info('Waiting for completion of the task: {}...'.format(task_id))
        solution = self.__wait_for_task_result(task_id)['solution']['gRecaptchaResponse']
        logger.success('Solution found for task: {}'.format(task_id))
        return solution
