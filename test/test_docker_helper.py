import pytest

'''
NOTE

in these tests we sometimes use a fixture named "mocker"
this fixture comes from pytest-mock
    see:
    https://pypi.org/project/pytest-mock/
it allows for functions like "spy" to monitor function calls
etc
'''

class Test_is_running:
    def test1(self, mocker):
        #patch the docker.from_env to avoid calling the real one
        mocker.patch("docker.from_env")

        import lib.docker.docker_helper as dh
        assert dh._is_running()

    def _raises_DockerException(self):
        from docker.errors import DockerException
        raise DockerException()

    def test2(self, mocker):
        #patch the docker.from_env to avoid calling the real one
        #and instead call our custom function which raises as expected
        import docker
        mocker.patch.object(docker, 'from_env', new=self._raises_DockerException)

        import lib.docker.docker_helper as dh
        assert (not dh._is_running())

'''
NOTE,
In these tests we use the pytest fixture for temporary paths for testing: tmp_path
    see:
    https://stackoverflow.com/questions/36070031/creating-a-temporary-directory-in-pytest
    https://docs.pytest.org/en/6.2.x/tmpdir.html
'''
class Test_is_command_present:
    def test1(self, mocker, tmp_path):
        def _return_valid_path(_arg):
            return tmp_path

        import shutil
        mocker.patch.object(shutil, 'which', new=_return_valid_path)

        import lib.docker.docker_helper as dh
        assert dh._is_command_present()

    def test2(self, mocker, tmp_path):
        def _return_none(_arg):
            return None

        import shutil
        mocker.patch.object(shutil, 'which', new=_return_none)

        import lib.docker.docker_helper as dh
        assert (not dh._is_command_present())

    def test3(self, mocker, tmp_path):
        def _return_bad_path(_arg):
            return "some bad path"

        import shutil
        mocker.patch.object(shutil, 'which', new=_return_bad_path)

        import lib.docker.docker_helper as dh
        assert (not dh._is_command_present())

'''
pytest.fail is also used when testing that the proper exception has been
thrown
    see:
    https://stackoverflow.com/questions/20274987/how-to-use-pytest-to-check-that-error-is-not-raised

for instance, here we check to see if the specific exception we're looking for
is thrown
and catch other exceptions and fail() on those
and then also, we check for if NO exception is thrown and fail() that too

try:
    worker._check_configs()
except e.File_does_not_exist as err:
    assert True
except Exception as err:
    pytest.fail(f"Saw unexpected exception: {err}")
else:
    pytest.fail(f"Did not throw exception as expected.")
'''
class Test_is_docker_ready:
    def test1(self, mocker, tmp_path):
        def _test():
            return False

        import lib.docker.docker_helper as dh
        mocker.patch.object(dh, '_is_command_present', new=_test)

        from lib.exceptions import docker

        try:
            dh._is_docker_ready()
        except docker.Could_not_find_executable:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test2(self, mocker, tmp_path):
        def _test():
            return False

        import lib.docker.docker_helper as dh
        mocker.patch.object(dh, '_is_running', new=_test)

        from lib.exceptions import docker

        try:
            dh._is_docker_ready()
        except docker.Docker_is_not_running:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test3(self, mocker, tmp_path):
        def _test():
            return True

        import lib.docker.docker_helper as dh
        mocker.patch.object(dh, '_is_running', new=_test)
        mocker.patch.object(dh, '_is_command_present', new=_test)

        assert dh._is_docker_ready()

'''
in these tests we sometimes use a fixture named "mocker"
this fixture comes from pytest-mock
    see:
    https://pypi.org/project/pytest-mock/
it allows for functions like "spy" to monitor function calls
etc
'''
class Test_in_swarm:
    def test1(self, mocker):
        def _test():
            import types
            _ret = types.SimpleNamespace()
            _ret.swarm = types.SimpleNamespace()
            _ret.swarm.attrs = dict()
            return _ret

        import docker
        mocker.patch.object(docker, 'from_env', new=_test)

        import lib.docker.docker_helper as dh
        assert (not dh._in_swarm())

    def test2(self, mocker):
        def _test():
            import types
            _ret = types.SimpleNamespace()
            _ret.swarm = types.SimpleNamespace()
            _ret.swarm.attrs = {"some key showing we're up": True}
            return _ret

        import docker
        mocker.patch.object(docker, 'from_env', new=_test)

        import lib.docker.docker_helper as dh
        assert dh._in_swarm()

