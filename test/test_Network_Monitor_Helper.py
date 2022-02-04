import pytest

class Test_Network_Monitor_Helper:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        NMH.__init__(_self)
        assert True

    def test2(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        m1 = mocker.patch("lib.docker.service_helper._Service_Helper")
        mock_service = mocker.MagicMock()
        m1.return_value = mock_service

        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        NMH._setup(_self)

        mock_service.start.assert_called()

    def test3(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        _stop = _self._service.stop
        _tmp_log_dir = _self._tmp_log_dir
        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        NMH._teardown(_self)

        _stop.assert_called()
        _tmp_log_dir.cleanup.assert_called()

    def test4(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _tmp_log_dir = _self._tmp_log_dir
        type(_self)._tmp_log_dir = None

        _stop = _self._service.stop
        
        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        NMH._teardown(_self)

        _stop.assert_called()
        _tmp_log_dir.cleanup.assert_not_called()

    def test5(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        type(_self)._service = None
        type(_self)._container = None
        
        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        assert not NMH._is_running(_self)

    def test6(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        type(_self)._service = 1
        type(_self)._container = None
        
        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        assert not NMH._is_running(_self)

    def test7(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        type(_self)._service = None
        type(_self)._container = 1
        
        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        assert not NMH._is_running(_self)

    def test8(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        type(_self)._service = 1
        type(_self)._container = 1
        
        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        assert NMH._is_running(_self)

    def test9(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        mock_container = mocker.MagicMock()
        
        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        NMH._start_monitoring(_self, mock_container)

        mock_container.exec.assert_called()

    def test10(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        mock_container = mocker.MagicMock()
        
        m1 = mocker.patch("json.loads")
        m1.return_value = "test"
        
        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        res = NMH._was_up(_self, mock_container, "start time", "stop time")

        mock_container.exec.assert_called()
        assert res == "test"

    def test11(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._is_running.return_value = True
        
        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        assert NMH.start(_self) is None

    def test12(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._is_running.return_value = False
        
        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        res = NMH.start(_self)

        _self._setup.assert_called()
        _self._start_monitoring.assert_called()
        assert res > 0

    def test13(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._is_running.return_value = True
        _self._was_up.return_value = "test"

        mock_container = mocker.MagicMock()
        mock_start_time = 0
        
        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        res = NMH._stop(_self, mock_container, mock_start_time)

        _self._was_up.assert_called()
        _self._teardown.assert_called()
        assert res == "test"

    def test14(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._is_running.return_value = False
        _self._was_up.return_value = "test"

        mock_container = mocker.MagicMock()
        mock_start_time = 0
        
        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        res = NMH._stop(_self, mock_container, mock_start_time)

        _self._was_up.assert_not_called()
        _self._teardown.assert_not_called()
        assert res is None