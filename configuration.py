import os

HOST = '0.0.0.0'
PORT = 9098
TEST_TIMEOUT_S = 60
RUN_TIMEOUT_S = 60
ACCESS_TIMEOUT_S = 5

REPORT_SERVER_HOST = '<IP ADDRESS OF TARGET REPORT SERVER>'
REPORT_SERVER_PORT = 80
REPORT_SERVER_PATH = 'contest/jury/judge/automated/'

BASE_DIR = os.path.join(os.getenv("HOME"), "code", "webelopers", "judge")

TEST_MODULE = "main_func"
TEST_FILES_PATH = os.path.join(os.getenv("HOME"), "code", "webelopers", "w_test")

MAX_MEMORY_CONTESTANT = 50

PORT_COUNTER_START = 9000

REPO_PATH = "/home/soroushvt/code/webelopers/repositories"