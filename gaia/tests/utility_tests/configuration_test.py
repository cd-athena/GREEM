import json
from gaia.utils.configuration_classes import Resolution, Rendition

BITRATE: str = 'bitrate'
BITRATE_BASE_VALUE: int = 1000

WIDTH: str = 'width'
WIDTH_BASE_VALUE: int = 200

HEIGHT: str = 'height'
HEIGHT_BASE_VALUE: int = 100


def get_base_resolution() -> Resolution:
    return Resolution(height=HEIGHT_BASE_VALUE, width=WIDTH_BASE_VALUE)


def get_base_rendition() -> Rendition:
    return Rendition(height=HEIGHT_BASE_VALUE, width=WIDTH_BASE_VALUE, bitrate=BITRATE_BASE_VALUE)


def test_resolution_basic() -> None:
    resolution = get_base_resolution()

    assert resolution is not None
    assert isinstance(resolution.height, int)
    assert resolution.height == HEIGHT_BASE_VALUE
    assert isinstance(resolution.width, int)
    assert resolution.width == WIDTH_BASE_VALUE


def test_resolution_dir_repr_basic() -> None:
    resolution = get_base_resolution()

    assert resolution is not None
    assert isinstance(resolution.get_resolution_dir_representation(), str)
    assert resolution.get_resolution_dir_representation(
    ) == f'{WIDTH_BASE_VALUE}x{HEIGHT_BASE_VALUE}'


def test_resolution_from_dict() -> None:
    test_dict = {
        WIDTH: WIDTH_BASE_VALUE,
        HEIGHT: HEIGHT_BASE_VALUE,
    }
    resolution = Resolution(**test_dict)

    assert resolution is not None
    assert isinstance(resolution.height, int)
    assert resolution.height == HEIGHT_BASE_VALUE
    assert isinstance(resolution.width, int)
    assert resolution.width == 200


def test_resolution_to_dict() -> None:
    test_dict = {
        HEIGHT: HEIGHT_BASE_VALUE,
        WIDTH: 200,
    }
    resolution = get_base_resolution()

    json_dump: str = resolution.model_dump_json()
    # test if dump json is containing the string values
    assert json_dump is not None
    assert HEIGHT in json_dump
    assert f'{HEIGHT_BASE_VALUE}' in json_dump
    assert WIDTH in json_dump
    assert f'{WIDTH_BASE_VALUE}' in json_dump

    # test that converting to dictionary works
    json_dict: dict = json.loads(json_dump)
    assert json_dict == test_dict
    # test dumping model as dictionary
    json_dict = resolution.model_dump()
    assert json_dict is not None
    assert HEIGHT in json_dict
    assert json_dict[HEIGHT] == HEIGHT_BASE_VALUE
    assert WIDTH in json_dict
    assert json_dict[WIDTH] == 200


def test_rendition_basic() -> None:
    rendition = get_base_rendition()

    assert rendition is not None
    assert isinstance(rendition.height, int)
    assert rendition.height == HEIGHT_BASE_VALUE
    assert isinstance(rendition.width, int)
    assert rendition.width == WIDTH_BASE_VALUE


def test_rendition_dir_repr_basic() -> None:
    rendition = get_base_rendition()

    assert rendition is not None
    assert isinstance(rendition.get_rendition_dir_representation(), str)
    assert rendition.get_rendition_dir_representation(
    ) == f'{BITRATE_BASE_VALUE}k_{WIDTH_BASE_VALUE}x{HEIGHT_BASE_VALUE}'

    cls_rendition = Rendition.new()
    assert cls_rendition is not None
    assert isinstance(cls_rendition.get_rendition_dir_representation(), str)
    assert cls_rendition.get_rendition_dir_representation() == '0k_0x0'


def test_rendition_from_dict() -> None:
    test_dict = {
        BITRATE: 1000,
        WIDTH: 200,
        HEIGHT: 100,
    }
    rendition = Rendition(**test_dict)

    assert rendition is not None
    assert isinstance(rendition.height, int)
    assert rendition.height == HEIGHT_BASE_VALUE
    assert isinstance(rendition.width, int)
    assert rendition.width == WIDTH_BASE_VALUE
    assert isinstance(rendition.bitrate, int)
    assert rendition.bitrate == BITRATE_BASE_VALUE
