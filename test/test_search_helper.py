import pytest

class Test_search:
    def test1(self, mocker, tmp_path):
        m1 = mocker.patch("lib.search._search_input_validator")
        m2 = mocker.patch("lib.search.search_helper._try_engine")
        m2.return_value = ["some results"]

        import lib.search.search_helper as sh
        res = sh.search("test")

        assert len(res) == 1
        assert res[0] == "some results"

    def test2(self, mocker, tmp_path):
        m1 = mocker.patch("lib.search._search_input_validator")
        m2 = mocker.patch("lib.search.search_helper._try_engine")
        m2.return_value = []

        import lib.search.search_helper as sh
        res = sh.search("test")

        assert len(res) == 0

class Test_try_engine:
    def test1(self, mocker, tmp_path):
        m1 = mocker.patch("lib.util.network_connected")
        m1.return_value = False

        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        m2 = mocker.patch.object(NMH, "start")

        #prevent the infinite loop from running
        class mock_Exception(Exception): pass
        m3 = mocker.patch("time.sleep")
        m3.side_effect = mock_Exception()

        mock_engine = mocker.MagicMock()
        mock_params = {}
        import lib.search.search_helper as sh
        try:
            res = sh._try_engine(mock_engine, mock_params)
        except mock_Exception:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

        m2.assert_not_called()

    def test2(self, mocker, tmp_path):
        m1 = mocker.patch("lib.util.network_connected")
        m1.return_value = True

        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        m2 = mocker.patch.object(NMH, "start")

        m3 = mocker.patch.object(NMH, "stop")
        m3.return_value = True

        #prevent the infinite loop from running
        class mock_Exception(Exception): pass
        m4 = mocker.patch("time.sleep")
        m4.side_effect = mock_Exception()

        class mock_engine_Exception(Exception): pass
        mock_engine = mocker.MagicMock()
        mock_engine.search.side_effect = mock_engine_Exception()
        mock_params = {}
        import lib.search.search_helper as sh
        try:
            res = sh._try_engine(mock_engine, mock_params)
        except mock_engine_Exception:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

        m2.assert_called()
        m3.assert_called()
        m4.assert_not_called()

    def test3(self, mocker, tmp_path):
        m1 = mocker.patch("lib.util.network_connected")
        m1.return_value = True

        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        m2 = mocker.patch.object(NMH, "start")

        m3 = mocker.patch.object(NMH, "stop")
        m3.return_value = False

        #prevent the infinite loop from running
        class mock_Exception(Exception): pass
        m4 = mocker.patch("time.sleep")
        m4.side_effect = mock_Exception()

        class mock_engine_Exception(Exception): pass
        mock_engine = mocker.MagicMock()
        mock_engine.search.side_effect = mock_engine_Exception()
        mock_params = {}

        import lib.search.search_helper as sh
        try:
            res = sh._try_engine(mock_engine, mock_params)
        except mock_Exception:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

        m2.assert_called()
        m3.assert_called()
        m4.assert_called()

        assert m3.call_count == 1

    def test4(self, mocker, tmp_path):
        m1 = mocker.patch("lib.util.network_connected")
        m1.return_value = True

        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        m2 = mocker.patch.object(NMH, "start")

        m3 = mocker.patch.object(NMH, "stop")
        m3.return_value = False

        #prevent the infinite loop from running
        class mock_Exception(Exception): pass
        m4 = mocker.patch("time.sleep")
        m4.side_effect = mock_Exception()

        mock_engine = mocker.MagicMock()
        mock_engine.search.return_value = ["some result"]
        mock_params = {}

        import lib.search.search_helper as sh
        try:
            res = sh._try_engine(mock_engine, mock_params)
        except mock_Exception:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

        m2.assert_called()
        m3.assert_called()
        m4.assert_called()
        assert m3.call_count == 1

    def test5(self, mocker, tmp_path):
        m1 = mocker.patch("lib.util.network_connected")
        m1.return_value = True

        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        m2 = mocker.patch.object(NMH, "start")

        m3 = mocker.patch.object(NMH, "stop")
        m3.return_value = True

        #prevent the infinite loop from running
        class mock_Exception(Exception): pass
        m4 = mocker.patch("time.sleep")
        m4.side_effect = mock_Exception()

        mock_engine = mocker.MagicMock()
        mock_engine.search.return_value = ["some result"]
        mock_params = {}

        import lib.search.search_helper as sh
        res = sh._try_engine(mock_engine, mock_params)

        m2.assert_called()
        m3.assert_called()
        m4.assert_not_called()
        assert m3.call_count == 1
        assert len(res) == 1
        assert res[0] == "some result"