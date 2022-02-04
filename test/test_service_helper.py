import pytest

class Test_check_for_image_name:
    def test1(self, mocker):
        _test_self = {}

        from lib.docker.service_helper import _Service_Helper as SH
        import lib.exceptions
        try:
            SH._check_for_image_name(_test_self, None)
        except lib.exceptions.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test2(self, mocker):
        _test_self = {}

        from lib.docker.service_helper import _Service_Helper as SH
        import lib.exceptions
        try:
            SH._check_for_image_name(_test_self, "")
        except lib.exceptions.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

'''
NOTE

In these tests we make a fake "self" object to pass in to test class methods
the self object should have some properties, so we do it in this special way
as per the docs:
    _test_self = mocker.MagicMock()
    _property = mocker.PropertyMock(return_value="test")
    type(_test_self)._image = _property
Where we setup a normal MagicMock object, which we then attach a mock property
(PropertyMock) to the object's type
    see:
    https://docs.python.org/3/library/unittest.mock.html#unittest.mock.PropertyMock
    https://stackoverflow.com/questions/11836436/how-to-mock-a-readonly-property-with-mock
'''
class Test_image:
    def test1(self, mocker):
        _test_self = mocker.MagicMock()
        _property = mocker.PropertyMock(return_value="test")
        type(_test_self)._docker_image = _property

        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH._image(_test_self, None)

        assert _ret == "test"

    def test2(self, mocker):
        _test_self = mocker.MagicMock()
        _property = mocker.PropertyMock(return_value="test")
        type(_test_self)._docker_image = _property

        _test_self._check_image_arg.return_value = "called it"

        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH._image(_test_self, "new image name")
        
        assert _ret == "test"
        _test_self._check_image_arg.assert_called()

