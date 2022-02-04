import pytest

class Test_is_int:
    def test1(self, mocker):
        import lib.util as util

        assert util.is_int(2)

    def test2(self, mocker):
        import lib.util as util

        assert util.is_int("2")

    def test3(self, mocker):
        import lib.util as util

        assert not util.is_int("a")

    def test4(self, mocker):
        import lib.util as util

        assert not util.is_int("4.2")

    def test5(self, mocker):
        import lib.util as util

        assert not util.is_int(4.2)

class Test_wait_for:
    def test1(self, mocker):
        def f(): return True
        import lib.util as util

        assert util._wait_for(f)

    def test2(self, mocker):
        def f(): return False
        import lib.util as util

        assert (not util._wait_for(f, 1))

class Test_remove_all_services:
    @pytest.fixture(autouse=True)
    def _setup_and_teardown(self, mocker):
        '''
        Setup
        '''

        #mocking the docker import and docker.from_env()
        import sys
        self.mock_client = mocker.MagicMock()
        sys.modules['docker'] = mocker.MagicMock()
        sys.modules['docker'].from_env.return_value = self.mock_client

        yield

        '''
        Teardown
        '''
        del sys.modules['docker']
        del self.mock_client

    def test1(self, mocker):
        import lib.docker.docker_helper as DH
        
        DH._remove_all_services()

        self.mock_client.services.list.assert_called()

    def test2(self, mocker):
        mock_service_obj = mocker.MagicMock()
        self.mock_client.services.list.return_value = [mock_service_obj]

        import lib.docker.docker_helper as DH
        
        DH._remove_all_services()

        self.mock_client.services.list.assert_called()
        mock_service_obj.remove.assert_called()

class Test_get_short_path_name:
    def test1(self, mocker):
        from pathlib import Path
        m1 = mocker.patch.object(Path, "absolute")
        m1.return_value = "test"

        mock_subprocess_run_return = mocker.MagicMock()
        type(mock_subprocess_run_return).returncode = 0

        m2 = mocker.patch("subprocess.run")
        type(m2).return_value = mock_subprocess_run_return

        import lib.util as util
        util.get_short_path_name("test")

        mock_subprocess_run_return.stdout.decode.assert_called()

    def test2(self, mocker):
        from pathlib import Path
        m1 = mocker.patch.object(Path, "absolute")
        m1.return_value = "test"

        mock_subprocess_run_return = mocker.MagicMock()
        type(mock_subprocess_run_return).returncode = 1

        m2 = mocker.patch("subprocess.run")
        type(m2).return_value = mock_subprocess_run_return

        #m3 = mocker.patch("str.rstrip")

        import lib.util as util
        _ret = util.get_short_path_name("test")

        assert _ret is None

class Test_is_valid_path:
    def test1(self, mocker, tmp_path):
        import lib.util as util
        _ret = util._is_valid_path(tmp_path)

        assert _ret

    def test2(self, mocker, tmp_path):
        import lib.util as util
        _ret = util._is_valid_path("")

        assert not _ret

    def test3(self, mocker, tmp_path):
        mock_path = tmp_path / "some fake path"
        
        import lib.util as util
        _ret = util._is_valid_path(mock_path)

        assert not _ret

class Test_is_iterable:
    def test1(self, mocker):
        import lib.util as util
        _ret = util._is_iterable([])

        assert _ret

    def test2(self, mocker):
        import lib.util as util
        _ret = util._is_iterable("test")

        assert not _ret

    def test3(self, mocker):
        import lib.util as util
        _ret = util._is_iterable(2)

        assert not _ret
    
class Test_is_valid_URL:
    def test1(self, mocker):
        mocker.patch("lib.util._network_connected")
        mocker.patch("lib.util._is_URL")
        mocker.patch("lib.util._is_URL_up")

        import lib.util as util
        _ret = util._is_valid_URL("test")

        assert _ret

    def test2(self, mocker):
        m1 = mocker.patch("lib.util._network_connected")
        m2 = mocker.patch("lib.util._is_URL")
        m3 = mocker.patch("lib.util._is_URL_up")

        m2.return_value = False

        import lib.util as util
        _ret = util._is_valid_URL("test")

        assert not _ret

    def test3(self, mocker):
        m1 = mocker.patch("lib.util._network_connected")
        m2 = mocker.patch("lib.util._is_URL")
        m3 = mocker.patch("lib.util._is_URL_up")

        m3.return_value = False

        import lib.util as util
        _ret = util._is_valid_URL("test")

        assert not _ret

    def test4(self, mocker):
        m1 = mocker.patch("lib.util._network_connected")
        m2 = mocker.patch("lib.util._is_URL")
        m3 = mocker.patch("lib.util._is_URL_up")

        m1.return_value = False

        import lib.util as util
        import lib.exceptions as exp
        try:
            _ret = util._is_valid_URL("test")
        except exp.Not_connected:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

