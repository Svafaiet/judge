import importlib.util

def run_test(test_loc: str, test_module: str, group_id: int, test_id: int):
    spec = importlib.util.spec_from_file_location(test_loc, test_module)
    # TODO check if module exists
    test_handler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)    
    # test_handle.run_test(group_id, test_id)
    # change name if neccessary
    

