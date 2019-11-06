import pickle as pk
import sys
import time
from ast import literal_eval
from datetime import datetime, timedelta
from threading import Thread, Lock
from urllib.error import URLError
from urllib.request import urlopen

import configuration as config
import logger
import requests
import socket
import project_handler as projects
import test_runner as tests
from flask import Flask, request
from timeout_decorator import timeout, TimeoutError

app = Flask(__name__)

# groups submission status
group_status = {}

# port availability status
port_status = {}


def find_and_lock_port() -> int:
    port = config.PORT_COUNTER_START
    lock = Lock()
    while port < 65535:
        lock.acquire()
        if not port in port_status:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.bind(("localhost", port))
                port_status[port] = s
                return port
            except socket.error:
                pass
            finally:
                s.close()
        lock.release()
        port += 1
    logger.log_error("Could not find any port!")
    raise Exception("No Port Found")


def release_port(port: int) -> None:
    lock = Lock()
    lock.acquire()
    port_status.pop(port)
    lock.release()


def test_and_set_active(group_id):
    if group_id not in group_status:
        group_status[group_id] = {
            'test_active': False,
            'test_count': 0,
            'last_run': None,
        }

    if not group_status[group_id]['test_active']:
        group_status[group_id]['test_active'] = True
        group_status[group_id]['last_run'] = datetime.now()
        group_status[group_id]['test_count'] += 1
        return True
    elif datetime.now() - group_status[group_id]['last_run'] > timedelta(seconds=config.RUN_TIMEOUT_S):
        logger.log_info('releasing and reacquiring lock for group_id', group_id, 'due to run timeout')
        group_status[group_id]['last_run'] = datetime.now()
        group_status[group_id]['test_count'] += 1
        return True

    return False


def deactivate_status(group_id):
    group_status[group_id]['test_active'] = False


@app.route('/', methods=['GET', 'POST'])
def handle_request():
    request_data = request.form
    if 'test_id' not in request_data or 'group_id' not in request_data or 'git_url' not in request_data:
        logger.log_error('malformed post request data.')
        return 'malformed post request data.', 400

    group_id = request_data['group_id']

    if test_and_set_active(group_id):
        logger.log_info('lock acquired for team with group_id {}'.format(group_id))
        test_id = int(request_data['test_id'])
        git_url = request_data['git_url']
        logger.log_info(
            'test id {} was given for team with group_id {}'.format(
                test_id,
                group_id)
        )
        process_request(git_url=git_url, group_id=group_id, test_id=test_id)
        logger.log_success(
            'test for team with group_id {} initiated successfully'.format(group_id))
        return "success - test initiated"
    else:
        logger.log_error(
            'another test for team with group_id {} is in progress'.format(group_id))
        return "error - existing test in progress", 406


def check_url_availability(url):
    try:
        return_code = _check_url_availability(url)
    except (TimeoutError, URLError):
        return_code = 500

    return return_code == 200


@timeout(seconds=config.ACCESS_TIMEOUT_S, use_signals=False)
def _check_url_availability(url):
    return urlopen(url).getcode()


def worker_run_tests(git_url: str, test_id: int, group_id: str):
    test_results = {}
    container_id = None
    port = None

    project_handler = projects.DEFAULT_PROJECT_HANDLER

    try:
        port = find_and_lock_port()
        logger.log_log("Port {} acquired for group {} in test {}".format(port, group_id, test_id))
        image_id = project_handler.setup(repo_dir=config.REPO_PATH, group_id=group_id, git_url=git_url)
        container_id = project_handler.run(image_id=image_id, port=port)
        ip = "http://localhost"
        try:
            time.sleep(5)
            test_results = run_test(ip, port, test_id, group_id)
            test_results = {  # with assumption of is_accepted as first argument and log as second argument
                "is_accepted": test_results[0],
                "log": test_results[1],
            }
        except TimeoutError as e:
            test_results = {
                "is_accepted": False,
                "log": "timeout"
            }
    except Exception as e:
        test_results = {
            "is_accepted": False,
            "log": str(e),
        }
    finally:
        if port is not None:
            release_port(port)
        if container_id is not None:
            project_handler.kill(container_id)
    return test_results


def worker_function(git_url, group_id, test_id):
    logger.log_info(
        'running tests for team with group_id {} on git url {}'.format(group_id, git_url))
    test_results = worker_run_tests(git_url=git_url, test_id=test_id, group_id=group_id)
    logger.log_info('releasing lock for team with group_id {}'.format(group_id))
    deactivate_status(group_id)
    logger.log_info(
        'reporting test results for team with group_id {} on git url {} to competition server'.format(group_id,
                                                                                                      git_url))
    report_test_results(group_id=group_id, test_id=test_id, test_results=test_results)
    logger.log_success(
        'test for team with group_id {} finished successfully'.format(group_id))


def report_test_results(group_id, test_id, test_results):
    logger.log_log(
        'log report for team with group_id {} for test_id {}'.format(group_id, test_id))
    logger.log_log(test_results)
    test_results['group_id'] = group_id
    test_results['test_id'] = test_id
    try:
        requests.post(
            'http://{}:{}/{}'.format(config.REPORT_SERVER_HOST, config.REPORT_SERVER_PORT, config.REPORT_SERVER_PATH),
            test_results)
    except:
        logger.log_error("failed to report test {} results for team id {}".format(test_id, group_id))


def process_request(git_url, group_id, test_id):
    thread = Thread(target=worker_function, args=(git_url, group_id, test_id))
    thread.start()


@timeout(config.TEST_TIMEOUT_S, use_signals=False)
def run_test(ip, port, test_id, group_id):
    try:
        logger.log_info('starting django server for group {} on {}:{}'.format(group_id, ip, port))
        result, string_output = tests.run_test(
            config.TEST_FILES_PATH, config.TEST_MODULE, test_id, ip, port
        )
    except Exception as exception:
        logger.log_warn(
            'test for for team with group_id {} ended with exception'.format(group_id))
        print(exception)
        return False, ('Exception: ' + str(exception)), 'HMM'

    return result, string_output, 'HMM'


def runserver(port=config.PORT):
    app.run(host=config.HOST, port=port)


if __name__ == '__main__':

    try:
        if len(sys.argv) > 1:
            server_port = int(sys.argv[1])
            logger.log_info('starting server on custom port', server_port)
            runserver(server_port)
        else:
            logger.log_info('starting server on default port')
            runserver()
    except Exception as e:
        logger.log_error("app stoped with error".format(str(e)))