class Test_is_URL:
    def test1(self, mocker):
        _good_URLs = [
            'http://foo.com/blah_blah',
            'http://foo.com/blah_blah/',
            'http://foo.com/blah_blah_(wikipedia)',
            'http://foo.com/blah_blah_(wikipedia)_(again)',
            'http://www.example.com/wpstyle/?p=364',
            'https://www.example.com/foo/?bar=baz&inga=42&quux',
            'http://✪df.ws/123',
            'http://userid:password@example.com:8080',
            'http://userid:password@example.com:8080/',
            'http://userid@example.com',
            'http://userid@example.com/',
            'http://userid@example.com:8080',
            'http://userid@example.com:8080/',
            'http://userid:password@example.com',
            'http://userid:password@example.com/',
            'http://142.42.1.1/',
            'http://142.42.1.1:8080/',
            'http://➡.ws/䨹',
            'http://⌘.ws',
            'http://⌘.ws/',
            'http://foo.com/blah_(wikipedia)#cite-1',
            'http://foo.com/blah_(wikipedia)_blah#cite-1',
            'http://foo.com/unicode_(✪)_in_parens'
            'http://foo.com/(something)?after=parens',
            'http://☺.damowmow.com/',
            'http://code.google.com/events/#&product=browser',
            'http://j.mp',
            'ftp://foo.bar/baz',
            'http://foo.bar/?q=Test%20URL-encoded%20stuff',
            'http://مثال.إختبار',
            'http://例子.测试',
            'http://उदाहरण.परीक्षा',
            r'''http://-.~_!$&'()*+,;=:%40:80%2f::::::@example.com''',
            'http://1337.net',
            'http://a.b-c.de',
            'http://223.255.255.254',
            'http://www.example.com',
            'http://www.example.com/some_page', #GOOD
            "http://www.abc.com", #GOOD
            "http://bbb3d.renderfarming.net/download.html", #GOOD
            "http://distribution.bbb3d.renderfarming.net/video/mp4/bbb_sunflower_1080p_30fps_normal.mp4", #GOOD
            'https://www.allyourmusic.com', #GOOD
            'http://www.stackoverflow.com', #GOOD
            'https://123.12.34.56:1234', #GOOD
            "http://www.google.com", #GOOD
            "https://www.google.com", #GOOD
            "http://google.com", #GOOD
            "https://google.com", #GOOD
            "http://www.google.com", #GOOD
            "http://google.com", #GOOD
            "http://www.google.com/~as_db3.2123/134-1a", #GOOD
            "https://www.google.com/~as_db3.2123/134-1a", #GOOD
            "http://google.com/~as_db3.2123/134-1a", #GOOD
            "https://google.com/~as_db3.2123/134-1a", #GOOD
            "http://www.google.com/~as_db3.2123/134-1a", #GOOD
            "http://google.com/~as_db3.2123/134-1a", #GOOD
            "http://www.google.co.uk", #GOOD
            "https://www.google.co.uk", #GOOD
            "http://google.co.uk", #GOOD
            "https://google.co.uk", #GOOD
            "http://www.google.co.uk", #GOOD
            "http://google.co.uk", #GOOD
            "http://www.google.co.uk/~as_db3.2123/134-1a", #GOOD
            "https://www.google.co.uk/~as_db3.2123/134-1a", #GOOD
            "http://google.co.uk/~as_db3.2123/134-1a", #GOOD
            "https://google.co.uk/~as_db3.2123/134-1a", #GOOD
            "http://www.google.co.uk/~as_db3.2123/134-1a", #GOOD
            "http://google.co.uk/~as_db3.2123/134-1a", #GOOD
            "https://google.co.", #GOOD
            "https://www.google.ro",
        ]
        
        for _u in _good_URLs:
            import lib.util as util
            _ret = util._is_URL(_u)
            if not _ret:
                mocker.fail(f"URL failed: {_u}")
            assert _ret

    def test2(self, mocker):
        _bad_URLs = [
            'http://',
            'http://.',
            'http://..',
            'http://../',
            'http://?',
            'http://??',
            'http://??/',
            'http://#',
            'http://##'
            'http://##/'
            'http://foo.bar?q=Spaces should be encoded',
            '//',
            '//a',
            '///a',
            '///',
            'http:///a',
            'foo.com',
            'rdar://1234',
            'h://test',
            'http:// shouldfail.com',
            ':// should fail',
            'http://foo.bar/foo(bar)baz quux',
            'ftps://foo.bar/',
            'http://-error-.invalid/',
            'http://-a.b.co',
            'http://a.b-.co',
            'http://0.0.0.0',
            'http://10.1.1.0'
            'http://10.1.1.255',
            'http://224.1.1.1',
            'http://1.1.1.1.1',
            'http://123.123.123',
            'http://3628126748',
            'http://.www.foo.bar/',
            'http://.www.foo.bar./',
            'http://10.1.1.1',
            "http://google", #BAD
            "https://...", #BAD
            "https://..", #BAD
            "https://.", #BAD
            "https://.google..com", #BAD
            "https://.google...com", #BAD
            "https://...google..com", #BAD
            "https://...google...com", #BAD
            'http://10.0.0.1', #GOOD
            "http://localhost:8080",
        ]
        
        for _u in _bad_URLs:
            import lib.util as util
            _ret = util._is_URL(_u)
            if _ret:
                mocker.fail(f"URL failed: {_u}")
            assert not _ret

    def test3(self, mocker):
        '''
        NOTE:
        The validators disagree on if this URL is valid, and so it is not
        tested
        But documented here for future revisions
        This URL is assumed to be invalid
        '''
        import lib.util as util
        _ret = util._is_URL('http://a.b--c.de/')

    def test4(self, mocker):
        '''
        NOTE:
        The validators disagree on if this URL is valid, and so it is not
        tested
        But documented here for future revisions
        This URL is assumed to be invalid
        '''
        import lib.util as util
        _ret = util._is_URL('http://www.foo.bar./')

