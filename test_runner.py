import importlib.util
import sys
import os


def run_test(test_loc: str, test_module: str, test_id: int, ip: str, port: int):
    sys.path.append(test_loc)
    spec = importlib.util.spec_from_file_location(test_module, os.path.join(test_loc, "{}.py".format(test_module)))

    # TODO check if module exists
    test_handler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(test_handler)
    return test_handler.main_func(ip, port, test_id)