'''
In these tests we mock the object returned from docker.from_env
we do this with a custom function that return a custom object
which then tracks calls to the internal function init()
    self._called = 0
    def _test2():
        def a():
            self._called += 1

        import types
        _ret = types.SimpleNamespace()
        _ret.swarm = types.SimpleNamespace()
        _ret.swarm.init = a
        return _ret
we make and remove a variable on self to track calls (_called)
'''
class Test_init_swarm:
    def test1(self, mocker):
        def _test():
            return False

        import lib.docker.docker_helper as dh
        mocker.patch.object(dh, '_in_swarm', new=_test)

        self._called = 0
        def _test2():
            def a():
                self._called += 1

            import types
            _ret = types.SimpleNamespace()
            _ret.swarm = types.SimpleNamespace()
            _ret.swarm.init = a
            return _ret

        import docker
        mocker.patch.object(docker, 'from_env', new=_test2)

        dh._init_swarm()
        assert (self._called == 1)

        del self._called

    def test1(self, mocker):
        def _test():
            return True

        import lib.docker.docker_helper as dh
        mocker.patch.object(dh, '_in_swarm', new=_test)

        self._called = 0
        def _test2():
            def a():
                self._called += 1

            import types
            _ret = types.SimpleNamespace()
            _ret.swarm = types.SimpleNamespace()
            _ret.swarm.init = a
            return _ret

        import docker
        mocker.patch.object(docker, 'from_env', new=_test2)

        dh._init_swarm()
        assert (self._called == 0)

        del self._called

class Test_get_client:
    @pytest.fixture(autouse=True)
    def _setup_and_teardown(self, mocker):
        '''
        Setup
        '''
        #mocking the docker import and docker.from_env()
        import sys
        sys.modules['docker'] = mocker.MagicMock()
        self.mock_client = mocker.MagicMock()
        sys.modules['docker'].from_env.return_value = self.mock_client

        yield

        '''
        Teardown
        '''
        del sys.modules['docker']
        del self.mock_client

    def test1(self, mocker):
        m = mocker.patch("lib.docker.docker_helper._is_docker_ready")

        import lib.docker.docker_helper as DH
        _ret = DH.get_client()

        import sys
        sys.modules['docker'].from_env.assert_called()
        m.assert_called()

class Test_list_containers:
    def test1(self, mocker):
        #setup for fake docker client
        m = mocker.patch("lib.docker.docker_helper._get_client")
        mock_client = mocker.MagicMock()
        m.return_value = mock_client

        import docker.errors as e
        mock_client.containers.list.side_effect = e.NotFound("MOCK")
        
        import lib.docker.docker_helper as DH
        _ret = DH.list_containers()

        assert len(_ret) == 0

    def test2(self, mocker):
        #setup for fake docker client
        m = mocker.patch("lib.docker.docker_helper._get_client")
        mock_client = mocker.MagicMock()
        m.return_value = mock_client

        class Mock_Exception(Exception): pass

        import docker.errors as e
        mock_client.containers.list.side_effect = Mock_Exception("MOCK")
        
        import lib.docker.docker_helper as DH
        try:
            _ret = DH.list_containers()
        except Mock_Exception :
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test3(self, mocker):
        #setup for fake docker client
        m = mocker.patch("lib.docker.docker_helper._get_client")
        mock_client = mocker.MagicMock()
        m.return_value = mock_client

        mock_client.containers.list.return_value = ["test"]
        
        import lib.docker.docker_helper as DH
        _ret = DH.list_containers()

        assert len(_ret) == 1
        assert _ret[0] == "test"

class Test_list_services:
    def test1(self, mocker):
        #setup for fake docker client
        m = mocker.patch("lib.docker.docker_helper._get_client")
        mock_client = mocker.MagicMock()
        m.return_value = mock_client
        
        import lib.docker.docker_helper as DH
        _ret = DH._list_services()

        assert len(_ret) == 0

    def test2(self, mocker):
        #setup for fake docker client
        m = mocker.patch("lib.docker.docker_helper._get_client")
        mock_client = mocker.MagicMock()
        m.return_value = mock_client

        mock_client.services.list.return_value = ["test"]
        
        import lib.docker.docker_helper as DH
        _ret = DH._list_services()

        assert len(_ret) == 1
        assert _ret[0] == "test"