class Test_is_URL_up:
    def test1(self, mocker):
        mocker.patch("lib.util._network_connected")

        mocker.patch("urllib.request.urlopen")

        import lib.util as util
        _ret = util._is_URL_up("test")

        assert _ret

    def test2(self, mocker):
        mocker.patch("lib.util._network_connected")

        m = mocker.patch("urllib.request.urlopen")
        from urllib import error
        m.side_effect = error.HTTPError(url="test", code=0, msg="test", hdrs="test", fp="test")

        import lib.util as util
        _ret = util._is_URL_up("test")

        assert _ret

    def test3(self, mocker):
        mocker.patch("lib.util._network_connected")

        import urllib
        m = mocker.patch("urllib.request.urlopen")
        import urllib
        m.side_effect = urllib.error.URLError(reason="Test")

        import lib.util as util
        _ret = util._is_URL_up("test")

        assert not _ret

    def test4(self, mocker):
        mocker.patch("lib.util._network_connected")

        m = mocker.patch("urllib.request.urlopen")
        import socket
        m.side_effect = socket.timeout()

        import lib.util as util
        _ret = util._is_URL_up("test")

        assert not _ret

class Test_network_connected:
    def test1(self, mocker):
        mocker.patch("lib.util._DNS_socket_connect")
        mocker.patch("lib.util._netcat_DNS")
        mocker.patch("lib.util._nmap")

        import lib.util as util
        _ret = util._network_connected()

        assert _ret

    def test2(self, mocker):
        m1 = mocker.patch("lib.util._DNS_socket_connect")
        m2 = mocker.patch("lib.util._netcat_DNS")
        m3 = mocker.patch("lib.util._nmap")

        m1.return_value = False

        import lib.util as util
        _ret = util._network_connected()

        assert _ret

    def test3(self, mocker):
        m1 = mocker.patch("lib.util._DNS_socket_connect")
        m2 = mocker.patch("lib.util._netcat_DNS")
        m3 = mocker.patch("lib.util._nmap")

        m1.return_value = False
        m2.return_value = False

        import lib.util as util
        _ret = util._network_connected()

        assert _ret

    def test4(self, mocker):
        m1 = mocker.patch("lib.util._DNS_socket_connect")
        m2 = mocker.patch("lib.util._netcat_DNS")
        m3 = mocker.patch("lib.util._nmap")

        m1.return_value = False
        m2.return_value = False
        m3.return_value = {"up" : False}

        import lib.util as util
        _ret = util._network_connected()

        assert not _ret

