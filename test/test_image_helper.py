import pytest

'''
we also use pytest fixtures, which are code that we run before a test
and we signal to pytest that we want to call a fixture by including
the name of fixture as an argument for the test
then also fixtures can be defined with the dectorator:
@pytest.fixture
    see:
    https://docs.pytest.org/en/6.2.x/fixture.html

----

in these tests we use this formulation to test:

import sys
from unittest.mock import MagicMock
sys.modules['lib.docker.docker_helper'] = MagicMock()
sys.modules['lib.docker.docker_helper'].is_docker_ready = MagicMock(return_value=True)

what this does is to preload a name into sys.modules that maps to a module
imported into the code we're testing:

import lib.docker.docker_helper as dh
dh.is_docker_ready()

This way we can mock the functions within that module, when the module is imported
into the code being tested
as, for some stupid reason, we can't overwrite the module functions in the test
and undo them later, we have to use the sys.modules to make a global change
    see:
    https://stackoverflow.com/questions/43162722/mocking-a-module-import-in-pytest
    https://stackoverflow.com/questions/8658043/how-to-mock-an-import

----

In this code we use the contruction:
@pytest.fixture(autouse=True)
def _setup_and_teardown():

which is a fixture that runs before and after each test
a "yield" is used to pause execution in the middle of the function
so that when it is ran after each test, it picks up where execution paused
after setup
    see:
    https://stackoverflow.com/questions/22627659/run-code-before-and-after-each-test-in-py-test
'''
class Test_list_images:
    @pytest.fixture(autouse=True)
    def _setup_and_teardown(self, mocker):
        '''
        Setup
        '''
        #mock the import from lib.docker.docker_helper
        #and its function is_docker_ready()
        import sys
        sys.modules['lib.docker.docker_helper'] = mocker.MagicMock()
        sys.modules['lib.docker.docker_helper'].is_docker_ready = mocker.MagicMock()

        #mock an image object to return from client.images.list()
        mock_image_object1 = mocker.MagicMock()
        mock_image_object1.attrs = {'RepoTags': ["Test"]}
        mock_image_object2 = mocker.MagicMock()
        mock_image_object2.attrs = {'RepoTags': []}

        #mock the "client" object returned from docker.from_env()
        mock_client = mocker.MagicMock()
        mock_client.images.list.return_value = [mock_image_object1, mock_image_object2]
        
        #finally mocking the docker import and docker.from_env()
        sys.modules['docker'] = mocker.MagicMock()
        sys.modules['docker'].from_env.return_value = mock_client

        yield

        '''
        Teardown
        '''
        del sys.modules['docker']
        del sys.modules['lib.docker.docker_helper']

    def test1(self):
        import lib.docker.image_helper as IH
        _ret = IH._list_images()

        assert (len(_ret) == 1)
        assert (_ret[0] == "Test")

class Test_find_image:
    def test1(self, mocker):
        mock_list_img = mocker.patch("lib.docker.image_helper._list_images")
        mock_list_img.return_value = []

        import lib.docker.image_helper as IH
        _ret = IH._find_image("test")

        assert len(_ret) == 0

    def test2(self, mocker):
        mock_list_img = mocker.patch("lib.docker.image_helper._list_images")
        mock_list_img.return_value = []

        import lib.docker.image_helper as IH
        import lib.exceptions
        try:
            IH._find_image(None)
        except lib.exceptions.Bad_argument:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test3(self, mocker):
        mock_list_img = mocker.patch("lib.docker.image_helper._list_images")
        mock_list_img.return_value = []

        import lib.docker.image_helper as IH
        _ret = IH._find_image("")

        assert len(_ret) == 0

    def test4(self, mocker):
        mock_list_img = mocker.patch("lib.docker.image_helper._list_images")
        mock_list_img.return_value = ["fake_image_name"]

        import lib.docker.image_helper as IH
        _ret = IH._find_image("test")

        assert len(_ret) == 0

    def test5(self, mocker):
        mock_list_img = mocker.patch("lib.docker.image_helper._list_images")
        mock_list_img.return_value = ["fake_image_name:1", "test:2"]

        import lib.docker.image_helper as IH
        _ret = IH._find_image("test")

        assert len(_ret) == 1

    def test6(self, mocker):
        mock_list_img = mocker.patch("lib.docker.image_helper._list_images")
        mock_list_img.return_value = ["fake_image_name:1", "test:2", "test:1"]

        import lib.docker.image_helper as IH
        _ret = IH._find_image("test")

        assert len(_ret) == 2

class Test_get_latest_image:
    def test1(self, mocker):
        mock_list_img = mocker.patch("lib.docker.image_helper._find_image")
        mock_list_img.return_value = []

        import lib.docker.image_helper as IH
        import lib.exceptions
        try:
            IH._get_latest_image("test")
        except lib.exceptions.image.No_such_image:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test2(self, mocker):
        mock_list_img = mocker.patch("lib.docker.image_helper._find_image")
        mock_list_img.return_value = ["test:bad_version"]

        import lib.docker.image_helper as IH
        import lib.exceptions
        try:
            IH._get_latest_image("test")
        except lib.exceptions.image.Bad_image_name_format:
            assert True
        except Exception as err:
            pytest.fail(f"Saw unexpected exception: {err}")
        else:
            pytest.fail(f"Did not throw exception as expected.")

    def test3(self, mocker):
        mock_list_img = mocker.patch("lib.docker.image_helper._find_image")
        mock_list_img.return_value = ["test:1"]

        import lib.docker.image_helper as IH
        _ret = IH._get_latest_image("test")

        assert isinstance(_ret, str)
        assert _ret == "test:1"

    def test4(self, mocker):
        mock_list_img = mocker.patch("lib.docker.image_helper._find_image")
        mock_list_img.return_value = [
            "test:2", "test:1", "some_other_image:1", "another_image:latest"
        ]

        import lib.docker.image_helper as IH
        _ret = IH._get_latest_image("test")

        assert isinstance(_ret, str)
        assert _ret == "test:2"

    def test5(self, mocker):
        mock_list_img = mocker.patch("lib.docker.image_helper._find_image")
        mock_list_img.return_value = [
            "test:2", "test:1", "some_other_image:1", "another_image:latest"
        ]

        import lib.docker.image_helper as IH
        _ret = IH._get_latest_image("some_other_image")

        assert isinstance(_ret, str)
        assert _ret == "some_other_image:1"