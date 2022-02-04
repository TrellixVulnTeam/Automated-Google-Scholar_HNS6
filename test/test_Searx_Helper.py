import pytest

class Test_search:
    def test1(self, mocker, tmp_path):
        from lib.search.Searx_Helper import Searx_Helper
        m1 = mocker.patch.object(Searx_Helper, "run")

        import lib.search.Searx_Helper as SH
        SH.search("test")

        m1.assert_called()

class Test_Searx_Helper:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        from lib.docker.service_helper import _Service_Helper
        m1 = mocker.patch("lib.docker.service_helper._Service_Helper")
        mock_object = mocker.MagicMock()
        m1.return_value = mock_object
        
        from lib.search.Searx_Helper import Searx_Helper as SH
        SH._startup_service(_self, "some image name", 1)

        mock_object.start.assert_called()

    def test2(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._is_running.return_value = True

        mock_container = mocker.MagicMock()
        
        from lib.search.Searx_Helper import Searx_Helper as SH
        SH._configure_searx(_self, mock_container)

        mock_container.exec.assert_called()
        mock_container.cp_to.assert_called()
        mock_container.restart.assert_called()

    def test3(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        
        from lib.search.Searx_Helper import Searx_Helper as SH
        SH._setup(_self)

        _self._startup_service.assert_called()
        _self._configure_searx.assert_called()

    def test4(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        
        from lib.search.Searx_Helper import Searx_Helper as SH
        SH.run(_self)

        _self._setup.assert_called()
        _self._search.assert_called()
        _self._stop.assert_called()

    def test5(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        m1 = mocker.patch("requests.get")
        m1.return_value.json.return_value = {
            'results': [
                {'url': "some URL"}
            ],
        }
        
        mock_params = {
            'query' : "test",
            "page": 1
        }
        from lib.search.Searx_Helper import Searx_Helper as SH
        res = SH._search(_self, mock_params)

        assert len(res) == 1
        assert res[0] == "some URL"

    def test6(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        m1 = mocker.patch("requests.get")
        m1.return_value.json.return_value = {
            #'results': [
                #{'url': "some URL"}
            #],
        }
        
        mock_params = {
            'query' : "test",
            "page": 1
        }
        from lib.search.Searx_Helper import Searx_Helper as SH
        res = SH._search(_self, mock_params)

        assert len(res) == 0

    def test7(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        from lib.search.Searx_Helper import Searx_Helper as SH
        SH._stop(_self)

        assert _self._service is None
        assert _self._container is None

    def test8(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._service = mocker.MagicMock()

        _self._container = mocker.MagicMock()
        mock_exec_return = mocker.MagicMock()
        type(mock_exec_return).exit_code = 0
        _self._container.exec.return_value = mock_exec_return

        m1 = mocker.patch("requests.get")
        type(m1.return_value).status_code = 200

        from lib.search.Searx_Helper import Searx_Helper as SH
        res = SH._is_running(_self)

        assert res == True

    def test9(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        type(_self)._service = None

        _self._container = mocker.MagicMock()
        mock_exec_return = mocker.MagicMock()
        type(mock_exec_return).exit_code = 0
        _self._container.exec.return_value = mock_exec_return

        m1 = mocker.patch("requests.get")
        type(m1.return_value).status_code = 200

        from lib.search.Searx_Helper import Searx_Helper as SH
        res = SH._is_running(_self)

        assert res == False

    def test10(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._service = mocker.MagicMock()

        type(_self)._container = None
        #mock_exec_return = mocker.MagicMock()
        #type(mock_exec_return).exit_code = 0
        #_self._container.exec.return_value = mock_exec_return

        m1 = mocker.patch("requests.get")
        type(m1.return_value).status_code = 200

        from lib.search.Searx_Helper import Searx_Helper as SH
        res = SH._is_running(_self)

        assert res == False

    def test11(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._service = mocker.MagicMock()

        _self._container = mocker.MagicMock()
        mock_exec_return = mocker.MagicMock()
        type(mock_exec_return).exit_code = 1
        _self._container.exec.return_value = mock_exec_return

        m1 = mocker.patch("requests.get")
        type(m1.return_value).status_code = 200

        from lib.search.Searx_Helper import Searx_Helper as SH
        res = SH._is_running(_self)

        assert res == False

    def test12(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._service = mocker.MagicMock()

        _self._container = mocker.MagicMock()
        mock_exec_return = mocker.MagicMock()
        type(mock_exec_return).exit_code = 0
        _self._container.exec.return_value = mock_exec_return

        m1 = mocker.patch("requests.get")
        type(m1.return_value).status_code = "some bad status code"

        from lib.search.Searx_Helper import Searx_Helper as SH
        res = SH._is_running(_self)

        assert res == False

    def test13(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._service = mocker.MagicMock()

        _self._container = mocker.MagicMock()
        mock_exec_return = mocker.MagicMock()
        type(mock_exec_return).exit_code = 0
        _self._container.exec.return_value = mock_exec_return

        m1 = mocker.patch("requests.get")
        import requests
        m1.side_effect = requests.exceptions.RequestException()
        #type(m1.return_value).status_code = 200

        from lib.search.Searx_Helper import Searx_Helper as SH
        res = SH._is_running(_self)

        assert res == False