'''
In this code we use the contruction:
@pytest.fixture(autouse=True)
def _setup_and_teardown():

which is a fixture that runs before and after each test
a "yield" is used to pause execution in the middle of the function
so that when it is ran after each test, it picks up where execution paused
after setup
    see:
    https://stackoverflow.com/questions/22627659/run-code-before-and-after-each-test-in-py-test

----

in these tests we use this formulation to test:

import sys
from unittest.mock import MagicMock
sys.modules['lib.docker.docker_helper'] = MagicMock()
sys.modules['lib.docker.docker_helper'].is_docker_ready = MagicMock(return_value=True)

what this does is to preload a name into sys.modules that maps to a module
imported into the code we're testing:

import lib.docker.docker_helper as dh
dh.is_docker_ready()

This way we can mock the functions within that module, when the module is imported
into the code being tested
as, for some stupid reason, we can't overwrite the module functions in the test
and undo them later, we have to use the sys.modules to make a global change
    see:
    https://stackoverflow.com/questions/43162722/mocking-a-module-import-in-pytest
    https://stackoverflow.com/questions/8658043/how-to-mock-an-import

--

In this instance, for whatever reason, we have to BOTH mock the module in
sys.modules AND use mocker.patch() in order to get the desired behaviour
of mocking the import of docker_helper

--

In these tests we extract the arguments that a method was called with
via the `.call_args.args` attributes
    see:
    https://stackoverflow.com/questions/31129350/python-unit-test-mock-get-mocked-functions-input-arguments
'''
class Test_start:
    @pytest.fixture(autouse=True)
    def _setup_and_teardown(self, mocker):
        '''
        Setup
        '''
        import sys
        sys.modules['lib.docker.docker_helper'] = mocker.MagicMock()

        #mocking the docker import and docker.from_env()
        import sys
        self.mock_client = mocker.MagicMock()
        sys.modules['docker'] = mocker.MagicMock()
        sys.modules['docker'].from_env.return_value = self.mock_client

        yield

        '''
        Teardown
        '''
        del sys.modules['lib.docker.docker_helper']
        del sys.modules['docker']
        del self.mock_client

    def test1(self, mocker):
        m = mocker.patch('lib.docker.docker_helper')
        m.in_swarm.return_value = True

        _test_self = mocker.MagicMock()

        from lib.docker.service_helper import _Service_Helper as SH
        SH.start(_test_self)

        _test_self._start.assert_called()
        m.is_docker_ready.assert_called()
        m.in_swarm.assert_called()
        m.init_swarm.assert_not_called()

    def test2(self, mocker):
        m = mocker.patch('lib.docker.docker_helper')
        m.in_swarm.return_value = False

        _test_self = mocker.MagicMock()

        from lib.docker.service_helper import _Service_Helper as SH
        SH.start(_test_self)

        _test_self._start.assert_called()
        m.is_docker_ready.assert_called()
        m.in_swarm.assert_called()
        m.init_swarm.assert_called()

    def test3(self, mocker):
        _test_self = mocker.MagicMock()
        _test_self._is_synchronized.return_value = True

        m0 = mocker.patch("uuid.uuid4")
        m0.return_value = "test"

        m1 = mocker.patch("subprocess.run")
        mock_run_ret = mocker.MagicMock()
        m1.return_value = mock_run_ret

        mock_run_ret.returncode = 0

        m2 = mocker.patch('lib.docker.docker_helper.list_services')
        mock_service = mocker.MagicMock()
        type(mock_service).name = "test"
        m2.return_value = [mock_service]

        from lib.docker.service_helper import _Service_Helper as SH
        SH._start(_test_self)

        _test_self._is_synchronized.assert_called()

    def test4(self, mocker):
        _test_self = mocker.MagicMock()
        _test_self._is_synchronized.return_value = True

        m0 = mocker.patch("uuid.uuid4")
        m0.return_value = "test"

        m1 = mocker.patch("subprocess.run")
        mock_run_ret = mocker.MagicMock()
        mock_run_ret.returncode = 0
        m1.return_value = mock_run_ret

        m2 = mocker.patch('lib.docker.docker_helper.list_services')
        m2.return_value = []

        from lib.docker.service_helper import _Service_Helper as SH
        import lib.exceptions as exp
        try:
            SH._start(_test_self)
        except exp.Could_not_launch_service:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test5(self, mocker):
        _test_self = mocker.MagicMock()
        _test_self._is_synchronized.return_value = True

        m0 = mocker.patch("uuid.uuid4")
        m0.return_value = "test"

        m1 = mocker.patch("subprocess.run")
        mock_run_ret = mocker.MagicMock()
        mock_run_ret.returncode = 1
        m1.return_value = mock_run_ret

        m2 = mocker.patch('lib.docker.docker_helper.list_services')
        mock_service = mocker.MagicMock()
        type(mock_service).name = "test"
        m2.return_value = [mock_service]

        from lib.docker.service_helper import _Service_Helper as SH
        import lib.exceptions as exp
        try:
            SH._start(_test_self)
        except exp.Could_not_launch_service:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test6(self, mocker):
        _test_self = mocker.MagicMock()
        _test_self._is_synchronized.return_value = True
        _test_self._mount.return_value = []
        _test_self._environment.return_value = []
        _test_self._publish.return_value = []

        mock_service_name = "test_name"

        m0 = mocker.patch("uuid.uuid4")
        m0.return_value = mock_service_name

        m1 = mocker.patch("subprocess.run")
        mock_run_ret = mocker.MagicMock()
        mock_run_ret.returncode = 0
        m1.return_value = mock_run_ret

        m2 = mocker.patch('lib.docker.docker_helper.list_services')
        mock_service = mocker.MagicMock()
        type(mock_service).name = mock_service_name
        m2.return_value = [mock_service]

        from lib.docker.service_helper import _Service_Helper as SH
        SH._start(_test_self)

        docker_command_string = m1.call_args.args[0]
        
        assert "docker service create" in docker_command_string
        assert "--name" in docker_command_string
        assert "--replicas" in docker_command_string
        assert "test_name" in docker_command_string

    def test7(self, mocker):
        _test_self = mocker.MagicMock()
        _test_self._is_synchronized.return_value = True
        _test_self._mount.return_value = [{
            "source" : "some_source_dir",
            "destination" : "some_destination_dir",
        }]
        _test_self._environment.return_value = []
        _test_self._publish.return_value = []

        mock_service_name = "test_name"

        m0 = mocker.patch("uuid.uuid4")
        m0.return_value = mock_service_name

        m1 = mocker.patch("subprocess.run")
        mock_run_ret = mocker.MagicMock()
        mock_run_ret.returncode = 0
        m1.return_value = mock_run_ret

        m2 = mocker.patch('lib.docker.docker_helper.list_services')
        mock_service = mocker.MagicMock()
        type(mock_service).name = mock_service_name
        m2.return_value = [mock_service]

        from lib.docker.service_helper import _Service_Helper as SH
        SH._start(_test_self)

        docker_command_string = m1.call_args.args[0]

        _test_self._mount.assert_called()
        assert "--mount" in docker_command_string
        assert "some_source_dir" in docker_command_string
        assert "some_destination_dir" in docker_command_string

    def test8(self, mocker):
        _test_self = mocker.MagicMock()
        _test_self._is_synchronized.return_value = True
        _test_self._mount.return_value = []
        _test_self._environment.return_value = [
        {"some_environment_key": "some_environment_value"}
        ]
        _test_self._publish.return_value = []

        mock_service_name = "test_name"

        m0 = mocker.patch("uuid.uuid4")
        m0.return_value = mock_service_name

        m1 = mocker.patch("subprocess.run")
        mock_run_ret = mocker.MagicMock()
        mock_run_ret.returncode = 0
        m1.return_value = mock_run_ret

        m2 = mocker.patch('lib.docker.docker_helper.list_services')
        mock_service = mocker.MagicMock()
        type(mock_service).name = mock_service_name
        m2.return_value = [mock_service]

        from lib.docker.service_helper import _Service_Helper as SH
        SH._start(_test_self)

        docker_command_string = m1.call_args.args[0]

        _test_self._environment.assert_called()
        assert "--env" in docker_command_string
        assert "some_environment_key" in docker_command_string
        assert "some_environment_value" in docker_command_string

    def test9(self, mocker):
        _test_self = mocker.MagicMock()
        _test_self._is_synchronized.return_value = True
        _test_self._mount.return_value = []
        _test_self._environment.return_value = []
        _test_self._publish.return_value = [
        {"external_port": "internal_port"}
        ]

        mock_service_name = "test_name"

        m0 = mocker.patch("uuid.uuid4")
        m0.return_value = mock_service_name

        m1 = mocker.patch("subprocess.run")
        mock_run_ret = mocker.MagicMock()
        mock_run_ret.returncode = 0
        m1.return_value = mock_run_ret

        m2 = mocker.patch('lib.docker.docker_helper.list_services')
        mock_service = mocker.MagicMock()
        type(mock_service).name = mock_service_name
        m2.return_value = [mock_service]

        from lib.docker.service_helper import _Service_Helper as SH
        SH._start(_test_self)

        docker_command_string = m1.call_args.args[0]

        _test_self._publish.assert_called()
        assert "--publish" in docker_command_string
        assert "external_port" in docker_command_string
        assert "internal_port" in docker_command_string

