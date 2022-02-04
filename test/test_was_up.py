import pytest

'''
NOTE
Here we mock a context manager
so we have emulate the context manager protocol
Thus we mock __enter__() and __exit__() (if needed) on an object returned from
main call seen in the context manager
    see:
    https://stackoverflow.com/questions/28850070/python-mocking-a-context-manager
    https://docs.python.org/3/library/stdtypes.html#typecontextmanager
    https://docs.python.org/3/reference/datamodel.html#context-managers
'''
class Test_get_heartbeats:
    def test1(self, mocker, tmp_path):
        m1 = mocker.patch("tarfile.open")
        mock_context_manager = mocker.MagicMock()
        m1.return_value = mock_context_manager

        mock_context_manager.__enter__.return_value = []

        import lib.service_share.network_monitor_worker.was_up as wu
        res = wu._get_heartbeats("test")

        assert len(res) == 0

    def test2(self, mocker, tmp_path):
        m1 = mocker.patch("tarfile.open")
        mock_context_manager = mocker.MagicMock()
        m1.return_value = mock_context_manager

        mock_tar_info = mocker.MagicMock()
        type(mock_tar_info).name = "-1639960620.2999249"

        mock_context_manager.__enter__.return_value = [mock_tar_info]

        import lib.service_share.network_monitor_worker.was_up as wu
        res = wu._get_heartbeats("test")

        assert len(res) == 1
        import datetime
        _key = datetime.datetime.fromtimestamp(float("1639960620.2999249"))
        assert res[_key] == False

    def test3(self, mocker, tmp_path):
        m1 = mocker.patch("tarfile.open")
        mock_context_manager = mocker.MagicMock()
        m1.return_value = mock_context_manager

        mock_tar_info = mocker.MagicMock()
        type(mock_tar_info).name = "+1639960620.2999249"

        mock_context_manager.__enter__.return_value = [mock_tar_info]

        import lib.service_share.network_monitor_worker.was_up as wu
        res = wu._get_heartbeats("test")

        assert len(res) == 1
        import datetime
        _key = datetime.datetime.fromtimestamp(float("1639960620.2999249"))
        assert res[_key] == True

    def test4(self, mocker, tmp_path):
        import lib.service_share.network_monitor_worker.was_up as wu
        import lib.exceptions as exp
        
        try:
            res = wu._get_heartbeats("some fake file.tar")
        except FileNotFoundError:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

class Test_get_input:
    def test1(self, mocker, tmp_path):
        m1 = mocker.patch("argparse.ArgumentParser")
        
        import lib.service_share.network_monitor_worker.was_up as wu
        res = wu._get_input()

        m1.assert_called()

