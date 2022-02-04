import pytest

class Test_init:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        m1 = mocker.patch("lib.util.is_valid_path")
        m1.return_value = True

        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        ZOH.__init__(_self, "some path")

        m1.assert_called()

    def test2(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        m1 = mocker.patch("lib.util.is_valid_path")
        m1.return_value = False

        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        import lib.exceptions as exp
        try:
            ZOH.__init__(_self, "some path")
        except exp.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

class Test_has_output:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._info_json_paths_and_content.return_value = []

        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._has_output(_self, "some path")

        assert res == False

    def test2(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._info_json_paths_and_content.return_value = ["some fake output"]

        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._has_output(_self, "some path")

        assert res == True

class Test_info_json_paths_and_content:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        from pathlib import Path
        m1 = mocker.patch.object(Path, "rglob")

        mock_file = mocker.MagicMock()
        mock_file.is_file.return_value = True
        type(mock_file).name = "info.json"

        m1.return_value = [mock_file]

        m2 = mocker.patch("json.loads")

        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._info_json_paths_and_content(_self, "some path")

        m2.assert_called()
    
    def test2(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        from pathlib import Path
        m1 = mocker.patch.object(Path, "rglob")

        mock_file = mocker.MagicMock()
        mock_file.is_file.return_value = False
        type(mock_file).name = "info.json"

        m1.return_value = [mock_file]

        m2 = mocker.patch("json.loads")

        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._info_json_paths_and_content(_self, "some path")

        m2.assert_not_called()

    def test3(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        from pathlib import Path
        m1 = mocker.patch.object(Path, "rglob")

        mock_file = mocker.MagicMock()
        mock_file.is_file.return_value = True
        type(mock_file).name = "some other name"

        m1.return_value = [mock_file]

        m2 = mocker.patch("json.loads")

        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._info_json_paths_and_content(_self, "some path")

        m2.assert_not_called()

    def test3(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        from pathlib import Path
        m1 = mocker.patch.object(Path, "rglob")

        mock_file = mocker.MagicMock()
        mock_file.is_file.return_value = False
        type(mock_file).name = "some other name"

        m1.return_value = [mock_file]

        m2 = mocker.patch("json.loads")

        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._info_json_paths_and_content(_self, "some path")

        m2.assert_not_called()

class Test_is_URL_done:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._info_json_paths_and_content.return_value = {}

        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._is_URL_done(_self, "some url", "some path")

        assert res == False

    def test2(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        mock_return = mocker.MagicMock()
        _self._info_json_paths_and_content.return_value = mock_return

        mock_content = {"URL": "some other URL"}
        mock_return.values.return_value = [mock_content]

        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._is_URL_done(_self, "some url", "some path")

        assert res == False

    def test3(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        mock_return = mocker.MagicMock()
        _self._info_json_paths_and_content.return_value = mock_return

        mock_content = {"URL": "some url"}
        mock_return.values.return_value = [mock_content]

        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._is_URL_done(_self, "some url", "some path")

        assert res == True

class Test_get_finished_URLs:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._get_finished_URLs(_self, "some path")

        _self._info_json_paths_and_content.assert_called()

class Test_content:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._content(_self, "some path")

        _self._info_json_paths_and_content.assert_called()

class Test_paths:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._paths(_self, "some path")

        _self._info_json_paths_and_content.assert_called()

class Test_get_bibtex:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._get_bibtex_and_files.return_value = {}
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._get_bibtex(_self, "some path")

        _self._get_bibtex_and_files.assert_called()
        assert len(res) == 0

    def test2(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._get_bibtex_and_files.return_value = {"some URL": None}
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._get_bibtex(_self, "some path")

        _self._get_bibtex_and_files.assert_called()
        assert len(res) == 1
        assert "some URL" in res
        assert res["some URL"] is None

    
    def test3(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._get_bibtex_and_files.return_value = {"some URL": {"file": None}}
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._get_bibtex(_self, "some path")

        _self._get_bibtex_and_files.assert_called()
        assert len(res) == 1
        assert "some URL" in res
        assert res["some URL"] is None

    def test4(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._get_bibtex_and_files.return_value = {
            "some URL": {
                "file": "some file",
                "bibtex": "some bibtex",
                },
            }
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._get_bibtex(_self, "some path")

        _self._get_bibtex_and_files.assert_called()
        assert len(res) == 1
        assert "some URL" in res
        assert not res["some URL"] is None
        assert res["some URL"] == "some bibtex"

class Test_get_files:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._get_bibtex_and_files.return_value = {}
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._get_files(_self, "some path")

        _self._get_bibtex_and_files.assert_called()
        assert len(res) == 0

    def test2(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._get_bibtex_and_files.return_value = {"some URL": None}
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._get_files(_self, "some path")

        _self._get_bibtex_and_files.assert_called()
        assert len(res) == 1
        assert "some URL" in res
        assert res["some URL"] is None

    
    def test3(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._get_bibtex_and_files.return_value = {
            "some URL": {
                #"files": "some file",
                "bibtex": "some bibtex",
                },
            }
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._get_files(_self, "some path")

        _self._get_bibtex_and_files.assert_called()
        assert len(res) == 1
        assert "some URL" in res
        assert res["some URL"] is None

    def test4(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._get_bibtex_and_files.return_value = {
            "some URL": {
                "files": "some file",
                "bibtex": "some bibtex",
                },
            }
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._get_files(_self, "some path")

        _self._get_bibtex_and_files.assert_called()
        assert len(res) == 1
        assert "some URL" in res
        assert not res["some URL"] is None
        assert res["some URL"] == "some file"

'''
NOTE

Here the code was hard to test, so we had to change the structure a bit and use
helper functions instead of code blocks to make the code more testable
    see:
    https://codereview.stackexchange.com/questions/237060/mocking-pathlib-path-i-o-methods-in-a-maintainable-way-which-tests-functionality
'''
class Test_get_bibtex_and_files:
    def test1(self, mocker, tmp_path):
        #setup
        _self = mocker.MagicMock()
        _ret1 = {}
        _self._info_json_paths_and_content.return_value  = _ret1

        from pathlib import Path
        m1 = mocker.patch.object(Path, "resolve")
        
        mock_path = "some path"
        mock_content = {
            "URL" : "some URL",
        }
        #_ret1[mock_path] = mock_content

        _self._get_bibtex_from_path.return_value = None

        m2 = mocker.patch("bibtexparser.loads")
        mock_bib_database = mocker.MagicMock()
        m2.return_value = mock_bib_database
        _ret2 = []
        type(mock_bib_database).entries = _ret2

        _test_entry = "Full Text:files/2/Lai et al. - 2020 - Severe acute respiratory syndrome coronavirus 2 (S.pdf:application/pdf;ScienceDirect Snapshot:files/3/S0924857920300674.html:text/html"
        mock_entry = {
            'file': _test_entry
        }
        #_ret2.append(mock_entry)

        _self._is_bibtext_string_a_path_to_file.return_value = None
        _self._is_file_a_snapshot.return_value = True

        #main
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._get_bibtex_and_files(_self, "some path")

        #test

        _self._info_json_paths_and_content.assert_called()
        _self._get_bibtex_from_path.assert_not_called()
        m2.assert_not_called()
        _self._is_bibtext_string_a_path_to_file.assert_not_called()
        _self._is_file_a_snapshot.assert_not_called()
        assert len(res) == 0

    def test2(self, mocker, tmp_path):
        #setup
        _self = mocker.MagicMock()
        _ret1 = {}
        _self._info_json_paths_and_content.return_value  = _ret1

        from pathlib import Path
        m1 = mocker.patch.object(Path, "resolve")
        
        mock_path = "some path"
        mock_content = {
            "URL" : "some URL",
        }
        _ret1[mock_path] = mock_content

        _self._get_bibtex_from_path.return_value = None

        m2 = mocker.patch("bibtexparser.loads")
        mock_bib_database = mocker.MagicMock()
        m2.return_value = mock_bib_database
        _ret2 = []
        type(mock_bib_database).entries = _ret2

        _test_entry = "Full Text:files/2/Lai et al. - 2020 - Severe acute respiratory syndrome coronavirus 2 (S.pdf:application/pdf;ScienceDirect Snapshot:files/3/S0924857920300674.html:text/html"
        mock_entry = {
            'file': _test_entry
        }
        #_ret2.append(mock_entry)

        _self._is_bibtext_string_a_path_to_file.return_value = None
        _self._is_file_a_snapshot.return_value = True

        #main
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._get_bibtex_and_files(_self, "some path")

        #test

        _self._info_json_paths_and_content.assert_called()
        _self._get_bibtex_from_path.assert_called()
        m2.assert_not_called()
        _self._is_bibtext_string_a_path_to_file.assert_not_called()
        _self._is_file_a_snapshot.assert_not_called()
        assert 'some URL' in res
        assert res['some URL'] is None

    def test3(self, mocker, tmp_path):
        #setup
        _self = mocker.MagicMock()
        _ret1 = {}
        _self._info_json_paths_and_content.return_value  = _ret1

        from pathlib import Path
        m1 = mocker.patch.object(Path, "resolve")
        
        mock_path = "some path"
        mock_content = {
            "URL" : "some URL",
        }
        _ret1[mock_path] = mock_content

        _self._get_bibtex_from_path.return_value = "some bibtex file path"

        m2 = mocker.patch("bibtexparser.loads")
        mock_bib_database = mocker.MagicMock()
        m2.return_value = mock_bib_database
        _ret2 = []
        type(mock_bib_database).entries = _ret2

        _test_entry = "Full Text:files/2/Lai et al. - 2020 - Severe acute respiratory syndrome coronavirus 2 (S.pdf:application/pdf;ScienceDirect Snapshot:files/3/S0924857920300674.html:text/html"
        mock_entry = {
            'file': _test_entry
        }
        #_ret2.append(mock_entry)

        _self._is_bibtext_string_a_path_to_file.return_value = None
        _self._is_file_a_snapshot.return_value = True

        #main
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._get_bibtex_and_files(_self, "some path")

        #test

        _self._info_json_paths_and_content.assert_called()
        _self._get_bibtex_from_path.assert_called()
        m2.assert_called()
        _self._is_bibtext_string_a_path_to_file.assert_not_called()
        _self._is_file_a_snapshot.assert_not_called()
        assert 'some URL' in res
        assert res['some URL'] is None

    def test4(self, mocker, tmp_path):
        #setup
        _self = mocker.MagicMock()
        _ret1 = {}
        _self._info_json_paths_and_content.return_value  = _ret1

        from pathlib import Path
        m1 = mocker.patch.object(Path, "resolve")
        
        mock_path = "some path"
        mock_content = {
            "URL" : "some URL",
        }
        _ret1[mock_path] = mock_content

        _self._get_bibtex_from_path.return_value = "some bibtex file path"

        m2 = mocker.patch("bibtexparser.loads")
        mock_bib_database = mocker.MagicMock()
        m2.return_value = mock_bib_database
        _ret2 = []
        type(mock_bib_database).entries = _ret2

        _test_entry = "Full Text:files/2/Lai et al. - 2020 - Severe acute respiratory syndrome coronavirus 2 (S.pdf:application/pdf;ScienceDirect Snapshot:files/3/S0924857920300674.html:text/html"
        mock_entry = {
            'file': _test_entry
        }
        _ret2.append(mock_entry)

        _self._is_bibtext_string_a_path_to_file.return_value = None
        _self._is_file_a_snapshot.return_value = True

        #main
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._get_bibtex_and_files(_self, "some path")

        #test

        _self._info_json_paths_and_content.assert_called()
        _self._get_bibtex_from_path.assert_called()
        m2.assert_called()
        _self._is_bibtext_string_a_path_to_file.assert_called()
        _self._is_file_a_snapshot.assert_not_called()
        assert 'some URL' in res
        assert res['some URL'] is None

    def test5(self, mocker, tmp_path):
        #setup
        _self = mocker.MagicMock()
        _ret1 = {}
        _self._info_json_paths_and_content.return_value  = _ret1

        from pathlib import Path
        m1 = mocker.patch.object(Path, "resolve")
        
        mock_path = "some path"
        mock_content = {
            "URL" : "some URL",
        }
        _ret1[mock_path] = mock_content

        _self._get_bibtex_from_path.return_value = "some bibtex file path"

        m2 = mocker.patch("bibtexparser.loads")
        mock_bib_database = mocker.MagicMock()
        m2.return_value = mock_bib_database
        _ret2 = []
        type(mock_bib_database).entries = _ret2

        _test_entry = "Full Text:files/2/Lai et al. - 2020 - Severe acute respiratory syndrome coronavirus 2 (S.pdf:application/pdf;ScienceDirect Snapshot:files/3/S0924857920300674.html:text/html"
        mock_entry = {
            'file': _test_entry
        }
        _ret2.append(mock_entry)

        _self._is_bibtext_string_a_path_to_file.return_value = "some path"
        _self._is_file_a_snapshot.return_value = True

        #main
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._get_bibtex_and_files(_self, "some path")

        #test

        _self._info_json_paths_and_content.assert_called()
        _self._get_bibtex_from_path.assert_called()
        m2.assert_called()
        _self._is_bibtext_string_a_path_to_file.assert_called()
        _self._is_file_a_snapshot.assert_called()
        assert 'some URL' in res
        assert res['some URL'] is None

    def test6(self, mocker, tmp_path):
        #setup
        _self = mocker.MagicMock()
        _ret1 = {}
        _self._info_json_paths_and_content.return_value  = _ret1

        from pathlib import Path
        m1 = mocker.patch.object(Path, "resolve")
        
        mock_path = "some path"
        mock_content = {
            "URL" : "some URL",
        }
        _ret1[mock_path] = mock_content

        _self._get_bibtex_from_path.return_value = "some bibtex file path"

        m2 = mocker.patch("bibtexparser.loads")
        mock_bib_database = mocker.MagicMock()
        m2.return_value = mock_bib_database
        _ret2 = []
        type(mock_bib_database).entries = _ret2

        _test_entry = "Full Text:files/2/Lai et al. - 2020 - Severe acute respiratory syndrome coronavirus 2 (S.pdf:application/pdf;ScienceDirect Snapshot:files/3/S0924857920300674.html:text/html"
        mock_entry = {
            'file': _test_entry
        }
        _ret2.append(mock_entry)

        _self._is_bibtext_string_a_path_to_file.return_value = "some path"
        _self._is_file_a_snapshot.return_value = False

        #main
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._get_bibtex_and_files(_self, "some path")

        #test

        _self._info_json_paths_and_content.assert_called()
        _self._get_bibtex_from_path.assert_called()
        m2.assert_called()
        _self._is_bibtext_string_a_path_to_file.assert_called()
        _self._is_file_a_snapshot.assert_called()
        assert 'some URL' in res
        assert 'files' in res['some URL']
        assert len(res['some URL']['files']) > 0

class Test_is_bibtext_string_a_path_to_file:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        from pathlib import Path
        m1 = mocker.patch.object(Path, "exists")
        m1.return_value = False
        m2 = mocker.patch.object(Path, "resolve")

        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._is_bibtext_string_a_path_to_file(_self, "some root path", "some additional string")

        m2.assert_not_called()

    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        from pathlib import Path
        m1 = mocker.patch.object(Path, "exists")
        m1.return_value = True
        m2 = mocker.patch.object(Path, "resolve")

        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._is_bibtext_string_a_path_to_file(_self, "some root path", "some additional string")

        m2.assert_called()

class Test_is_file_a_snapshot:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._is_file_a_snapshot(_self, tmp_path / "some_snapshot.html")

        assert res == True

    def test2(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._is_file_a_snapshot(_self, tmp_path / "some other file.pdf")

        assert res == False

class Test_get_bibtex_from_path:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        mock_zoteroing_output = tmp_path
        #mock_my_library = mock_zoteroing_output / "My Library"
        #mock_my_library.mkdir()
        #mock_bibtex_file = mock_my_library / "My Library.bib"
        #mock_bibtex_file.touch()
        #mock_bibtex_file.write_text( "some bibtex" )
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._get_bibtex_from_path(_self, tmp_path )

        assert res is None

    def test2(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        mock_zoteroing_output = tmp_path
        mock_my_library = mock_zoteroing_output / "My Library"
        #mock_my_library.mkdir()
        #mock_bibtex_file = mock_my_library / "My Library.bib"
        #mock_bibtex_file.touch()
        #mock_bibtex_file.write_text( "some bibtex" )

        res = ZOH._get_bibtex_from_path(_self, mock_zoteroing_output )

        assert res is None
    

    def test3(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        mock_zoteroing_output = tmp_path
        mock_my_library = mock_zoteroing_output / "My Library"
        mock_my_library.mkdir()
        mock_bibtex_file = mock_my_library / "My Library.bib"
        mock_bibtex_file.touch()
        mock_bibtex_file.write_text( "some bibtex" )

        res = ZOH._get_bibtex_from_path(_self, mock_zoteroing_output )

        assert not res is None
        assert res == "some bibtex"

class Test_URLs_need_manual_handling:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._info_json_paths_and_content.return_value = {}
        _self._get_bibtex_and_files.return_value = {}
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._URLs_need_manual_handling(_self, "some path" )

        assert len(res) == 0

    def test2(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._info_json_paths_and_content.return_value = {
            "some path": {
                'URL': "some URL",
                'error': True,
            }
        }
        _self._get_bibtex_and_files.return_value = {}
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._URLs_need_manual_handling(_self, "some path" )

        assert len(res) == 1
        assert res[0] == "some URL"

    def test3(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._info_json_paths_and_content.return_value = {
            "some path": {
                'URL': "some URL",
                'error': False,
            }
        }
        _self._get_bibtex_and_files.return_value = {}
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._URLs_need_manual_handling(_self, "some path" )

        assert len(res) == 0

    def test4(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._info_json_paths_and_content.return_value = {
            "some path": {
                'URL': "some URL",
                'error': False,
            }
        }
        _self._get_bibtex_and_files.return_value = {
            "some other URL": None,
        }
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._URLs_need_manual_handling(_self, "some path" )

        assert len(res) == 1
        assert res[0] == "some other URL"

    def test5(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._info_json_paths_and_content.return_value = {
            "some path": {
                'URL': "some URL",
                'error': False,
            }
        }
        _self._get_bibtex_and_files.return_value = {
            "some other URL": {
                "files": [],
            },
        }
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._URLs_need_manual_handling(_self, "some path" )

        assert len(res) == 1
        assert res[0] == "some other URL"

    def test6(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._info_json_paths_and_content.return_value = {
            "some path": {
                'URL': "some URL",
                'error': False,
            }
        }
        _self._get_bibtex_and_files.return_value = {
            "some other URL": {
                "files": ["some file path"],
            },
        }
        
        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        res = ZOH._URLs_need_manual_handling(_self, "some path" )

        assert len(res) == 0

class Test_manual_handling_file:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._URLs_need_manual_handling.return_value = ["some URL"]

        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        mock_Zoteroing_output = tmp_path
        res = ZOH._manual_handling_file(_self, mock_Zoteroing_output )

        import pandas as pd
        df = pd.DataFrame(res)
        l = df["URL"].to_list()

        assert len(l) == 1
        assert l[0] == "some URL"
        ls = list(mock_Zoteroing_output.iterdir())
        assert len(ls) == 1
        assert "needs_manual_handling.html" in str(ls)

        import pandas as pd
        for _df in pd.read_html(ls[0]):
            assert len(_df["URL"].to_list()) == 1
            assert _df["URL"].to_list()[0] == "some URL"

    def test2(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._URLs_need_manual_handling.return_value = ["some URL"]

        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        mock_Zoteroing_output = tmp_path
        
        #test1
        res1 = ZOH._manual_handling_file(_self, mock_Zoteroing_output )

        import pandas as pd
        df = pd.DataFrame(res1)
        l = df["URL"].to_list()

        assert len(l) == 1
        assert l[0] == "some URL"
        ls = list(mock_Zoteroing_output.iterdir())
        assert len(ls) == 1
        assert "needs_manual_handling.html" in str(ls)

        import pandas as pd
        for _df in pd.read_html(ls[0]):
            assert len(_df["URL"].to_list()) == 1
            assert _df["URL"].to_list()[0] == "some URL"

        #test2
        _self._URLs_need_manual_handling.return_value = ["some other URL"]

        res2 = ZOH._manual_handling_file(_self, mock_Zoteroing_output )

        import pandas as pd
        df2 = pd.DataFrame(res2)
        l2 = df2["URL"].to_list()

        assert len(l2) == 2
        sl2 = set(l2)
        assert "some URL" in sl2
        assert "some other URL" in sl2
        ls2 = list(mock_Zoteroing_output.iterdir())
        assert len(ls2) == 1
        assert "needs_manual_handling.html" in str(ls2)

        import pandas as pd
        for _df in pd.read_html(ls2[0]):
            assert len(_df["URL"].to_list()) == 2
            _ = set(_df["URL"].to_list())
            assert "some URL" in _
            assert "some other URL" in _

class Test_assemble_zoteroing_output:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._get_bibtex_and_files.return_value = {}

        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        mock_Zoteroing_output = tmp_path
        res = ZOH._assemble_zoteroing_output(_self, mock_Zoteroing_output )

        mock_Zoteroing_output

        assert len(res) == 0

    def test2(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._get_bibtex_and_files.return_value = {"some URL": None}

        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        mock_Zoteroing_output = tmp_path
        res = ZOH._assemble_zoteroing_output(_self, mock_Zoteroing_output )

        mock_Zoteroing_output

        assert len(res) == 1
        assert list(res.keys())[0] == "some URL"
        ls = [str(_.name) for _ in mock_Zoteroing_output.rglob("*")]
        sls = set( ls )
        assert "results" in ls
        assert "1" in ls
        assert "url.txt" in ls

        for _ in mock_Zoteroing_output.rglob("*"):
            if _.name == "url.txt":
                assert _.read_text() == "some URL"

    def test3(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._get_bibtex_and_files.return_value = {
            "some URL": {
                "bibtex": None
            }
        }

        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        mock_Zoteroing_output = tmp_path
        res = ZOH._assemble_zoteroing_output(_self, mock_Zoteroing_output )

        mock_Zoteroing_output

        assert len(res) == 1
        assert list(res.keys())[0] == "some URL"
        ls = [str(_.name) for _ in mock_Zoteroing_output.rglob("*")]
        sls = set( ls )
        assert "results" in ls
        assert "1" in ls
        assert "url.txt" in ls

        for _ in mock_Zoteroing_output.rglob("*"):
            if _.name == "url.txt":
                assert _.read_text() == "some URL"

    def test4(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._get_bibtex_and_files.return_value = {
            "some URL": {
                "bibtex": "some bibtex",
            },
        }

        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper

        mock_Zoteroing_output = tmp_path
        res = ZOH._assemble_zoteroing_output(_self, mock_Zoteroing_output )

        mock_Zoteroing_output

        assert len(res) == 1
        assert list(res.keys())[0] == "some URL"
        assert "bibtex" in res["some URL"]
        assert not res["some URL"]["bibtex"] is None

        from pathlib import Path
        assert Path(res["some URL"]["bibtex"]).exists()

        ls = [str(_.name) for _ in mock_Zoteroing_output.rglob("*")]
        sls = set( ls )
        assert "results" in ls
        assert "1" in ls
        assert "url.txt" in ls
        assert "bibtex.bib" in ls

        for _ in mock_Zoteroing_output.rglob("*"):
            if _.name == "url.txt":
                assert _.read_text() == "some URL"

            if _.name == "bibtex.bib":
                assert _.read_text() == "some bibtex"

    def test5(self, mocker, tmp_path):
        mock_Zoteroing_output = tmp_path
        #mock_file = mock_Zoteroing_output / "some file"
        #mock_file.touch()

        _self = mocker.MagicMock()
        _self._get_bibtex_and_files.return_value = {
            "some URL": {
                "bibtex": "some bibtex",
                #"files": [str(mock_file)],
            },
        }

        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper
        
        res = ZOH._assemble_zoteroing_output(_self, mock_Zoteroing_output )

        assert len(res) == 1
        assert list(res.keys())[0] == "some URL"
        assert "bibtex" in res["some URL"]
        assert not "files" in res["some URL"]
        assert len(res["some URL"]) == 1
        assert not res["some URL"]["bibtex"] is None

        from pathlib import Path
        assert Path(res["some URL"]["bibtex"]).exists()

        ls = [str(_.name) for _ in mock_Zoteroing_output.rglob("*")]
        sls = set( ls )
        assert "results" in ls
        assert "1" in ls
        assert "url.txt" in ls
        assert "bibtex.bib" in ls

        for _ in mock_Zoteroing_output.rglob("*"):
            if _.name == "url.txt":
                assert _.read_text() == "some URL"

            if _.name == "bibtex.bib":
                assert _.read_text() == "some bibtex"

    def test6(self, mocker, tmp_path):
        mock_Zoteroing_output = tmp_path
        mock_file = mock_Zoteroing_output / "some file"
        mock_file.touch()

        _self = mocker.MagicMock()
        _self._get_bibtex_and_files.return_value = {
            "some URL": {
                "bibtex": "some bibtex",
                "files": [str(mock_file)],
            },
        }

        from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper
        ZOH = _zoteroing_output_helper
        
        res = ZOH._assemble_zoteroing_output(_self, mock_Zoteroing_output )

        mock_file.unlink() #remove mock file to avoid messing up the tests
        from pathlib import Path
        assert not Path(mock_file).exists()

        assert len(res) == 1
        assert list(res.keys())[0] == "some URL"
        assert "bibtex" in res["some URL"]
        assert "files" in res["some URL"]
        assert len(res["some URL"]) == 2
        assert not res["some URL"]["bibtex"] is None
        assert not res["some URL"]["files"] is None
        assert len(res["some URL"]["files"]) == 1

        from pathlib import Path
        assert Path(res["some URL"]["bibtex"]).exists()
        assert Path(res["some URL"]["files"][0]).exists()

        ls = [str(_.name) for _ in mock_Zoteroing_output.rglob("*")]
        sls = set( ls )
        assert "results" in ls
        assert "1" in ls
        assert "url.txt" in ls
        assert "bibtex.bib" in ls
        assert "some file" in ls

        for _ in mock_Zoteroing_output.rglob("*"):
            if _.name == "url.txt":
                assert _.read_text() == "some URL"

            if _.name == "bibtex.bib":
                assert _.read_text() == "some bibtex"