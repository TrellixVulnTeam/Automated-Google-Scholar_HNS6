import pytest

class Test_start:
    def test1(self, mocker, tmp_path):
        mock_urls = []
        mock_output_dir = ""
        import lib.zoteroing.Zoteroing_Helper as ZH
        res = ZH.start(mock_urls, mock_output_dir)

        len(res) == 0

    def test2(self, mocker, tmp_path):
        mock_urls = ["some URL"]
        mock_output_dir = ""

        m1 = mocker.patch("lib.zoteroing.Zoteroing_Helper._get_batches")
        m1.return_value = ["mock batch"]

        m2 = mocker.patch("lib.zoteroing.Zoteroing_Helper._Zoteroing_Helper")

        m3 = mocker.patch("lib.zoteroing.Zoteroing_Helper._try_Zoteroing")

        import lib.zoteroing.Zoteroing_Helper as ZH
        res = ZH.start(mock_urls, mock_output_dir)

        m1.assert_called()
        m2.assert_called()
        m3.assert_called()

class Test_get_batches:
    def test1(self, mocker, tmp_path):
        mock_urls = []
        
        import lib.zoteroing.Zoteroing_Helper as ZH
        res = ZH._get_batches(mock_urls)

        len(res) == 0

    def test2(self, mocker, tmp_path):
        mock_urls = []

        m1 = mocker.patch("lib.zoteroing.Zoteroing_Helper._grouper")
        m1.return_value = ["mock batch"]
        
        import lib.zoteroing.Zoteroing_Helper as ZH
        res = ZH._get_batches(mock_urls)

        m1.assert_called()

    def test3(self, mocker, tmp_path):
        mock_urls = ["url1", "url2"]
        
        import lib.zoteroing.Zoteroing_Helper as ZH
        res = ZH._get_batches(mock_urls, batch_size=2)

        assert len(res) == 1
        assert len(res[0]) == 2
    
    def test4(self, mocker, tmp_path):
        mock_urls = ["url1", "url2", "url3"]
        
        import lib.zoteroing.Zoteroing_Helper as ZH
        res = ZH._get_batches(mock_urls, batch_size=2)

        assert len(res) == 2
        assert len(res[0]) == 2
        assert len(res[1]) == 1

    def test5(self, mocker, tmp_path):
        mock_urls = ["url1", "url2", "url3"]
        
        import lib.zoteroing.Zoteroing_Helper as ZH
        res = ZH._get_batches(mock_urls, batch_size=2)

        set_mock_urls = set(mock_urls)
        for batch in res:
            for url in batch:
                assert not url is None
                assert url in set_mock_urls