class Test_get_timeline:
    def test1(self, mocker, tmp_path):
        mock_heartbeats = {}
        import lib.service_share.network_monitor_worker.was_up as wu
        res = wu._get_timeline(mock_heartbeats, 0, 1)

        assert len(res) == 2
        assert all( [(i is None) for i in res] )

    def get_mock_heartbeats(self, mocker, mock_heartbeats):
        '''
        Create a list booleans mapping to heartbeat values in mock_heartbeats
        as produced by code in was_up._get_heartbeats()
        '''
        m1 = mocker.patch("tarfile.open")
        mock_context_manager = mocker.MagicMock()
        m1.return_value = mock_context_manager

        _encoded_mock_heartbeats = []
        for (k, v) in mock_heartbeats.items():
            _name = ""
            if v == True:
                _name += "+"
            else:
                _name += "-"
            _name += str(k)

            mock_tar_info = mocker.MagicMock()
            type(mock_tar_info).name = _name
            _encoded_mock_heartbeats.append( mock_tar_info )

        mock_context_manager.__enter__.return_value = _encoded_mock_heartbeats

        import lib.service_share.network_monitor_worker.was_up as wu
        return wu._get_heartbeats("test")

    '''
    In the following tests we use mock times for the start and stop times
    to produce a timeline with several boolean values, but two None values
        where the None values are in positions as if they were sorted
        into position just like normal start and stop times
    Then to check the structure of the returned timeline
    None values are inserted into a list on the assumption that the two
    lists should be identical
        the test list, and the returned timeline
    '''
    def test1(self, mocker, tmp_path):
        mock_heartbeats = {
            1:True, 2:True, 3:False, 4:False,
            5:False, 6:True, 7:True, 8:True,
            9:False
        }

        parsed_heart_beats = self.get_mock_heartbeats(mocker, mock_heartbeats)

        import lib.service_share.network_monitor_worker.was_up as wu
        res = wu._get_timeline(parsed_heart_beats, .1, .5)

        assert res[0] == None
        assert res[1] == None
        _res = res[2:]

        _input_heartbeats = list(mock_heartbeats.values())
        for i in range(len( _input_heartbeats )):
            assert _res[i] == _input_heartbeats[i]

    def test2(self, mocker, tmp_path):
        mock_heartbeats = {
            1:True, 2:True, 3:False, 4:False,
            5:False, 6:True, 7:True, 8:True,
            9:False
        }

        parsed_heart_beats = self.get_mock_heartbeats(mocker, mock_heartbeats)

        import lib.service_share.network_monitor_worker.was_up as wu
        res = wu._get_timeline(parsed_heart_beats, 1.1, 1.5)

        _input_heartbeats = list(mock_heartbeats.values())
        assert_heartbeats = _input_heartbeats.copy()
        assert_heartbeats.insert(1, None)
        assert_heartbeats.insert(1, None)

        assert len(assert_heartbeats) == len(res)
        for i in range(len( assert_heartbeats )):
            assert res[i] == assert_heartbeats[i]

    def test3(self, mocker, tmp_path):
        mock_heartbeats = {
            1:True, 2:True, 3:False, 4:False,
            5:False, 6:True, 7:True, 8:True,
            9:False
        }

        parsed_heart_beats = self.get_mock_heartbeats(mocker, mock_heartbeats)

        import lib.service_share.network_monitor_worker.was_up as wu
        res = wu._get_timeline(parsed_heart_beats, 10, 11)

        _input_heartbeats = list(mock_heartbeats.values())
        assert_heartbeats = _input_heartbeats.copy()
        assert_heartbeats.append(None)
        assert_heartbeats.append(None)

        assert len(assert_heartbeats) == len(res)
        for i in range(len( assert_heartbeats )):
            assert res[i] == assert_heartbeats[i]

    def test4(self, mocker, tmp_path):
        mock_heartbeats = {
            1:True, 2:True, 3:False, 4:False,
            5:False, 6:True, 7:True, 8:True,
            9:False
        }

        parsed_heart_beats = self.get_mock_heartbeats(mocker, mock_heartbeats)

        import lib.service_share.network_monitor_worker.was_up as wu
        res = wu._get_timeline(parsed_heart_beats, 1.5, 2.5)

        _input_heartbeats = list(mock_heartbeats.values())
        assert_heartbeats = _input_heartbeats.copy()
        assert_heartbeats.insert(1, None)
        assert_heartbeats.insert(3, None)

        assert len(assert_heartbeats) == len(res)
        for i in range(len( assert_heartbeats )):
            assert res[i] == assert_heartbeats[i]

