import pytest

class Test_init:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        m1 = mocker.patch("lib.util.is_valid_path")
        m1.return_value = True

        from lib.scraping._scraping_tracker import _scraping_tracker as ST
        ST.__init__(_self, "some path")

        _self._setup.assert_called()

    def test2(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        m1 = mocker.patch("lib.util.is_valid_path")
        m1.return_value = False

        from lib.scraping._scraping_tracker import _scraping_tracker as ST
        import lib.exceptions as exp
        try:
            ST.__init__(_self, "some path")
        except exp.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

        _self._setup.assert_not_called()

class Test_setup:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        from pathlib import Path
        m1 = mocker.patch.object(Path, "exists")
        m1.return_value = False
        mocker.patch.object(Path, "touch")

        m2 = mocker.patch("tarfile.open")

        from lib.scraping._scraping_tracker import _scraping_tracker as ST
        ST._setup(_self, "some path", "some name")

        m2.assert_called()

    def test2(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        from pathlib import Path
        m1 = mocker.patch.object(Path, "exists")
        m1.return_value = True

        m2 = mocker.patch("tarfile.open")

        from lib.scraping._scraping_tracker import _scraping_tracker as ST
        ST._setup(_self, "some path", "some name")

        m2.assert_not_called()
        _self._load.assert_called()

class Test_load:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        from lib.scraping._scraping_tracker import _scraping_tracker as ST
        ST._load(_self, "some path")

        _self._get_logs.assert_called()

class Test_get_logs:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        from pathlib import Path
        m1 = mocker.patch.object(Path, "exists")
        m1.return_value = False

        from lib.scraping._scraping_tracker import _scraping_tracker as ST
        res = ST._get_logs(_self, "some path")

        assert len(res) == 0

    def test2(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        from pathlib import Path
        m1 = mocker.patch.object(Path, "exists")
        m1.return_value = True

        m2 = mocker.patch("tarfile.open")
        import tarfile
        m2.side_effect = tarfile.ReadError()

        from lib.scraping._scraping_tracker import _scraping_tracker as ST
        res = ST._get_logs(_self, "some path")

        assert len(res) == 0

    def test3(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        from pathlib import Path
        m1 = mocker.patch.object(Path, "exists")
        m1.return_value = True

        m2 = mocker.patch("tarfile.open")

        m3 = mocker.patch.object(Path, "iterdir")

        from lib.scraping._scraping_tracker import _scraping_tracker as ST
        res = ST._get_logs(_self, "some path")

        m3.assert_called()

class Test_page:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        type(_self)._current_page = "some test value"

        from lib.scraping._scraping_tracker import _scraping_tracker as ST
        res = ST.page(_self, None)

        assert res == "some test value"

    def test2(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        type(_self)._current_page = "some test value"

        m1 = mocker.patch("lib.util.is_int")
        m1.return_value = True

        from lib.scraping._scraping_tracker import _scraping_tracker as ST
        res = ST.page(_self, 42)

        assert res == 42

    def test3(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        type(_self)._current_page = "some test value"

        m1 = mocker.patch("lib.util.is_int")
        m1.return_value = False

        from lib.scraping._scraping_tracker import _scraping_tracker as ST
        import lib.exceptions as exp
        try:
            res = ST.page(_self, "some other test value")
        except exp.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

class Test_url:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        type(_self)._current_URL = "some test value"

        from lib.scraping._scraping_tracker import _scraping_tracker as ST
        res = ST.url(_self, None)

        assert res == "some test value"
    
    def test2(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        type(_self)._current_page = "some test value"

        m1 = mocker.patch("lib.util.is_URL")
        m1.return_value = True

        from lib.scraping._scraping_tracker import _scraping_tracker as ST
        res = ST.url(_self, 42)

        assert res == "42"

    def test3(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        type(_self)._current_page = "some test value"

        m1 = mocker.patch("lib.util.is_URL")
        m1.return_value = False

        from lib.scraping._scraping_tracker import _scraping_tracker as ST
        import lib.exceptions as exp
        try:
            res = ST.page(_self, "some other test value")
        except exp.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

class Test_begin_and_end:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        from lib.scraping._scraping_tracker import _scraping_tracker as ST
        for call in [ST.page_begin, ST.page_end, ST.url_begin, ST.url_end]:
            call(_self)
            _self._append.assert_called()

'''
Note
here we finally use the `spec` argument to make a mocked object appear as
an instance of another class; specially `date`
    see:
    https://stackoverflow.com/questions/11146725/isinstance-and-mocking/26567750
    https://docs.python.org/3/library/unittest.mock-examples.html#creating-a-mock-from-an-existing-object
'''
class Test_json_serial:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        from datetime import date, datetime
        mock_obj = mocker.MagicMock(spec=date)

        from lib.scraping._scraping_tracker import _scraping_tracker as ST
        res = ST._json_serial(_self, mock_obj )

        mock_obj.isoformat.assert_called()

    def test2(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        from datetime import date, datetime
        mock_obj = mocker.MagicMock(spec=datetime)

        from lib.scraping._scraping_tracker import _scraping_tracker as ST
        res = ST._json_serial(_self, mock_obj )

        mock_obj.isoformat.assert_called()

    def test3(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        mock_obj = mocker.MagicMock()

        from lib.scraping._scraping_tracker import _scraping_tracker as ST
        try:
            res = ST._json_serial(_self, mock_obj )
        except TypeError:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

class Test_append:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        mock_message = {}
        mock_resume_file = mocker.MagicMock()

        m1 = mocker.patch("tarfile.open")

        m2 = mocker.patch("tempfile.TemporaryDirectory")

        from pathlib import Path
        m3 = mocker.patch.object(Path, "touch")

        m4 = mocker.patch("json.dumps")
        
        from pathlib import Path
        m5 = mocker.patch.object(Path, "write_text")

        from lib.scraping._scraping_tracker import _scraping_tracker as ST
        res = ST._append(_self, mock_message, mock_resume_file )

        m1.assert_called()

class Test_get_URLs:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        mock_resume_file = mocker.MagicMock()

        from lib.scraping._scraping_tracker import _scraping_tracker as ST
        res = ST._get_URLs(_self, mock_resume_file )

        _self._get_logs.assert_called()