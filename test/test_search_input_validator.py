import pytest

class Test_validate:
    def test1(self, mocker, tmp_path):
        import lib.util as util
        m1 = mocker.patch("lib.util.is_valid_page_number")
        m1.return_value = False

        import lib.search._search_input_validator as SIV
        import lib.exceptions as exp
        try:
            SIV.validate("test")
        except exp.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test2(self, mocker, tmp_path):
        import lib.util as util
        m1 = mocker.patch("lib.util.is_valid_page_number")
        m1.return_value = True

        m2 = mocker.patch("lib.util.is_valid_year")
        m2.return_value = False

        import lib.search._search_input_validator as SIV
        import lib.exceptions as exp
        try:
            SIV.validate("test", since=1)
        except exp.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test3(self, mocker, tmp_path):
        import lib.util as util
        m1 = mocker.patch("lib.util.is_valid_page_number")
        m1.return_value = True

        m2 = mocker.patch("lib.util.is_valid_year")
        m2.return_value = True

        m3 = mocker.patch("lib.util.are_valid_search_years")
        m3.return_value = False

        import lib.search._search_input_validator as SIV
        import lib.exceptions as exp
        try:
            SIV.validate("test", since=1, until=2)
        except exp.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test4(self, mocker, tmp_path):
        import lib.util as util
        m1 = mocker.patch("lib.util.is_valid_page_number")
        m1.return_value = True

        m2 = mocker.patch("lib.util.is_valid_year")
        m2.return_value = True

        m3 = mocker.patch("lib.util.are_valid_search_years")
        m3.return_value = True

        m4 = mocker.patch("lib.search.SERP_API_helper._SERP_API_search")

        import lib.search._search_input_validator as SIV
        res = SIV.validate("test")

        #assert res == {"query": "test", "page": 1, "since": None, "until": None}
        assert res == {"query": "test", "page": 1}

    def test5(self, mocker, tmp_path):
        import lib.util as util
        m1 = mocker.patch("lib.util.is_valid_page_number")
        m1.return_value = True

        m2 = mocker.patch("lib.util.is_valid_year")
        m2.return_value = True

        m3 = mocker.patch("lib.util.are_valid_search_years")
        m3.return_value = True

        m4 = mocker.patch("lib.search.SERP_API_helper._SERP_API_search")

        import lib.search._search_input_validator as SIV
        res = SIV.validate("test", page=2, since=1)

        #assert res == {"query": "test", "page": 1, "since": None, "until": None}
        assert res == {"query": "test", "page": 2, "since": 1}

    def test6(self, mocker, tmp_path):
        import lib.util as util
        m1 = mocker.patch("lib.util.is_valid_page_number")
        m1.return_value = True

        m2 = mocker.patch("lib.util.is_valid_year")
        m2.return_value = True

        m3 = mocker.patch("lib.util.are_valid_search_years")
        m3.return_value = True

        m4 = mocker.patch("lib.search.SERP_API_helper._SERP_API_search")

        import lib.search._search_input_validator as SIV
        res = SIV.validate("test", page=2, since=1, until=2)

        #assert res == {"query": "test", "page": 1, "since": None, "until": None}
        assert res == {"query": "test", "page": 2, "since": 1, "until": 2}