class Test_partition_timeline:
    def test1(self, mocker, tmp_path):
        mock_timeline = [None, None, True, True, False, False, False, True, True, True, False]

        import lib.service_share.network_monitor_worker.was_up as wu
        res = wu._partition_timeline(mock_timeline)

        assert len(res["pre_start"]) == 0
        assert len(res["between_start_and_stop"]) == 0
        _test = [True, True, False, False, False, True, True, True, False]
        assert len(res["post_stop"]) == len(_test)
        for i in range(len(_test)):
            res["post_stop"][i] == _test[i]

    def test2(self, mocker, tmp_path):
        mock_timeline = [True, True, False, False, False, True, True, True, False, None, None]

        import lib.service_share.network_monitor_worker.was_up as wu
        res = wu._partition_timeline(mock_timeline)

        assert len(res["post_stop"]) == 0
        assert len(res["between_start_and_stop"]) == 0
        _test = [True, True, False, False, False, True, True, True, False]
        
        assert len(res["pre_start"]) == len(_test)
        for i in range(len(_test)):
            res["pre_start"][i] == _test[i]

    def test3(self, mocker, tmp_path):
        mock_timeline = [True, True, False, False, None, None, False, True, True, True, False]

        import lib.service_share.network_monitor_worker.was_up as wu
        res = wu._partition_timeline(mock_timeline)

        assert len(res["between_start_and_stop"]) == 0
        
        _test1 = [True, True, False, False]
        assert len(res["pre_start"]) == len(_test1)
        for i in range(len(_test1)):
            res["pre_start"][i] == _test1[i]

        _test2 = [False, True, True, True, False]
        assert len(res["post_stop"]) == len(_test2)
        for i in range(len(_test2)):
            res["post_stop"][i] == _test2[i]

    def test4(self, mocker, tmp_path):
        mock_timeline = [True, True, False, None, False, False, None, True, True, True, False]

        import lib.service_share.network_monitor_worker.was_up as wu
        res = wu._partition_timeline(mock_timeline)
        
        _test1 = [True, True, False]
        assert len(res["pre_start"]) == len(_test1)
        for i in range(len(_test1)):
            res["pre_start"][i] == _test1[i]

        _test2 = [True, True, True, False]
        assert len(res["post_stop"]) == len(_test2)
        for i in range(len(_test2)):
            res["post_stop"][i] == _test2[i]

        _test3 = [False, False]
        assert len(res["between_start_and_stop"]) == len(_test3)
        for i in range(len(_test3)):
            res["between_start_and_stop"][i] == _test3[i]

    def test5(self, mocker, tmp_path):
        mock_timeline = [None, None]

        import lib.service_share.network_monitor_worker.was_up as wu
        res = wu._partition_timeline(mock_timeline)

        assert (len(res["pre_start"]) == len(res["post_stop"]) == len(res["between_start_and_stop"]) == 0)

