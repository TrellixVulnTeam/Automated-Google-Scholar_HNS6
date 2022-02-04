import pytest

'''
NOTE
In these tests we want to check if the code has gone into the block responsible
for making a new tar archive
we do this by checking if the tar.close() command has been used
as this is one of the few methods that are unique to that block
and thus can be used to signal if the block has been tested for or not

--

also, as the code is an infinite loop
we have time.sleep() throw an exception in order to avoid getting caught
in the infinite loop
'''
class Test_main:
    def test1(self, mocker, tmp_path):
        from pathlib import Path
        m1 = mocker.patch.object(Path, "exists")
        m1.return_value = False

        #prevent the infinite loop from running
        class mock_Exception(Exception): pass
        m2 = mocker.patch("time.sleep")
        m2.side_effect = mock_Exception()

        m3 = mocker.patch.object(Path, "touch")
        m4 = mocker.patch.object(Path, "mkdir")
        
        m5 = mocker.patch("tarfile.open")
        mock_context_manager = mocker.MagicMock()
        m5.return_value = mock_context_manager
        mock_context_manager.__enter__.return_value = mocker.MagicMock()

        import lib.service_share.network_monitor_worker.start_monitoring as sm
        try:
            sm.main()
        except mock_Exception:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

        mock_context_manager.close.assert_called()

    def test2(self, mocker, tmp_path):
        from pathlib import Path
        m1 = mocker.patch.object(Path, "exists")
        m1.return_value = True

        #prevent the infinite loop from running
        class mock_Exception(Exception): pass
        m2 = mocker.patch("time.sleep")
        m2.side_effect = mock_Exception()

        m3 = mocker.patch.object(Path, "touch")
        m4 = mocker.patch.object(Path, "mkdir")
        
        m5 = mocker.patch("tarfile.open")
        mock_context_manager = mocker.MagicMock()
        m5.return_value = mock_context_manager
        mock_context_manager.__enter__.return_value = mocker.MagicMock()

        import lib.service_share.network_monitor_worker.start_monitoring as sm
        try:
            sm.main()
        except mock_Exception:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

        mock_context_manager.close.assert_not_called()