class Test_try_Zoteroing:
    def test1(self, mocker, tmp_path):
        mocker_zoteroing_obj = mocker.MagicMock()
        
        m1 = mocker.patch("lib.util.network_connected")
        m1.return_value = False

        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        m2 = mocker.patch.object(NMH, "start")
        m3 = mocker.patch.object(NMH, "stop")
        
        class mock_exception(Exception): pass
        m_last = mocker.patch("time.sleep")
        m_last.side_effect = mock_exception()

        import lib.zoteroing.Zoteroing_Helper as ZH
        try:
            res = ZH._try_Zoteroing(mocker_zoteroing_obj)
        except mock_exception:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")
        
        m1.assert_called()
        m2.assert_not_called()
        mocker_zoteroing_obj.start.assert_not_called()
        m3.assert_not_called()

    def test2(self, mocker, tmp_path):
        class mock_zoteroing_exception(Exception): pass
        mocker_zoteroing_obj = mocker.MagicMock()
        mocker_zoteroing_obj.start.side_effect = mock_zoteroing_exception()
        
        m1 = mocker.patch("lib.util.network_connected")
        m1.return_value = True

        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        m2 = mocker.patch.object(NMH, "start")
        m3 = mocker.patch.object(NMH, "stop")
        m3.return_value = True
        
        class mock_exception(Exception): pass
        m_last = mocker.patch("time.sleep")
        m_last.side_effect = mock_exception()

        import lib.zoteroing.Zoteroing_Helper as ZH
        try:
            res = ZH._try_Zoteroing(mocker_zoteroing_obj)
        except mock_zoteroing_exception:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")
        
        m1.assert_called()
        m2.assert_called()
        mocker_zoteroing_obj.start.assert_called()
        m3.assert_called()
        m3.calls == 1

    def test3(self, mocker, tmp_path):
        class mock_zoteroing_exception(Exception): pass
        mocker_zoteroing_obj = mocker.MagicMock()
        mocker_zoteroing_obj.start.side_effect = mock_zoteroing_exception()
        
        m1 = mocker.patch("lib.util.network_connected")
        m1.return_value = True

        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        m2 = mocker.patch.object(NMH, "start")
        m3 = mocker.patch.object(NMH, "stop")
        m3.return_value = False
        
        class mock_exception(Exception): pass
        m_last = mocker.patch("time.sleep")
        m_last.side_effect = mock_exception()

        import lib.zoteroing.Zoteroing_Helper as ZH
        try:
            res = ZH._try_Zoteroing(mocker_zoteroing_obj)
        except mock_exception:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")
        
        m1.assert_called()
        m2.assert_called()
        mocker_zoteroing_obj.start.assert_called()
        m3.assert_called()
        m3.calls == 1

    def test4(self, mocker, tmp_path):
        #class mock_zoteroing_exception(Exception): pass
        mocker_zoteroing_obj = mocker.MagicMock()
        #mocker_zoteroing_obj.start.side_effect = mock_zoteroing_exception()
        mocker_zoteroing_obj.start.return_value = "some return value"
        
        m1 = mocker.patch("lib.util.network_connected")
        m1.return_value = True

        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        m2 = mocker.patch.object(NMH, "start")
        m3 = mocker.patch.object(NMH, "stop")
        m3.return_value = False
        
        class mock_exception(Exception): pass
        m_last = mocker.patch("time.sleep")
        m_last.side_effect = mock_exception()

        import lib.zoteroing.Zoteroing_Helper as ZH
        try:
            res = ZH._try_Zoteroing(mocker_zoteroing_obj)
        except mock_exception:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")
        
        m1.assert_called()
        m2.assert_called()
        mocker_zoteroing_obj.start.assert_called()
        m3.assert_called()
        m3.calls == 1

    def test4(self, mocker, tmp_path):
        #class mock_zoteroing_exception(Exception): pass
        mocker_zoteroing_obj = mocker.MagicMock()
        #mocker_zoteroing_obj.start.side_effect = mock_zoteroing_exception()
        mocker_zoteroing_obj.start.return_value = "some return value"
        
        m1 = mocker.patch("lib.util.network_connected")
        m1.return_value = True

        from lib.Network_Monitor_Helper import Network_Monitor_Helper as NMH
        m2 = mocker.patch.object(NMH, "start")
        m3 = mocker.patch.object(NMH, "stop")
        m3.return_value = True
        
        class mock_exception(Exception): pass
        m_last = mocker.patch("time.sleep")
        m_last.side_effect = mock_exception()

        import lib.zoteroing.Zoteroing_Helper as ZH
        res = ZH._try_Zoteroing(mocker_zoteroing_obj)
        
        m1.assert_called()
        m2.assert_called()
        mocker_zoteroing_obj.start.assert_called()
        m3.assert_called()
        m3.calls == 1
        assert res == "some return value"

