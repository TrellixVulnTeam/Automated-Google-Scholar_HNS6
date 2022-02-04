import lib.logging as logging
LOG = logging.getLogger(__name__)

'''
Docker image names used for this project have the following format:
    <image_name>:<version_number>
Where `version_number` is an integer
'''
def get_latest_image(_img): return _get_latest_image(_img)
def find_image(_img): return _find_image(_img)
def list_images(): return _list_images()

def _get_latest_image(_img):
    _imgs = _find_image(_img)
    if len(_imgs) == 0:
        from lib.exceptions import image
        raise image.No_such_image(_img)

    #for each image, find the latest version (the one with the highest version
    #number)
    d_images = {}
    for _i in _imgs:
        _parts = _i.split(':')

        if len(_parts) == 2:
            try:
                _version = int(_parts[1])
            except ValueError:
                continue #not an integer

            _name = _parts[0]

            if not _name in d_images:
                d_images[_name] = _version

            if _version > d_images[_name]:
                d_images[_name] = _version

    if not _img in d_images:
        '''
        Found the image name, but it doesn't have the proper format
        '''
        _exp = "Format should be: "
        _exp += f"{_img}:<version_number>"
        from lib.exceptions import image
        raise image.Bad_image_name_format(_exp)

    return f"{_img}:{d_images[_img]}"

def _find_image(_img):
    if not isinstance(_img, str):
        import lib.exceptions
        raise lib.exceptions.Bad_argument("Argument should be string")

    if len(_img) == 0:
        return []

    _ret = []
    for _i in _list_images():
        if str(_img) in _i:
            _ret.append(_i)
    return _ret

def _list_images():
    '''
    returns a list of the names of images stored locally
    '''
    LOG.debug("Listing images seen in local docker")

    import lib.docker.docker_helper as dh
    dh.is_docker_ready()

    LOG.debug("Docker is ready")

    import docker
    client = docker.from_env()

    LOG.debug("Raw list of images seen:")

    _images = client.images.list()

    LOG.debug(_images)
    _ret = []
    for i in _images:
        if len(i.attrs['RepoTags']) == 0:
            LOG.debug("Skipping image with empty name:")
            LOG.debug(i.attrs['RepoTags'])
            continue

        _ret.append( i.attrs['RepoTags'][0] )

    LOG.debug("Names of all found images:")
    LOG.debug(_ret)
    
    return _ret