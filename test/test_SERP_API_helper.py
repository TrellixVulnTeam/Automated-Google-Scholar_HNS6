import pytest

class Test_SERP_API_search:
    def test1(self, mocker, tmp_path):
        from serpapi import GoogleSearch
        m1 = mocker.patch.object(GoogleSearch, "get_dict")
        m1.return_value = {
            "search_metadata" : {
                "status" : "Success",
            },
            'organic_results' : [{
                "link" : "test",
            }],
        }

        import lib.search.SERP_API_helper as SAH
        res = SAH._SERP_API_search("test")

        assert len(res) == 1
        assert res[0] == "test"

    def test2(self, mocker, tmp_path):
        from serpapi import GoogleSearch
        m1 = mocker.patch.object(GoogleSearch, "get_dict")
        m1.return_value = {
            "search_metadata" : {
                "status" : "Success",
            },
            'organic_results' : [{
                #"link" : "test",
            }],
        }

        import lib.search.SERP_API_helper as SAH
        res = SAH._SERP_API_search("test")

        assert len(res) == 0

    def test3(self, mocker, tmp_path):
        from serpapi import GoogleSearch
        m1 = mocker.patch.object(GoogleSearch, "get_dict")
        m1.return_value = {
            "search_metadata" : {
                "status" : "Success",
            },
            #'organic_results' : [{
                #"link" : "test",
            #}],
        }

        import lib.search.SERP_API_helper as SAH
        res = SAH._SERP_API_search("test")

        assert len(res) == 0

    def test4(self, mocker, tmp_path):
        from serpapi import GoogleSearch
        m1 = mocker.patch.object(GoogleSearch, "get_dict")
        m1.return_value = {
            "search_metadata" : {
                "status" : "some bad status",
            },
            #'organic_results' : [{
                #"link" : "test",
            #}],
        }

        import lib.search.SERP_API_helper as SAH
        res = SAH._SERP_API_search("test")

        assert len(res) == 0

    def test5(self, mocker, tmp_path):
        from serpapi import GoogleSearch
        m1 = mocker.patch.object(GoogleSearch, "get_dict")
        m1.return_value = {
            "search_metadata" : {
                #"status" : "some bad status",
            },
            'organic_results' : [{
                "link" : "test",
            }],
        }

        import lib.search.SERP_API_helper as SAH
        import lib.exceptions as exp
        try:
            SAH._SERP_API_search("test")
        except exp.search.Failed_Search:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test6(self, mocker, tmp_path):
        from serpapi import GoogleSearch
        m1 = mocker.patch.object(GoogleSearch, "get_dict")
        m1.return_value = {
            #"search_metadata" : {
                #"status" : "some bad status",
            #},
            'organic_results' : [{
                "link" : "test",
            }],
        }

        import lib.search.SERP_API_helper as SAH
        import lib.exceptions as exp
        try:
            SAH._SERP_API_search("test")
        except exp.search.Failed_Search:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test7(self, mocker, tmp_path):
        from serpapi import GoogleSearch
        m1 = mocker.patch.object(GoogleSearch, "get_dict")
        m1.return_value = {
            #"search_metadata" : {
                #"status" : "some bad status",
            #},
            #'organic_results' : [{
                #"link" : "test",
            #}],
        }

        import lib.search.SERP_API_helper as SAH
        import lib.exceptions as exp
        try:
            SAH._SERP_API_search("test")
        except exp.search.Failed_Search:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")