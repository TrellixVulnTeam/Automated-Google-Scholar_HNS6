#-------------------------------------------------------------------------------
#Docker exceptions
#-------------------------------------------------------------------------------

class Docker_is_not_running(Exception): pass
class Could_not_find_executable(Exception): pass
class No_such_container(Exception): pass
class Container_not_running(Exception): pass
class Could_not_launch_service(Exception): pass

import types

docker = types.SimpleNamespace()
docker.Docker_is_not_running = Docker_is_not_running
docker.Could_not_find_executable = Could_not_find_executable
docker.No_such_container = No_such_container
docker.Container_not_running = Container_not_running
docker.Could_not_launch_service = Could_not_launch_service

#-------------------------------------------------------------------------------
#image exceptions
#-------------------------------------------------------------------------------

class No_such_image(Exception): pass
class Bad_image_name_format(Exception): pass

import types
image = types.SimpleNamespace()
image.No_such_image = No_such_image
image.Bad_image_name_format = Bad_image_name_format

#-------------------------------------------------------------------------------
#search exceptions
#-------------------------------------------------------------------------------

class Failed_Search(Exception): pass
import types
search = types.SimpleNamespace()
search.Failed_Search = Failed_Search

#-------------------------------------------------------------------------------
#misc
#-------------------------------------------------------------------------------

class Bad_argument(Exception): pass

class File_does_not_exist(Exception): pass
class Is_not_file(Exception): pass
class Not_connected(Exception): pass
class Bad_Path(Exception): pass