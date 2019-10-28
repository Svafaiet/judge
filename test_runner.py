import importlib.util


def run_test(test_loc: str, test_module: str, test_id: int, ip: str, port: int):
    spec = importlib.util.spec_from_file_location(test_loc, test_module)
    # TODO check if module exists
    test_handler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(test_handler)
    test_handle.run_test(ip, port, test_id)
    
