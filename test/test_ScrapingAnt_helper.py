import pytest

class Test_search:
    def test1(self, mocker, tmp_path):
        m1 = mocker.patch("lib.search.ScrapingAnt_helper.ScrapingAnt_helper")

        import lib.search.ScrapingAnt_helper as SAH
        SAH.search("test")

        m1.assert_called()

class Test_ScrapingAnt_helper:
    def test1(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        m1 = mocker.patch("lib.search._search_input_validator.validate")

        from lib.search.ScrapingAnt_helper import ScrapingAnt_helper as SAH
        SAH.__init__(_self, "test")

        m1.assert_called()

    def test2(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._parse.return_value = ["test"]

        from lib.search.ScrapingAnt_helper import ScrapingAnt_helper as SAH
        res = SAH.run(_self)

        assert len(res) == 1
        assert res[0] == "test"

    def test3(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._parse.return_value = []

        mocker.patch("time.sleep")

        from lib.search.ScrapingAnt_helper import ScrapingAnt_helper as SAH
        import lib.exceptions as exp
        try:
            res = SAH.run(_self)
        except exp.search.Failed_Search:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test4(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        _self._parse.return_value = ["test"]

        from lib.search.ScrapingAnt_helper import ScrapingAnt_helper as SAH
        _params = {
            "page": 1,
            "query":"test",
            "since":"since_value",
            "until":"until_value",
        }

        res = SAH._get_query_string(_self, _params)

        assert isinstance(res, str)
        assert "scholar" in res
        assert "since_value" in res
        assert "until_value" in res
        assert "test" in res
        assert "start=0" in res

    def test5(self, mocker, tmp_path):
        _self = mocker.MagicMock()
        type(_self)._last_proxy_country = None
        
        from lib.search.ScrapingAnt_helper import ScrapingAnt_helper as SAH
        res = SAH._choose_proxy_country(_self)

        assert isinstance(res, str)
        assert not _self._last_proxy_country is None

    def test6(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        m1 = mocker.patch("scrapingant_client.ScrapingAntClient")
        mock_client = mocker.MagicMock()
        m1.return_value = mock_client

        from lib.search.ScrapingAnt_helper import ScrapingAnt_helper as SAH
        res = SAH._search(_self, "test", "test country")

        mock_client.general_request.assert_called()

    def test7(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        import scrapingant_client

        m1 = mocker.patch("scrapingant_client.ScrapingAntClient")
        mock_client = mocker.MagicMock()
        mock_client.general_request.side_effect = scrapingant_client.ScrapingantClientException()
        m1.return_value = mock_client

        from lib.search.ScrapingAnt_helper import ScrapingAnt_helper as SAH
        import lib.exceptions as exp
        try:
            res = SAH._search(_self, "test", "test country")
        except exp.search.Failed_Search:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test8(self, mocker, tmp_path):
        _self = mocker.MagicMock()

        import bs4
        m1 = mocker.patch.object(bs4, "BeautifulSoup")

        from lib.search.ScrapingAnt_helper import ScrapingAnt_helper as SAH
        res = SAH._parse(_self, "test")
        
        assert res == []