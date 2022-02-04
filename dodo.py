'''
A configuration file for the task runner Doit
    see:
    https://pypi.org/project/doit/
    https://pydoit.org/
'''
def task_test():
    '''
    Here we run pytest in a special way, so that pytest is aware of the structure
    of the module, and so can import libraries into the tests correctly
    by default, pytest does not properly setup its environment as python would
    this has the result of not allowing the tests to properly import the modules
    they test
        see:
        https://stackoverflow.com/questions/20971619/ensuring-py-test-includes-the-application-directory-in-sys-path
    '''
    return {
        'actions': ['python -m pytest --quiet'],
    }

def task_test_verbose():
    return {
        'actions': ['python -m pytest --verbose'],
    }