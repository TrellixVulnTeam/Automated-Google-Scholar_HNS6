import pytest

class Test_get_container:
    def test1(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()

        #setup for fake docker client
        m = mocker.patch("lib.docker.docker_helper.get_client")
        mock_client = mocker.MagicMock()
        m.return_value = mock_client

        import docker.errors
        mock_client.containers.get.side_effect = docker.errors.NotFound("MOCK")
        
        from lib.docker.container_helper import _Container_Helper as CH
        import lib.exceptions
        try:
            CH._get_container(_test_self, "test")
        except lib.exceptions.docker.No_such_container:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test2(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()

        #setup for fake docker client
        m = mocker.patch("lib.docker.docker_helper.get_client")
        mock_client = mocker.MagicMock()
        m.return_value = mock_client

        import docker.errors
        mock_client.containers.get.return_value = "test"
        
        from lib.docker.container_helper import _Container_Helper as CH
        _ret = CH._get_container(_test_self, "test")

        assert _ret == "test"

class Test_is_running:
    def test1(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()

        #setup for fake docker client
        m = mocker.patch("lib.docker.docker_helper.list_containers")
        m.return_value = []
        
        from lib.docker.container_helper import _Container_Helper as CH
        assert not CH._is_running(_test_self)

    def test2(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        type(_test_self)._id = "test"

        #setup for fake docker client
        m = mocker.patch("lib.docker.docker_helper.list_containers")
        mock_container_obj = mocker.MagicMock()
        type(mock_container_obj).id = "test"
        m.return_value = [mock_container_obj]
        
        from lib.docker.container_helper import _Container_Helper as CH
        assert CH._is_running(_test_self)

    def test3(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        type(_test_self)._id = "test"

        #setup for fake docker client
        m = mocker.patch("lib.docker.docker_helper.list_containers")
        mock_container_obj = mocker.MagicMock()
        type(mock_container_obj).id = "test2"
        m.return_value = [mock_container_obj]
        
        from lib.docker.container_helper import _Container_Helper as CH
        assert not CH._is_running(_test_self)

class Test_exec:
    def test1(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        _test_self._is_running.return_value = True
        
        from lib.docker.container_helper import _Container_Helper as CH
        CH.exec(_test_self, "test")

        _test_self._exec.assert_called()

    def test2(self, mocker):
        #setup the fake "self" object
        _test_self = mocker.MagicMock()
        _test_self._is_running.return_value = False

        from lib.docker.container_helper import _Container_Helper as CH
        import lib.exceptions as exp
        try:
            CH.exec(_test_self, "test")
        except exp.docker.Container_not_running:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

class Test_restart:
    def test1(self, mocker):
        _test_self = mocker.MagicMock()
        _test_self._is_running.return_value = False
        
        from lib.docker.container_helper import _Container_Helper as CH
        CH.restart(_test_self)

        _test_self._is_running.assert_called()
        _test_self._container.restart.assert_not_called()

    def test2(self, mocker):
        _test_self = mocker.MagicMock()
        _test_self._is_running.return_value = True
        
        from lib.docker.container_helper import _Container_Helper as CH
        CH.restart(_test_self)

        _test_self._is_running.assert_called()
        _test_self._container.restart.assert_called()

class Test_cp_to:
    def test1(self, mocker):
        _test_self = mocker.MagicMock()
        
        m1 = mocker.patch("lib.util.is_pathlike")
        m1.return_value = True

        from pathlib import Path
        m2 = mocker.patch.object(Path, "exists")
        m2.return_value = True

        from lib.docker.container_helper import _Container_Helper as CH
        CH.cp_to(_test_self, "some source dir", "some destination dir")

        _test_self._cp_to.assert_called()

    def test2(self, mocker):
        _test_self = mocker.MagicMock()
        
        m1 = mocker.patch("lib.util.is_pathlike")
        m1.return_value = False

        from pathlib import Path
        m2 = mocker.patch.object(Path, "exists")
        m2.return_value = True

        from lib.docker.container_helper import _Container_Helper as CH
        import lib.exceptions
        try:
            CH.cp_to(_test_self, "some source dir", "some destination dir")
        except lib.exceptions.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test3(self, mocker):
        _test_self = mocker.MagicMock()
        
        m1 = mocker.patch("lib.util.is_pathlike")
        m1.return_value = True

        from pathlib import Path
        m2 = mocker.patch.object(Path, "exists")
        m2.return_value = False

        from lib.docker.container_helper import _Container_Helper as CH
        import lib.exceptions
        try:
            CH.cp_to(_test_self, "some source dir", "some destination dir")
        except lib.exceptions.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test4(self, mocker, tmp_path):
        _test_self = mocker.MagicMock()
        _test_self._is_running.return_value = True
        
        m0 = mocker.patch("tempfile.TemporaryDirectory")
        m0.return_value = tmp_path

        mock_put = tmp_path / "put.tar"
        mock_put.touch()

        m1 = mocker.patch("shutil.copy")
        m2 = mocker.patch("tarfile.open")
        from tarfile import TarFile
        m3 = mocker.patch.object(TarFile, "add")

        from lib.docker.container_helper import _Container_Helper as CH
        res = CH._cp_to(_test_self, "some source dir", "some destination dir")

        _test_self._container.put_archive.assert_called()
        assert res == True

    def test5(self, mocker, tmp_path):
        _test_self = mocker.MagicMock()
        _test_self._is_running.return_value = False
        
        m0 = mocker.patch("tempfile.TemporaryDirectory")
        m0.return_value = tmp_path

        mock_put = tmp_path / "put.tar"
        mock_put.touch()

        m1 = mocker.patch("shutil.copy")
        m2 = mocker.patch("tarfile.open")
        from tarfile import TarFile
        m3 = mocker.patch.object(TarFile, "add")

        from lib.docker.container_helper import _Container_Helper as CH
        res = CH._cp_to(_test_self, "some source dir", "some destination dir")

        _test_self._container.put_archive.assert_not_called()

    def test6(self, mocker, tmp_path):
        _test_self = mocker.MagicMock()
        _test_self._is_running.return_value = True
        import docker
        _test_self._container.put_archive.side_effect = docker.errors.NotFound("BOOM")
        
        m0 = mocker.patch("tempfile.TemporaryDirectory")
        m0.return_value = tmp_path

        mock_put = tmp_path / "put.tar"
        mock_put.touch()

        m1 = mocker.patch("shutil.copy")
        m2 = mocker.patch("tarfile.open")
        from tarfile import TarFile
        m3 = mocker.patch.object(TarFile, "add")

        from lib.docker.container_helper import _Container_Helper as CH
        import lib.exceptions
        try:
            CH._cp_to(_test_self, "some source dir", "some destination dir")
        except lib.exceptions.Bad_Path:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")