class Test_DNS_socket_connect:
    def test1(self, mocker):
        mocker.patch("socket.setdefaulttimeout")
        mocker.patch("socket.socket")

        import lib.util as util
        _ret = util._DNS_socket_connect("Test")

        assert _ret

    def test2(self, mocker):
        mocker.patch("socket.setdefaulttimeout")
        m = mocker.patch("socket.socket")

        import socket
        m.side_effect = socket.error()

        import lib.util as util
        _ret = util._DNS_socket_connect("Test")

        assert not _ret

class Test_DNS_socket_connect:
    def test1(self, mocker):
        m = mocker.patch("subprocess.run")
        mock_result = mocker.MagicMock()
        mock_result.stderr.decode.return_value = "open"
        m.return_value = mock_result

        import lib.util as util
        _ret = util._netcat_DNS("Test")

        assert _ret

    def test2(self, mocker):
        m = mocker.patch("subprocess.run")
        mock_result = mocker.MagicMock()
        mock_result.stderr.decode.return_value = "some bad response"
        m.return_value = mock_result

        import lib.util as util
        _ret = util._netcat_DNS("Test")

        assert not _ret

class Test_nmap:
    def test1(self, mocker, tmp_path):
        from pathlib import Path
        m0 = mocker.patch.object(Path, "resolve")

        m1 = mocker.patch("subprocess.run")
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        m1.return_value = mock_result

        m2 = mocker.patch("xmltodict.parse")
        
        #response format:
        #d_response["nmaprun"]["host"]["status"]["@state"]
        #d_response["nmaprun"]["host"]["ports"]["port"]
        mock_d_response = {
            "nmaprun" : {
                "host" : {
                    "status" : {
                        "@state" : "up",
                    },
                    "ports" : {
                        "port" : [{
                            "state" : {
                                "@state" : "open",
                            },
                            "@portid" : 42,
                        }]
                    }
                }
            }
        }
        m2.return_value = mock_d_response

        import lib.util as util
        _ret = util._nmap("Test")

        assert _ret["up"]
        assert _ret['open_port'] == [42]

    def test2(self, mocker, tmp_path):
        from pathlib import Path
        m0 = mocker.patch.object(Path, "resolve")

        m1 = mocker.patch("subprocess.run")
        mock_result = mocker.MagicMock()
        mock_result.returncode = 1
        m1.return_value = mock_result

        m2 = mocker.patch("xmltodict.parse")
        
        #response format:
        #d_response["nmaprun"]["host"]["status"]["@state"]
        #d_response["nmaprun"]["host"]["ports"]["port"]
        mock_d_response = {
            "nmaprun" : {
                "host" : {
                    "status" : {
                        "@state" : "up",
                    },
                    "ports" : {
                        "port" : [{
                            "state" : {
                                "@state" : "open",
                            },
                            "@portid" : 42,
                        }]
                    }
                }
            }
        }
        m2.return_value = mock_d_response

        import lib.util as util
        _ret = util._nmap("Test")

        assert not _ret["up"]
        assert len(_ret['open_port']) == 0

    def test3(self, mocker, tmp_path):
        from pathlib import Path
        m0 = mocker.patch.object(Path, "resolve")

        m1 = mocker.patch("subprocess.run")
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        m1.return_value = mock_result

        m2 = mocker.patch("xmltodict.parse")

        import xml
        m2.side_effect = xml.parsers.expat.ExpatError()
        
        #response format:
        #d_response["nmaprun"]["host"]["status"]["@state"]
        #d_response["nmaprun"]["host"]["ports"]["port"]
        mock_d_response = {
            "nmaprun" : {
                "host" : {
                    "status" : {
                        "@state" : "up",
                    },
                    "ports" : {
                        "port" : [{
                            "state" : {
                                "@state" : "open",
                            },
                            "@portid" : 42,
                        }]
                    }
                }
            }
        }
        m2.return_value = mock_d_response

        import lib.util as util
        _ret = util._nmap("Test")

        assert not _ret["up"]
        assert len(_ret['open_port']) == 0

    def test4(self, mocker, tmp_path):
        from pathlib import Path
        m0 = mocker.patch.object(Path, "resolve")

        m1 = mocker.patch("subprocess.run")
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        m1.return_value = mock_result

        m2 = mocker.patch("xmltodict.parse")

        import xmltodict
        m2.side_effect = xmltodict.ParsingInterrupted()
        
        #response format:
        #d_response["nmaprun"]["host"]["status"]["@state"]
        #d_response["nmaprun"]["host"]["ports"]["port"]
        mock_d_response = {
            "nmaprun" : {
                "host" : {
                    "status" : {
                        "@state" : "up",
                    },
                    "ports" : {
                        "port" : [{
                            "state" : {
                                "@state" : "open",
                            },
                            "@portid" : 42,
                        }]
                    }
                }
            }
        }
        m2.return_value = mock_d_response

        import lib.util as util
        _ret = util._nmap("Test")

        assert not _ret["up"]
        assert len(_ret['open_port']) == 0

    def test5(self, mocker, tmp_path):
        from pathlib import Path
        m0 = mocker.patch.object(Path, "resolve")

        m1 = mocker.patch("subprocess.run")
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        m1.return_value = mock_result

        m2 = mocker.patch("xmltodict.parse")
        
        #response format:
        #d_response["nmaprun"]["host"]["status"]["@state"]
        #d_response["nmaprun"]["host"]["ports"]["port"]
        mock_d_response = { }
        m2.return_value = mock_d_response

        import lib.util as util
        _ret = util._nmap("Test")

        assert not _ret["up"]
        assert len(_ret['open_port']) == 0

    def test6(self, mocker, tmp_path):
        from pathlib import Path
        m0 = mocker.patch.object(Path, "resolve")

        m1 = mocker.patch("subprocess.run")
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        m1.return_value = mock_result

        m2 = mocker.patch("xmltodict.parse")
        
        #response format:
        #d_response["nmaprun"]["host"]["status"]["@state"]
        #d_response["nmaprun"]["host"]["ports"]["port"]
        mock_d_response = {
            "nmaprun" : {
            }
        }
        m2.return_value = mock_d_response

        import lib.util as util
        _ret = util._nmap("Test")

        assert not _ret["up"]
        assert len(_ret['open_port']) == 0

    def test7(self, mocker, tmp_path):
        from pathlib import Path
        m0 = mocker.patch.object(Path, "resolve")

        m1 = mocker.patch("subprocess.run")
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        m1.return_value = mock_result

        m2 = mocker.patch("xmltodict.parse")
        
        #response format:
        #d_response["nmaprun"]["host"]["status"]["@state"]
        #d_response["nmaprun"]["host"]["ports"]["port"]
        mock_d_response = {
            "nmaprun" : {
                "host" : {
                }
            }
        }
        m2.return_value = mock_d_response

        import lib.util as util
        _ret = util._nmap("Test")

        assert not _ret["up"]
        assert len(_ret['open_port']) == 0

    def test8(self, mocker, tmp_path):
        from pathlib import Path
        m0 = mocker.patch.object(Path, "resolve")

        m1 = mocker.patch("subprocess.run")
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        m1.return_value = mock_result

        m2 = mocker.patch("xmltodict.parse")
        
        #response format:
        #d_response["nmaprun"]["host"]["status"]["@state"]
        #d_response["nmaprun"]["host"]["ports"]["port"]
        mock_d_response = {
            "nmaprun" : {
                "host" : {
                    "status" : {
                    },
                    "ports" : {
                        "port" : [{
                            "state" : {
                                "@state" : "open",
                            },
                            "@portid" : 42,
                        }]
                    }
                }
            }
        }
        m2.return_value = mock_d_response

        import lib.util as util
        _ret = util._nmap("Test")

        assert not _ret["up"]
        assert len(_ret['open_port']) == 0

    def test9(self, mocker, tmp_path):
        from pathlib import Path
        m0 = mocker.patch.object(Path, "resolve")

        m1 = mocker.patch("subprocess.run")
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        m1.return_value = mock_result

        m2 = mocker.patch("xmltodict.parse")
        
        #response format:
        #d_response["nmaprun"]["host"]["status"]["@state"]
        #d_response["nmaprun"]["host"]["ports"]["port"]
        mock_d_response = {
            "nmaprun" : {
                "host" : {
                    "status" : {
                        "@state" : "some bad response",
                    },
                    "ports" : {
                        "port" : [{
                            "state" : {
                                "@state" : "up",
                            },
                            "@portid" : 42,
                        }]
                    }
                }
            }
        }
        m2.return_value = mock_d_response

        import lib.util as util
        _ret = util._nmap("Test")

        assert not _ret["up"]
        assert len(_ret['open_port']) == 0

    def test10(self, mocker, tmp_path):
        from pathlib import Path
        m0 = mocker.patch.object(Path, "resolve")

        m1 = mocker.patch("subprocess.run")
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        m1.return_value = mock_result

        m2 = mocker.patch("xmltodict.parse")
        
        #response format:
        #d_response["nmaprun"]["host"]["status"]["@state"]
        #d_response["nmaprun"]["host"]["ports"]["port"]
        mock_d_response = {
            "nmaprun" : {
                "host" : {
                    "status" : {
                        "@state" : "up",
                    },
                    "ports" : {
                        "port" : [{
                            "state" : {
                                #"@state" : "up",
                            },
                            "@portid" : 42,
                        }]
                    }
                }
            }
        }
        m2.return_value = mock_d_response

        import lib.util as util
        _ret = util._nmap("Test")

        assert _ret["up"]
        assert len(_ret['open_port']) == 0

    def test11(self, mocker, tmp_path):
        from pathlib import Path
        m0 = mocker.patch.object(Path, "resolve")

        m1 = mocker.patch("subprocess.run")
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        m1.return_value = mock_result

        m2 = mocker.patch("xmltodict.parse")
        
        #response format:
        #d_response["nmaprun"]["host"]["status"]["@state"]
        #d_response["nmaprun"]["host"]["ports"]["port"]
        mock_d_response = {
            "nmaprun" : {
                "host" : {
                    "status" : {
                        "@state" : "up",
                    },
                    "ports" : {
                        "port" : [{
                            #"state" : {
                                #"@state" : "up",
                            #},
                            "@portid" : 42,
                        }]
                    }
                }
            }
        }
        m2.return_value = mock_d_response

        import lib.util as util
        _ret = util._nmap("Test")

        assert _ret["up"]
        assert len(_ret['open_port']) == 0

    def test12(self, mocker, tmp_path):
        from pathlib import Path
        m0 = mocker.patch.object(Path, "resolve")

        m1 = mocker.patch("subprocess.run")
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        m1.return_value = mock_result

        m2 = mocker.patch("xmltodict.parse")
        
        #response format:
        #d_response["nmaprun"]["host"]["status"]["@state"]
        #d_response["nmaprun"]["host"]["ports"]["port"]
        mock_d_response = {
            "nmaprun" : {
                "host" : {
                    "status" : {
                        "@state" : "up",
                    },
                    "ports" : {
                        "port" : [{
                            #"state" : {
                                #"@state" : "up",
                            #},
                            #"@portid" : 42,
                        }]
                    }
                }
            }
        }
        m2.return_value = mock_d_response

        import lib.util as util
        _ret = util._nmap("Test")

        assert _ret["up"]
        assert len(_ret['open_port']) == 0

    def test13(self, mocker, tmp_path):
        from pathlib import Path
        m0 = mocker.patch.object(Path, "resolve")

        m1 = mocker.patch("subprocess.run")
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        m1.return_value = mock_result

        m2 = mocker.patch("xmltodict.parse")
        
        #response format:
        #d_response["nmaprun"]["host"]["status"]["@state"]
        #d_response["nmaprun"]["host"]["ports"]["port"]
        mock_d_response = {
            "nmaprun" : {
                "host" : {
                    "status" : {
                        "@state" : "up",
                    },
                    "ports" : {
                        #"port" : [{
                            #"state" : {
                                #"@state" : "up",
                            #},
                            #"@portid" : 42,
                        #}]
                    }
                }
            }
        }
        m2.return_value = mock_d_response

        import lib.util as util
        _ret = util._nmap("Test")

        assert _ret["up"]
        assert len(_ret['open_port']) == 0

    def test14(self, mocker, tmp_path):
        from pathlib import Path
        m0 = mocker.patch.object(Path, "resolve")

        m1 = mocker.patch("subprocess.run")
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        m1.return_value = mock_result

        m2 = mocker.patch("xmltodict.parse")
        
        #response format:
        #d_response["nmaprun"]["host"]["status"]["@state"]
        #d_response["nmaprun"]["host"]["ports"]["port"]
        mock_d_response = {
            "nmaprun" : {
                "host" : {
                    "status" : {
                        "@state" : "up",
                    },
                    #"ports" : {
                        #"port" : [{
                            #"state" : {
                                #"@state" : "up",
                            #},
                            #"@portid" : 42,
                        #}]
                    #}
                }
            }
        }
        m2.return_value = mock_d_response

        import lib.util as util
        _ret = util._nmap("Test")

        assert _ret["up"]
        assert len(_ret['open_port']) == 0

    def test15(self, mocker, tmp_path):
        from pathlib import Path
        m0 = mocker.patch.object(Path, "resolve")

        m1 = mocker.patch("subprocess.run")
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        m1.return_value = mock_result

        m2 = mocker.patch("xmltodict.parse")
        
        #response format:
        #d_response["nmaprun"]["host"]["status"]["@state"]
        #d_response["nmaprun"]["host"]["ports"]["port"]
        mock_d_response = {
            "nmaprun" : {
                "host" : {
                    "status" : {
                        "@state" : "up",
                    },
                    "ports" : {
                        "port" : [{
                            "state" : {
                                "@state" : "some bad state",
                            },
                            "@portid" : 42,
                        }]
                    }
                }
            }
        }
        m2.return_value = mock_d_response

        import lib.util as util
        _ret = util._nmap("Test")

        assert _ret["up"]
        assert len(_ret['open_port']) == 0