class Test_Zoteroing_Helper:
    class Test_init:
        def test1(self, mocker, tmp_path):
            test_self = mocker.MagicMock()
            
            #urls, code_dir, output_dir
            test_urls = "http://www.google.com"
            test_output_dir = tmp_path
            test_num_tasks = 1

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            import lib.exceptions as exp
            try:
                ZH.__init__(test_self, test_urls, test_output_dir, test_num_tasks)
            except exp.Bad_argument:
                assert True
            except Exception as err:
                pytest.fail(f"Saw unexpected exception: {err}")
            else:
                pytest.fail(f"Did not throw exception as expected.")

        def test2(self, mocker, tmp_path):
            test_self = mocker.MagicMock()
            
            #urls, code_dir, output_dir
            #test_urls = ["http://www.google.com"]
            test_urls = ["some bad URL"]
            test_output_dir = tmp_path
            test_num_tasks = 1

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            import lib.exceptions as exp
            try:
                ZH.__init__(test_self, test_urls, test_output_dir, test_num_tasks)
            except exp.Bad_argument:
                assert True
            except Exception as err:
                pytest.fail(f"Saw unexpected exception: {err}")
            else:
                pytest.fail(f"Did not throw exception as expected.")

        def test3(self, mocker, tmp_path):
            test_self = mocker.MagicMock()
            
            #urls, code_dir, output_dir
            #test_urls = ["http://www.google.com"]
            test_urls = []
            test_output_dir = tmp_path
            test_num_tasks = 1

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            import lib.exceptions as exp
            try:
                ZH.__init__(test_self, test_urls, test_output_dir, test_num_tasks)
            except exp.Bad_argument:
                assert True
            except Exception as err:
                pytest.fail(f"Saw unexpected exception: {err}")
            else:
                pytest.fail(f"Did not throw exception as expected.")

        def test4(self, mocker, tmp_path):
            test_self = mocker.MagicMock()
            
            #urls, code_dir, output_dir
            test_urls = ["http://www.google.com"]
            test_output_dir = tmp_path
            test_num_tasks = "some bad argument"

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            import lib.exceptions as exp
            try:
                ZH.__init__(test_self, test_urls, test_output_dir, test_num_tasks)
            except exp.Bad_argument:
                assert True
            except Exception as err:
                pytest.fail(f"Saw unexpected exception: {err}")
            else:
                pytest.fail(f"Did not throw exception as expected.")

        def test5(self, mocker, tmp_path):
            test_self = mocker.MagicMock()
            
            #urls, code_dir, output_dir
            test_urls = ["http://www.google.com"]
            test_output_dir = tmp_path
            test_num_tasks = 0

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            import lib.exceptions as exp
            try:
                ZH.__init__(test_self, test_urls, test_output_dir, test_num_tasks)
            except exp.Bad_argument:
                assert True
            except Exception as err:
                pytest.fail(f"Saw unexpected exception: {err}")
            else:
                pytest.fail(f"Did not throw exception as expected.")

        def test6(self, mocker, tmp_path):
            test_self = mocker.MagicMock()
            
            #urls, code_dir, output_dir
            test_urls = ["http://www.google.com"]
            test_output_dir = tmp_path
            test_num_tasks = 1

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            import lib.exceptions as exp
            ZH.__init__(test_self, test_urls, test_output_dir, test_num_tasks)

            assert test_self._max_tasks == 1

        def test6(self, mocker, tmp_path):
            test_self = mocker.MagicMock()
            
            #urls, code_dir, output_dir
            test_urls = ["http://www.google.com"]
            test_output_dir = tmp_path
            test_num_tasks = None

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            import lib.exceptions as exp
            ZH.__init__(test_self, test_urls, test_output_dir, test_num_tasks)

            assert test_self._max_tasks == 1

        def test7(self, mocker, tmp_path):
            test_self = mocker.MagicMock()
            
            #urls, code_dir, output_dir
            test_urls = 10*["http://www.google.com"] #make a length 10 list
            test_output_dir = tmp_path
            test_num_tasks = None

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            import lib.exceptions as exp
            ZH.__init__(test_self, test_urls, test_output_dir, test_num_tasks)

            import lib.zoteroing.Zoteroing_Helper
            assert test_self._max_tasks == lib.zoteroing.Zoteroing_Helper._MAX_TASKS

        def test8(self, mocker, tmp_path):
            test_self = mocker.MagicMock()
            
            #urls, code_dir, output_dir
            test_urls = ["http://www.google.com"]
            test_output_dir = "some bad dir"
            test_num_tasks = 1

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            import lib.exceptions as exp
            try:
                ZH.__init__(test_self, test_urls, test_output_dir, test_num_tasks)
            except exp.Bad_argument:
                assert True
            except Exception as err:
                pytest.fail(f"Saw unexpected exception: {err}")
            else:
                pytest.fail(f"Did not throw exception as expected.")

        def test9(self, mocker, tmp_path):
            test_self = mocker.MagicMock()
                
            m1 = mocker.patch("lib.zoteroing._zoteroing_output_helper._zoteroing_output_helper")

            test_urls = ["http://www.google.com"] #make a length 10 list
            test_output_dir = tmp_path
            test_num_tasks = 1

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            import lib.exceptions as exp
            ZH.__init__(test_self, test_urls, test_output_dir, test_num_tasks)

            m1.assert_called()

    class Test_startup_Zoteroing_service:
        def test1(self, mocker, tmp_path):
            test_self = mocker.MagicMock()

            mocker.patch("lib.docker.service_helper._Service_Helper")
            from pathlib import Path
            mocker.patch.object(Path, "resolve")

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            ZH._startup_Zoteroing_service(test_self, "test_image_name", tmp_path, tmp_path, 1)

    class Test_start:
        def test1(self, mocker, tmp_path):
            mock_self = mocker.MagicMock()
            mock_self._all_done.return_value = True

            mock_service = mocker.MagicMock()

            mock_time = mocker.patch("time.sleep")

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            ZH._start(mock_self, mock_service, tmp_path)

            mock_service.stop.assert_called()
        
        def test2(self, mocker, tmp_path):
            '''
            Here we do something special, because we're testing a main loop
            we do not break out of the main loop in the normal way
            but rather have the time.sleep() call throw an exception
            which halts execution
            we then catch / look for the exeception that halts the loop
            which implies that the normal main loop breakout code was not called
            '''
            mock_self = mocker.MagicMock()
            mock_self._all_done.return_value = False

            mock_service = mocker.MagicMock()

            class Mock_Exception(Exception): pass
            mock_time = mocker.patch("time.sleep")
            mock_time.side_effect = Mock_Exception()

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            try:
                ZH._start(mock_self, mock_service, tmp_path)
            except Mock_Exception:
                assert True
            except Exception as err:
                pytest.fail(f"Saw unexpected exception: {err}")
            else:
                pytest.fail(f"Did not throw exception as expected.")

    class Test_assign_URLs_to_tasks:
        def test1(self, mocker):
            mock_self = mocker.MagicMock()
            mock_self._get_ready_containers.return_value = []
            mock_self._urls = []
            mock_self._URL_to_container = {}

            mock_service = mocker.MagicMock()

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            ZH._assign_URLs_to_tasks(mock_self, mock_service)

            assert len(mock_self._URL_to_container) == 0

        def test2(self, mocker):
            mock_self = mocker.MagicMock()
            mock_container = mocker.MagicMock()
            mock_self._get_ready_containers.return_value = [mock_container]
            mock_self._urls = []
            mock_self._URL_to_container = {}

            mock_service = mocker.MagicMock()

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            ZH._assign_URLs_to_tasks(mock_self, mock_service)

            assert len(mock_self._URL_to_container) == 0

        def test3(self, mocker):
            mock_self = mocker.MagicMock()
            mock_container = mocker.MagicMock()
            mock_self._get_ready_containers.return_value = []
            mock_self._urls = ["test"]
            mock_self._URL_to_container = {}

            mock_service = mocker.MagicMock()

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            ZH._assign_URLs_to_tasks(mock_self, mock_service)

            assert len(mock_self._URL_to_container) == 0

        def test4(self, mocker):
            mock_self = mocker.MagicMock()
            mock_container = mocker.MagicMock()
            mock_self._get_ready_containers.return_value = [mock_container]
            mock_self._urls = ["test"]
            mock_self._URL_to_container = {}

            mock_service = mocker.MagicMock()

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            ZH._assign_URLs_to_tasks(mock_self, mock_service)

            assert len(mock_self._URL_to_container) == 1

        def test5(self, mocker):
            mock_self = mocker.MagicMock()
            mock_container = mocker.MagicMock()
            mock_self._get_ready_containers.return_value = [mock_container, mock_container]
            mock_self._urls = ["test"]
            mock_self._URL_to_container = {}

            mock_service = mocker.MagicMock()

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            ZH._assign_URLs_to_tasks(mock_self, mock_service)

            assert len(mock_self._URL_to_container) == 1

        def test6(self, mocker):
            mock_self = mocker.MagicMock()
            mock_container = mocker.MagicMock()
            mock_self._get_ready_containers.return_value = [mock_container]
            mock_self._urls = ["test1", "Test2"]
            mock_self._URL_to_container = {}

            mock_service = mocker.MagicMock()

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            ZH._assign_URLs_to_tasks(mock_self, mock_service)

            assert len(mock_self._URL_to_container) == 1

    class Test_get_ready_containers:
        def test1(self, mocker):
            mock_self = mocker.MagicMock()
            mock_self._get_idle_containers.return_value = []
            mock_self._URL_to_container = {}

            mock_service = mocker.MagicMock()

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._get_ready_containers(mock_self, mock_service)

            assert len(_ret) == 0

        def test2(self, mocker):
            mock_self = mocker.MagicMock()
            mock_container = mocker.MagicMock()
            mock_container.id.return_value = 1
            mock_self._get_idle_containers.return_value = [mock_container]
            mock_self._URL_to_container = {}

            mock_service = mocker.MagicMock()

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._get_ready_containers(mock_self, mock_service)

            assert len(_ret) == 1
            assert _ret[0].id() == 1

        def test3(self, mocker):
            mock_self = mocker.MagicMock()
            mock_container = mocker.MagicMock()
            mock_container.id.return_value = 1
            mock_self._get_idle_containers.return_value = [mock_container]
            mock_self._URL_to_container = {"test": mock_container}

            mock_service = mocker.MagicMock()

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._get_ready_containers(mock_self, mock_service)

            assert len(_ret) == 0

        def test4(self, mocker):
            mock_self = mocker.MagicMock()
            mock_container1 = mocker.MagicMock()
            mock_container1.id.return_value = 1
            mock_container2 = mocker.MagicMock()
            mock_container2.id.return_value = 2
            mock_self._get_idle_containers.return_value = [mock_container1, mock_container2]
            mock_self._URL_to_container = {"test": mock_container1}

            mock_service = mocker.MagicMock()

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._get_ready_containers(mock_self, mock_service)

            assert len(_ret) == 1
            assert _ret[0].id() == 2

        def test5(self, mocker):
            mock_self = mocker.MagicMock()
            mock_container1 = mocker.MagicMock()
            mock_container1.id.return_value = 1
            mock_container2 = mocker.MagicMock()
            mock_container2.id.return_value = 2
            mock_self._get_idle_containers.return_value = [mock_container2]
            mock_self._URL_to_container = {"test": mock_container1}

            mock_service = mocker.MagicMock()

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._get_ready_containers(mock_self, mock_service)

            assert len(_ret) == 1
            assert _ret[0].id() == 2

    class Test_prune_finished_tasks:
        def test1(self, mocker, tmp_path):
            mock_self = mocker.MagicMock()
            mock_self._output_helper.get_finished_URLs.return_value = []

            mock_self._URL_to_container = {}

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._prune_finished_tasks(mock_self, tmp_path)

            mock_self._is_URL_done.assert_not_called()

        def test2(self, mocker, tmp_path):
            mock_self = mocker.MagicMock()
            mock_self._output_helper.get_finished_URLs.return_value = ["Test1"]

            mock_container = mocker.MagicMock()
            mock_self._URL_to_container = {"Test1":mock_container}

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._prune_finished_tasks(mock_self, tmp_path)

            mock_self._is_URL_done.assert_called()

    class Test_is_URL_done:
        def test1(self, mocker, tmp_path):
            mock_self = mocker.MagicMock()
            mock_self._URL_to_container = {}
            mock_self._is_container_idle.return_value = False
            mock_self._output_helper.is_URL_done.return_value = False

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._is_URL_done(mock_self, "test")

            assert not _ret

        def test2(self, mocker, tmp_path):
            mock_self = mocker.MagicMock()
            mock_self._URL_to_container = {"test":None}
            mock_self._is_container_idle.return_value = False
            mock_self._output_helper.is_URL_done.return_value = False

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._is_URL_done(mock_self, "test")

            assert not _ret

        def test3(self, mocker, tmp_path):
            mock_self = mocker.MagicMock()
            mock_self._URL_to_container = {"test":None}
            mock_self._is_container_idle.return_value = True
            mock_self._output_helper.is_URL_done.return_value = False

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._is_URL_done(mock_self, "test")

            assert not _ret

        def test4(self, mocker, tmp_path):
            mock_self = mocker.MagicMock()
            mock_self._URL_to_container = {"test":None}
            mock_self._is_container_idle.return_value = True
            mock_self._output_helper.is_URL_done.return_value = True

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._is_URL_done(mock_self, "test")

            assert _ret

    class Test_all_done:
        def test1(self, mocker):
            mock_self = mocker.MagicMock()
            mock_self._are_all_URLs_Zoteroed.return_value = False
            mock_self._are_all_containers_finished.return_value = False
            
            mock_service = mocker.MagicMock()

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._all_done(mock_self, mock_service)

            assert not _ret

        def test2(self, mocker):
            mock_self = mocker.MagicMock()
            mock_self._are_all_URLs_Zoteroed.return_value = False
            mock_self._are_all_containers_finished.return_value = True
            
            mock_service = mocker.MagicMock()

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._all_done(mock_self, mock_service)

            assert not _ret

        def test3(self, mocker):
            mock_self = mocker.MagicMock()
            mock_self._are_all_URLs_Zoteroed.return_value = True
            mock_self._are_all_containers_finished.return_value = False
            
            mock_service = mocker.MagicMock()

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._all_done(mock_self, mock_service)

            assert not _ret

        def test4(self, mocker):
            mock_self = mocker.MagicMock()
            mock_self._are_all_URLs_Zoteroed.return_value = True
            mock_self._are_all_containers_finished.return_value = True
            
            mock_service = mocker.MagicMock()

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._all_done(mock_self, mock_service)

            assert _ret

    class Test_are_all_URLs_Zoteroed:
        def test1(self, mocker):
            mock_self = mocker.MagicMock()
            mock_urls = []
            mock_URL_to_container = {}

            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._are_all_URLs_Zoteroed(mock_self, mock_urls, mock_URL_to_container)

            assert _ret

        def test2(self, mocker):
            mock_self = mocker.MagicMock()
            mock_urls = ["test"]
            mock_URL_to_container = {}
            
            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._are_all_URLs_Zoteroed(mock_self, mock_urls, mock_URL_to_container)
            
            assert not _ret

        def test3(self, mocker):
            mock_self = mocker.MagicMock()
            mock_urls = []
            mock_URL_to_container = {"test":None}
            
            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._are_all_URLs_Zoteroed(mock_self, mock_urls, mock_URL_to_container)
            
            assert not _ret

        def test4(self, mocker):
            mock_self = mocker.MagicMock()
            mock_urls = ["test"]
            mock_URL_to_container = {"test":None}
            
            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._are_all_URLs_Zoteroed(mock_self, mock_urls, mock_URL_to_container)
            
            assert not _ret

    class Test_are_all_containers_finished:
        def test1(self, mocker):
            mock_self = mocker.MagicMock()
            mock_self._get_idle_containers.return_value = []

            mock_service = mocker.MagicMock()
            mock_service.containers.return_value = ["test"]
            
            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._are_all_containers_finished(mock_self, mock_service)
            
            assert not _ret

        def test2(self, mocker):
            mock_self = mocker.MagicMock()
            mock_self._get_idle_containers.return_value = ["test"]

            mock_service = mocker.MagicMock()
            mock_service.containers.return_value = ["test"]
            
            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._are_all_containers_finished(mock_self, mock_service)
            
            assert _ret

        def test3(self, mocker):
            mock_self = mocker.MagicMock()
            mock_self._get_idle_containers.return_value = ["test"]

            mock_service = mocker.MagicMock()
            mock_service.containers.return_value = ["test1", "test2"]
            
            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._are_all_containers_finished(mock_self, mock_service)
            
            assert not _ret

    class Test_get_idle_containers:
        def test1(self, mocker):
            mock_self = mocker.MagicMock()
            mock_self._is_container_idle.return_value = False

            mock_service = mocker.MagicMock()
            mock_service.containers.return_value = ["test"]
            
            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._get_idle_containers(mock_self, mock_service)
            
            assert len(_ret) == 0

        def test2(self, mocker):
            mock_self = mocker.MagicMock()
            mock_self._is_container_idle.return_value = True

            mock_service = mocker.MagicMock()
            mock_service.containers.return_value = ["test"]
            
            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._get_idle_containers(mock_self, mock_service)
            
            assert len(_ret) == 1
            assert _ret[0] == "test"

    class Test_is_container_idle:
        def test1(self, mocker):
            mock_self = mocker.MagicMock()
            
            mock_container = mocker.MagicMock()
            mock_return = mocker.MagicMock()
            mock_return.output.decode.return_value = "IDLE"
            mock_container.exec.return_value = mock_return
            
            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._is_container_idle(mock_self, mock_container)
            
            assert _ret

        def test2(self, mocker):
            mock_self = mocker.MagicMock()
            
            mock_container = mocker.MagicMock()
            mock_return = mocker.MagicMock()
            mock_return.output.decode.return_value = "NOT IDLE"
            mock_container.exec.return_value = mock_return
            
            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            _ret = ZH._is_container_idle(mock_self, mock_container)
            
            assert not _ret

    class Test_compile_reports_of_finished_URLs:
        def test1(self, mocker, tmp_path):
            _self = mocker.MagicMock()
            _self._output_helper.paths_and_content.return_value = {}
            
            mock_output_dir = tmp_path
            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            res = ZH._compile_reports_of_finished_URLs(_self, mock_output_dir)

            assert len(res) == 0

        def test2(self, mocker, tmp_path):
            _self = mocker.MagicMock()
            mock_return1 = {
                "URL" : "some URL",
                "error" : "some error report",
                "error msg": "an error message",
            }

            mock_return2  = {
                str(tmp_path) : mock_return1
            }
            _self._output_helper.paths_and_content.return_value = mock_return2
            
            mock_output_dir = tmp_path
            from lib.zoteroing.Zoteroing_Helper import _Zoteroing_Helper as ZH
            res = ZH._compile_reports_of_finished_URLs(_self, mock_output_dir)

            assert len(res) == 1
            set_values_mock_return = set( list( mock_return1.values() ) )
            set_values_res = []
            for report in res:
                for v in report.values():
                    set_values_res.append(v)
            set_values_res = set(set_values_res)

            assert set_values_mock_return <= set_values_res
            for itm in set_values_res:
                if not itm in set_values_mock_return:
                    assert "My Library" in itm