'''
BUG
in these test sys.exit() is called to halt execution
but pytest ignores that for some reason?
so instead we have _return() throw an exception that pytest does not ignore
and then tests that functions are or are not called based on test conditions
in addition to the "_return" value
'''
class Test_main:
    def test1(self, mocker, tmp_path):
        m0 = mocker.patch( "argparse.ArgumentParser" )

        m1 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._get_heartbeats" )
        m1.return_value = []

        class mock_Exception(Exception): pass
        m2 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._return" )
        m2.side_effect = mock_Exception()

        m3 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._get_timeline" )
        m4 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._partition_timeline" )

        import lib.service_share.network_monitor_worker.was_up as wu
        import lib.exceptions as exp
        try:
            wu.main()
        except mock_Exception:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

        m1.assert_called()
        m3.assert_not_called()
        m4.assert_not_called()

    def test2(self, mocker, tmp_path):
        m0 = mocker.patch( "argparse.ArgumentParser" )

        m1 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._get_heartbeats" )
        m1.return_value = ["heartbeat 1", "heartbeat 2"]

        class mock_Exception(Exception): pass
        m2 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._return" )
        m2.side_effect = mock_Exception()

        m3 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._get_timeline" )
        m4 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._partition_timeline" )
        m4.return_value = {
            "between_start_and_stop": [],
            "pre_start": [],
            "post_stop": [],
            }

        import lib.service_share.network_monitor_worker.was_up as wu
        import lib.exceptions as exp
        try:
            wu.main()
        except mock_Exception:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

        m1.assert_called()
        m3.assert_called()
        m4.assert_called()
        m2.was_called_with(False)

    def test2(self, mocker, tmp_path):
        m0 = mocker.patch( "argparse.ArgumentParser" )

        m1 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._get_heartbeats" )
        m1.return_value = ["heartbeat 1", "heartbeat 2"]

        class mock_Exception(Exception): pass
        m2 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._return" )
        m2.side_effect = mock_Exception()

        m3 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._get_timeline" )
        m4 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._partition_timeline" )
        m4.return_value = {
            "between_start_and_stop": [],
            "pre_start": [],
            "post_stop": [],
            }

        import lib.service_share.network_monitor_worker.was_up as wu
        import lib.exceptions as exp
        try:
            wu.main()
        except mock_Exception:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

        m1.assert_called()
        m3.assert_called()
        m4.assert_called()
        m2.was_called_with(False)

    def test3(self, mocker, tmp_path):
        m0 = mocker.patch( "argparse.ArgumentParser" )

        m1 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._get_heartbeats" )
        m1.return_value = ["heartbeat 1", "heartbeat 2"]

        class mock_Exception(Exception): pass
        m2 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._return" )
        m2.side_effect = mock_Exception()

        m3 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._get_timeline" )
        m4 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._partition_timeline" )
        m4.return_value = {
            "between_start_and_stop": [],
            "pre_start": [True],
            "post_stop": [False],
            }

        import lib.service_share.network_monitor_worker.was_up as wu
        import lib.exceptions as exp
        try:
            wu.main()
        except mock_Exception:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

        m1.assert_called()
        m3.assert_called()
        m4.assert_called()
        m2.was_called_with(True)

    def test4(self, mocker, tmp_path):
        m0 = mocker.patch( "argparse.ArgumentParser" )

        m1 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._get_heartbeats" )
        m1.return_value = ["heartbeat 1", "heartbeat 2"]

        class mock_Exception(Exception): pass
        m2 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._return" )
        m2.side_effect = mock_Exception()

        m3 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._get_timeline" )
        m4 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._partition_timeline" )
        m4.return_value = {
            "between_start_and_stop": [],
            "pre_start": [False],
            "post_stop": [False],
            }

        import lib.service_share.network_monitor_worker.was_up as wu
        import lib.exceptions as exp
        try:
            wu.main()
        except mock_Exception:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

        m1.assert_called()
        m3.assert_called()
        m4.assert_called()
        m2.was_called_with(False)

    def test5(self, mocker, tmp_path):
        m0 = mocker.patch( "argparse.ArgumentParser" )

        m1 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._get_heartbeats" )
        m1.return_value = ["heartbeat 1", "heartbeat 2"]

        class mock_Exception(Exception): pass
        m2 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._return" )
        m2.side_effect = mock_Exception()

        m3 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._get_timeline" )
        m4 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._partition_timeline" )
        m4.return_value = {
            "between_start_and_stop": [True],
            "pre_start": [],
            "post_stop": [],
            }

        import lib.service_share.network_monitor_worker.was_up as wu
        import lib.exceptions as exp
        try:
            wu.main()
        except mock_Exception:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

        m1.assert_called()
        m3.assert_called()
        m4.assert_called()
        m2.was_called_with(True)

    def test6(self, mocker, tmp_path):
        m0 = mocker.patch( "argparse.ArgumentParser" )

        m1 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._get_heartbeats" )
        m1.return_value = ["heartbeat 1", "heartbeat 2"]

        class mock_Exception(Exception): pass
        m2 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._return" )
        m2.side_effect = mock_Exception()

        m3 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._get_timeline" )
        m4 = mocker.patch( "lib.service_share.network_monitor_worker.was_up._partition_timeline" )
        m4.return_value = {
            "between_start_and_stop": [False],
            "pre_start": [],
            "post_stop": [],
            }

        import lib.service_share.network_monitor_worker.was_up as wu
        import lib.exceptions as exp
        try:
            wu.main()
        except mock_Exception:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

        m1.assert_called()
        m3.assert_called()
        m4.assert_called()
        m2.was_called_with(False)