class Test_is_valid_page_number:
    def test1(self, mocker):
        import lib.util as util
        assert not util.is_valid_page_number("bad input")

    def test2(self, mocker):
        import lib.util as util
        assert not util.is_valid_page_number(0)

    def test3(self, mocker):
        import lib.util as util
        assert util.is_valid_page_number(1)

class Test_is_valid_page_number:
    def test1(self, mocker):
        import lib.util as util
        assert not util._is_valid_year("bad input")

    def test2(self, mocker):
        import lib.util as util
        assert not util._is_valid_year(0)

    def test3(self, mocker):
        import lib.util as util
        assert util._is_valid_year(1)

    def test4(self, mocker):
        from datetime import datetime
        current_year = datetime.now().year

        import lib.util as util
        assert not util._is_valid_year(current_year + 1)

class Test_are_valid_search_years:
    def test1(self, mocker):
        import lib.util as util
        assert not util.are_valid_search_years("bad input", 1)

    def test2(self, mocker):
        import lib.util as util
        assert not util.are_valid_search_years(1, "bad input")

    def test3(self, mocker):
        import lib.util as util
        assert not util.are_valid_search_years("bad input", "bad input")

    def test4(self, mocker):
        import lib.util as util
        assert not util.are_valid_search_years(2, 1)

    def test5(self, mocker):
        import lib.util as util
        assert util.are_valid_search_years(1, 2)

class Test_is_pathlike:
    def test1(self, mocker):
        import lib.util as util
        assert util.is_pathlike("some string")

    def test2(self, mocker):
        import lib.util as util
        assert util.is_pathlike(bytes(10))

    def test3(self, mocker):
        import os
        class some_pathlike(os.PathLike): pass

        import lib.util as util
        assert util.is_pathlike( some_pathlike )

    def test4(self, mocker):
        from pathlib import PurePath
        class some_pathlike(PurePath): pass
        
        import lib.util as util
        assert util.is_pathlike( some_pathlike )

    def test5(self, mocker):
        class some_pathlike:
            def __fspath__(self): pass
        
        import lib.util as util
        assert util.is_pathlike( some_pathlike )

    def test6(self, mocker):
        class some_pathlike:
            __fspath__ = "some string"
        
        import lib.util as util
        assert not util.is_pathlike( some_pathlike )

    def test6(self, mocker):
        class some_pathlike: pass
        
        import lib.util as util
        assert not util.is_pathlike( some_pathlike )