class Test_is_running:
    @pytest.fixture(autouse=True)
    def _setup_and_teardown(self, mocker):
        '''
        Setup
        '''

        #mocking the docker import and docker.from_env()
        import sys
        self.mock_client = mocker.MagicMock()
        sys.modules['docker'] = mocker.MagicMock()
        sys.modules['docker'].from_env.return_value = self.mock_client

        yield

        '''
        Teardown
        '''
        del sys.modules['docker']
        del self.mock_client

    def test1(self, mocker):
        _test_self = mocker.MagicMock()
        type(_test_self)._service = None

        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH._is_running(_test_self)

        assert (_ret == False)

    def test2(self, mocker):
        _test_self = mocker.MagicMock()
        type(_test_self)._service = None

        m = mocker.patch('lib.docker.docker_helper.is_docker_ready')
        m.side_effect = Exception('Boom!')

        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH._is_running(_test_self)

        assert (_ret == False)

    def test3(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        _mock_service = mocker.MagicMock()
        type(_mock_service).id = "test"
        type(_test_self)._service = _mock_service

        self.mock_client.services.list.return_value = []

        #mock_service_obj = {}
        #mock_service_obj['id'] = "test"
        #m.return_value = [mock_service_obj]

        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH._is_running(_test_self)

        assert (_ret == False)

    def test4(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        _mock_service = mocker.MagicMock()
        type(_mock_service).id = "test"
        type(_test_self)._service = _mock_service

        mock_service_obj = mocker.MagicMock()
        type(mock_service_obj).id = "test"
        self.mock_client.services.list.return_value = [mock_service_obj]

        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH._is_running(_test_self)

        assert (_ret == True)

    def test5(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        _mock_service = mocker.MagicMock()
        type(_mock_service).id = "test"
        type(_test_self)._service = _mock_service

        mock_service_obj = mocker.MagicMock()
        type(mock_service_obj).id = "test2"
        self.mock_client.services.list.return_value = [mock_service_obj]

        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH._is_running(_test_self)

        assert (_ret == False)

class Test_stop:
    def test1(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        _test_self._is_running.return_value = False

        #setup the fake "service" object
        _mock_service = mocker.MagicMock()
        type(_test_self)._service = _mock_service
        
        from lib.docker.service_helper import _Service_Helper as SH
        SH.stop(_test_self)

        _test_self._is_running.assert_called()
        _mock_service.remove.assert_not_called()

    def test2(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        _test_self._is_running.return_value = True

        #setup the fake "service" object
        _mock_service = mocker.MagicMock()
        type(_test_self)._service = _mock_service
        
        from lib.docker.service_helper import _Service_Helper as SH
        SH.stop(_test_self)

        _test_self._is_running.assert_called()
        _mock_service.remove.assert_called()

class Test_replicas:
    def test1(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        _test_self._kwargs = {}
        _test_self._kwargs['replicas'] = 1

        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH._replicas(_test_self)

        assert _ret == 1

    def test2(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        _test_self._kwargs = {}
        _test_self._kwargs['replicas'] = 1

        from lib.docker.service_helper import _Service_Helper as SH
        import lib.exceptions
        try:
            SH._replicas(_test_self, "test")
        except lib.exceptions.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test3(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        _test_self._kwargs = {}
        _test_self._kwargs['replicas'] = 1

        from lib.docker.service_helper import _Service_Helper as SH
        import lib.exceptions
        try:
            SH._replicas(_test_self, 0)
        except lib.exceptions.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test4(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        _test_self._kwargs = {}
        _test_self._kwargs['replicas'] = 1

        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH._replicas(_test_self, 2)

        assert _ret == 2

class Test_container_ids:
    @pytest.fixture(autouse=True)
    def _setup_and_teardown(self, mocker):
        '''
        Setup
        '''
        #mocking the docker import and docker.from_env()
        import sys
        self.mock_client = mocker.MagicMock()
        sys.modules['docker'] = mocker.MagicMock()
        sys.modules['docker'].from_env.return_value = self.mock_client

        yield

        '''
        Teardown
        '''
        del sys.modules['docker']
        del self.mock_client

    def test1(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        _test_self._service = mocker.MagicMock()

        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH._container_ids(_test_self)

        self.mock_client.containers.list.assert_called()
        _test_self._service.tasks.assert_called()

    def test2(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        _test_self._service.tasks.return_value = [{"test":None}]

        _mock_task = mocker.MagicMock()
        self.mock_client.containers.list.return_value = [_mock_task]

        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH._container_ids(_test_self)

        assert len(_ret) == 0

    def test3(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        _mock_task = {"Status": {"ContainerStatus": {"ContainerID": "test"}} }
        _test_self._service.tasks.return_value = [_mock_task]

        assert _mock_task["Status"]["ContainerStatus"]["ContainerID"] == "test"

        #setup the fake container returned by the Docker client
        _mock_container = mocker.MagicMock()
        type(_mock_container).id = "test"

        assert _mock_container.id == "test"

        self.mock_client.containers.list.return_value = [_mock_container]

        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH._container_ids(_test_self)

        assert len(_ret) == 1
        assert _ret[0] == "test"

    def test4(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        _mock_task = {"Status": {"ContainerStatus": {"ContainerID": ""}} }
        _test_self._service.tasks.return_value = [_mock_task]

        #setup the fake container returned by the Docker client
        _mock_container = mocker.MagicMock()
        type(_mock_container).id = "test"

        self.mock_client.containers.list.return_value = [_mock_container]

        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH._container_ids(_test_self)

        assert len(_ret) == 0

    r'''
    Testing for intermitent error:

    Traceback (most recent call last):
    File "main.py", line 93, in <module>
    main()
    File "main.py", line 15, in main
    _sh.start()
    File "C:\Users\pmatt\Documents\Professional Work\Work\dev\dev, scraping\dev\lib\docker\service_helper.py", line 31, in start
    self._service = self._start()
    File "C:\Users\pmatt\Documents\Professional Work\Work\dev\dev, scraping\dev\lib\docker\service_helper.py", line 46, in _start
    if self._is_synchronized():
    File "C:\Users\pmatt\Documents\Professional Work\Work\dev\dev, scraping\dev\lib\docker\service_helper.py", line 107, in _is_synchronized
    _ids = self._container_ids()
    File "C:\Users\pmatt\Documents\Professional Work\Work\dev\dev, scraping\dev\lib\docker\service_helper.py", line 79, in _container_ids
    for _container in client.containers.list():
    File "C:\Users\pmatt\anaconda3\envs\dev1_2\lib\site-packages\docker\models\containers.py", line 961, in list
    containers.append(self.get(r['Id']))
    File "C:\Users\pmatt\anaconda3\envs\dev1_2\lib\site-packages\docker\models\containers.py", line 897, in get
    resp = self.client.api.inspect_container(container_id)
    File "C:\Users\pmatt\anaconda3\envs\dev1_2\lib\site-packages\docker\utils\decorators.py", line 19, in wrapped
    return f(self, resource_id, *args, **kwargs)
    File "C:\Users\pmatt\anaconda3\envs\dev1_2\lib\site-packages\docker\api\container.py", line 771, in inspect_container
    return self._result(
    File "C:\Users\pmatt\anaconda3\envs\dev1_2\lib\site-packages\docker\api\client.py", line 274, in _result
    self._raise_for_status(response)
    File "C:\Users\pmatt\anaconda3\envs\dev1_2\lib\site-packages\docker\api\client.py", line 270, in _raise_for_status
    raise create_api_error_from_http_exception(e)
    File "C:\Users\pmatt\anaconda3\envs\dev1_2\lib\site-packages\docker\errors.py", line 31, in create_api_error_from_http_exception
    raise cls(e, response=response, explanation=explanation)
    docker.errors.NotFound: 404 Client Error for http+docker://localnpipe/v1.41/containers/16d183c9e6f50fa570e430ec6acf6411d2013b1321dab45dd455c0f7fcd5deb4/json: Not Found ("No such container: 16d183c9e6f50fa570e430ec6acf6411d2013b1321dab45dd455c0f7fcd5deb4")
    '''

    def test5(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()

        class Mock_Exception(Exception): pass

        #setup the fake container returned by the Docker client
        _mock_container = mocker.MagicMock()
        self.mock_client.containers.list.side_effect = Mock_Exception()

        from lib.docker.service_helper import _Service_Helper as SH
        try:
            SH._container_ids(_test_self)
        except Mock_Exception:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test6(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()

        class Mock_Exception(Exception): pass

        #setup the fake container returned by the Docker client
        _mock_container = mocker.MagicMock()

        import docker.errors
        self.mock_client.containers.list.side_effect = docker.errors.NotFound("MOCK")

        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH._container_ids(_test_self)

        assert len(_ret) == 0

class Test_is_synchronized:
    def test1(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        _test_self._container_ids.return_value = []
        kwargs = {}
        kwargs['replicas'] = 1
        type(_test_self)._kwargs = kwargs

        from lib.docker.service_helper import _Service_Helper as SH
        assert ( not SH._is_synchronized(_test_self) )

    def test2(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        _test_self._container_ids.return_value = ["test"]
        kwargs = {}
        kwargs['replicas'] = 1
        type(_test_self)._kwargs = kwargs

        from lib.docker.service_helper import _Service_Helper as SH
        assert ( SH._is_synchronized(_test_self) )

class Test_containers:
    def test1(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        _test_self._is_running.return_value = False

        mocker.patch("lib.docker.docker_helper.is_docker_ready")

        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH.containers(_test_self)
        
        assert len(_ret) == 0
        _test_self._is_running.assert_called()

    def test2(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        _test_self._is_running.return_value = True
        _test_self._container_ids.return_value = ["test"]

        #setup fake container helper
        m = mocker.patch("lib.docker.container_helper.get_container")
        m.return_value = "test"
        
        mocker.patch("lib.docker.docker_helper.is_docker_ready")

        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH.containers(_test_self)
        
        assert len(_ret) == 1
        assert _ret[0] == "test"

    def test3(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        _test_self._is_running.return_value = True
        _test_self._container_ids.return_value = ["test"]

        #setup fake container helper
        m = mocker.patch("lib.docker.container_helper.get_container")
        m.return_value = "test"

        import lib.exceptions as exp
        m.side_effect = exp.docker.No_such_container("test")
        
        mocker.patch("lib.docker.docker_helper.is_docker_ready")

        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH.containers(_test_self)
        
        assert len(_ret) == 0

'''
NOTE

In this testing we have patch pathlib.Path
They work in a special way, so we have to patch the object Path
rather than the name pathlib.Path
    see:
    https://stackoverflow.com/questions/48864027/how-do-i-patch-the-pathlib-path-exists-method
'''
class Test_mount:
    def test1(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()

        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH.mount(_test_self)

        _test_self._mount.assert_called()

    def test2(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()

        from lib.docker.service_helper import _Service_Helper as SH
        import lib.exceptions
        try:
            _ret = SH.mount(_test_self, "src")
        except lib.exceptions.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test3(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()

        from pathlib import Path
        m = mocker.patch.object(Path, "exists")
        m.return_value = False

        from lib.docker.service_helper import _Service_Helper as SH
        import lib.exceptions
        try:
            _ret = SH.mount(_test_self, "src", "dst")
        except lib.exceptions.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test4(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()

        from lib.docker.service_helper import _Service_Helper as SH
        import lib.exceptions
        try:
            _ret = SH.mount(_test_self, "src", 42)
        except lib.exceptions.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test5(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()

        m = mocker.patch("platform.system")
        m.return_value = 'Windows'

        m2 = mocker.patch("lib.util.get_short_path_name")
        m2.return_value = "test"

        from pathlib import Path
        m3 = mocker.patch.object(Path, "exists")
        m3.return_value = True

        from lib.docker.service_helper import _Service_Helper as SH
        SH.mount(_test_self, "src", "dst")

        _test_self._mount.assert_called()

    def test6(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        kwargs = {}
        kwargs['mounts'] = "test"
        type(_test_self)._kwargs = kwargs
        
        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH._mount(_test_self)

        assert _ret == "test"

    def test7(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        kwargs = {}
        kwargs['mounts'] = []
        type(_test_self)._kwargs = kwargs
        
        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH._mount(_test_self, "src", "dst")

        _test_result = {
            "source": "src",
            "destination": "dst",
            }
        
        assert len(_ret) == 1
        assert _ret[0] == _test_result

class Test_environment:
    def test1(self, mocker):
        _test_self = mocker.MagicMock()

        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH.environment(_test_self)

        _test_self._environment.assert_called()

    def test2(self, mocker):
        _test_self = mocker.MagicMock()

        from lib.docker.service_helper import _Service_Helper as SH
        import lib.exceptions
        try:
            _ret = SH.environment(_test_self, "some key value")
        except lib.exceptions.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test3(self, mocker):
        _test_self = mocker.MagicMock()

        from lib.docker.service_helper import _Service_Helper as SH
        import lib.exceptions
        try:
            _ret = SH.environment(_test_self, None, "some value")
        except lib.exceptions.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test4(self, mocker):
        _test_self = mocker.MagicMock()
        _test_self._kwargs = {
            'environment_variables': [{"key": "value"}]
        }

        from lib.docker.service_helper import _Service_Helper as SH
        res = SH._environment(_test_self)

        assert len(res) == 1
        assert res[0] == {"key": "value"}

    def test5(self, mocker):
        _test_self = mocker.MagicMock()
        _test_self._kwargs = {
            'environment_variables': [{"key": "value"}]
        }

        from lib.docker.service_helper import _Service_Helper as SH
        res = SH._environment(_test_self, "new key", "new value")

        assert len(res) == 2
        
        _keys = set([[*_d.keys()][0]  for _d in res])
        _values = set([[*_d.values()][0]  for _d in res])

        assert "key" in _keys
        assert "new key" in _keys
        assert "value" in _values
        assert "new value" in _values

class Test_publish:
    def test1(self, mocker):
        _test_self = mocker.MagicMock()

        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH.publish(_test_self)

        _test_self._publish.assert_called()

    def test2(self, mocker):
        _test_self = mocker.MagicMock()

        from lib.docker.service_helper import _Service_Helper as SH
        import lib.exceptions
        try:
            _ret = SH.publish(_test_self, "new port")
        except lib.exceptions.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test3(self, mocker):
        _test_self = mocker.MagicMock()

        from lib.docker.service_helper import _Service_Helper as SH
        import lib.exceptions
        try:
            _ret = SH.publish(_test_self, None, "new target")
        except lib.exceptions.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test4(self, mocker):
        _test_self = mocker.MagicMock()

        m1 = mocker.patch( "lib.util.is_int" )
        m1.return_value = False

        from lib.docker.service_helper import _Service_Helper as SH
        import lib.exceptions
        try:
            _ret = SH.publish(_test_self, "new port", "new target")
        except lib.exceptions.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test5(self, mocker):
        _test_self = mocker.MagicMock()

        m1 = mocker.patch( "lib.util.is_int" )
        m1.return_value = True
        
        from lib.docker.service_helper import _Service_Helper as SH
        import lib.exceptions
        try:
            _ret = SH.publish(_test_self, -1, 65535+1)
        except lib.exceptions.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test6(self, mocker):
        _test_self = mocker.MagicMock()

        from lib.docker.service_helper import _Service_Helper as SH
        _ret = SH.publish(_test_self, 1, 2)

        _test_self._publish.assert_called()

    def test7(self, mocker):
        _test_self = mocker.MagicMock()
        _test_self._kwargs = {
            'port_mappings': [{"published": "target"}]
        }

        from lib.docker.service_helper import _Service_Helper as SH
        res = SH._publish(_test_self)

        assert len(res) == 1
        assert res[0] == {"published": "target"}

    def test8(self, mocker):
        _test_self = mocker.MagicMock()
        _test_self._kwargs = {
            'port_mappings': [{"published": "target"}]
        }

        from lib.docker.service_helper import _Service_Helper as SH
        res = SH._publish(_test_self, "new publish", "new target")

        assert len(res) == 2
        
        _keys = set([[*_d.keys()][0]  for _d in res])
        _values = set([[*_d.values()][0]  for _d in res])

        assert "published" in _keys
        assert "new publish" in _keys
        assert "target" in _values
        assert "new target" in _values