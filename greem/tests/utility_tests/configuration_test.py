import json

import pytest
from greem.utility.configuration_classes import (
    Resolution,
    Representation,
    EncodingConfigDTO,
    EncodingConfig,
)

BITRATE: str = "bitrate"
BITRATE_BASE_VALUE: int = 1000

WIDTH: str = "width"
WIDTH_BASE_VALUE: int = 200

HEIGHT: str = "height"
HEIGHT_BASE_VALUE: int = 100


# '''
#    --------------------------------------------------------------------------------------------------

#                                                HELPER FUNCTIONS
#    --------------------------------------------------------------------------------------------------
# '''


def get_base_resolution() -> Resolution:
    return Resolution(height=HEIGHT_BASE_VALUE, width=WIDTH_BASE_VALUE)


def get_base_representation() -> Representation:
    return Representation(
        height=HEIGHT_BASE_VALUE, width=WIDTH_BASE_VALUE, bitrate=BITRATE_BASE_VALUE
    )


def get_base_encoding_config_dto() -> EncodingConfigDTO:
    return EncodingConfigDTO(
        codec="avc",
        preset="medium",
        representation=get_base_representation(),
        segment_duration=1,
        framerate=10,
    )


def get_base_encoding_config() -> EncodingConfig:
    return EncodingConfig(
        codecs=["avc", "hevc"],
        presets=["medium"],
        representations=[get_base_representation(), Representation.new()],
        segment_duration=[1, 2],
        framerate=[24, 30],
    )


# '''
#    --------------------------------------------------------------------------------------------------

#                                                TEST CASES
#    --------------------------------------------------------------------------------------------------
# '''


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
    assert (
        resolution.get_resolution_dir_representation()
        == f"{WIDTH_BASE_VALUE}x{HEIGHT_BASE_VALUE}"
    )


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
    assert f"{HEIGHT_BASE_VALUE}" in json_dump
    assert WIDTH in json_dump
    assert f"{WIDTH_BASE_VALUE}" in json_dump

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


def test_representation_basic() -> None:
    representation = get_base_representation()

    assert representation is not None
    assert isinstance(representation.height, int)
    assert representation.height == HEIGHT_BASE_VALUE
    assert isinstance(representation.width, int)
    assert representation.width == WIDTH_BASE_VALUE


def test_representation_dir_repr_basic() -> None:
    representation = get_base_representation()

    assert representation is not None
    assert isinstance(representation.get_representation_dir_string(), str)
    assert (
        representation.get_representation_dir_string()
        == f"{BITRATE_BASE_VALUE}k_{WIDTH_BASE_VALUE}x{HEIGHT_BASE_VALUE}"
    )

    cls_representation = Representation.new()
    assert cls_representation is not None
    assert isinstance(cls_representation.get_representation_dir_string(), str)
    assert cls_representation.get_representation_dir_string() == "0k_0x0"


def test_representation_from_dict() -> None:
    test_dict = {
        BITRATE: 1000,
        WIDTH: 200,
        HEIGHT: 100,
    }
    representation = Representation(**test_dict)

    assert representation is not None
    assert isinstance(representation.height, int)
    assert representation.height == HEIGHT_BASE_VALUE
    assert isinstance(representation.width, int)
    assert representation.width == WIDTH_BASE_VALUE
    assert isinstance(representation.bitrate, int)
    assert representation.bitrate == BITRATE_BASE_VALUE


def test_encoding_config_dto_basic() -> None:
    dto = get_base_encoding_config_dto()

    assert dto is not None
    assert isinstance(dto, EncodingConfigDTO)
    assert isinstance(dto.codec, str)
    assert isinstance(dto.preset, str)
    assert isinstance(dto.segment_duration, int)
    assert isinstance(dto.framerate, int)

    assert dto.codec == "avc"
    assert dto.preset == "medium"
    assert dto.segment_duration == 1
    assert dto.framerate == 10


def test_encoding_config_dto_from_dict() -> None:
    data = {
        "codec": "avc",
        "preset": "medium",
        "representation": get_base_representation(),
        "segment_duration": 1,
        "framerate": 10,
    }
    dto = EncodingConfigDTO(**data)

    assert dto is not None
    assert isinstance(dto, EncodingConfigDTO)
    assert isinstance(dto.codec, str)
    assert isinstance(dto.preset, str)
    assert isinstance(dto.segment_duration, int)
    assert isinstance(dto.framerate, int)

    assert dto.codec == "avc"
    assert dto.preset == "medium"
    assert dto.segment_duration == 1
    assert dto.framerate == 10


def test_encoding_config_dto_get_output_directory() -> None:
    dto = get_base_encoding_config_dto()

    video_name: str = "AncientThought"
    extension: str = ".mp4"  # should be removed by function

    output_dir_path = dto.get_output_directory()

    assert output_dir_path is not None
    assert len(output_dir_path) > 0
    assert isinstance(output_dir_path, str)

    # assert video_name in output_dir_path
    # extension should not be kept in output path
    # assert extension not in output_dir_path


def test_encoding_config_base() -> None:
    config = get_base_encoding_config()

    assert config is not None
    assert isinstance(config, EncodingConfig)

    assert len(config.codecs) > 0
    assert len(config.presets) > 0
    assert len(config.representations) > 0


def test_encoding_config_from_file() -> None:
    # this config file should exist
    config = EncodingConfig.from_file(
        "greem/tests/utility_tests/test_datasets/test_config_file.yaml"
    )

    assert config is not None
    assert isinstance(config, EncodingConfig)

    assert len(config.codecs) == 2
    assert len(config.presets) == 10
    assert len(config.representations) == 6
    assert len(config.framerate) == 2  # type: ignore


def test_encoding_config_get_encoding_dtos() -> None:
    # this config file should exist
    config = EncodingConfig.from_file(
        "greem/tests/utility_tests/test_datasets/test_config_file.yaml"
    )

    encoding_dtos: list[EncodingConfigDTO] = config.get_encoding_dtos()

    #     assert len(result) > 0
    # assert 'avc' in result or 'hevc' in result
    # assert 'medium' in result
    # assert 'fps' in result
    # assert '24fps' in result or '30fps' in result

    # should not be None
    assert encoding_dtos is not None
    # should be of type list
    assert isinstance(encoding_dtos, list)
    # should not be empty
    assert len(encoding_dtos) == 240

    for dto in encoding_dtos:
        assert dto.is_dash is False
        assert dto.codec in ["h264", "h265"]
        assert dto.preset in [
            "ultrafast",
            "superfast",
            "veryfast",
            "faster",
            "fast",
            "medium",
            "slow",
            "slower",
            "veryslow",
            "placebo",
        ]
        assert dto.framerate in [24, 30]

    # this config file should exist
    config = EncodingConfig.from_file(
        "greem/tests/utility_tests/test_datasets/test_config_file.yaml"
    )
    config.is_dash = True

    encoding_dtos: list[EncodingConfigDTO] = config.get_encoding_dtos()

    # should not be None
    assert encoding_dtos is not None
    # should be of type list
    assert isinstance(encoding_dtos, list)
    # should not be empty
    assert len(encoding_dtos) == 1440

    for dto in encoding_dtos:
        assert dto.is_dash is True
        assert dto.codec in ["h264", "h265"]
        assert dto.preset in [
            "ultrafast",
            "superfast",
            "veryfast",
            "faster",
            "fast",
            "medium",
            "slow",
            "slower",
            "veryslow",
            "placebo",
        ]
        assert dto.framerate in [24, 30]


def test_encoding_config_from_file_raises_error() -> None:
    with pytest.raises(FileNotFoundError):
        EncodingConfig.from_file("your_file_is_in_another_castle")


def test_encoding_config_get_all_result_directories() -> None:
    config = get_base_encoding_config()

    result_directories = config.get_all_result_directories()

    assert result_directories is not None
    assert len(result_directories) == 8
    for result in result_directories:
        assert len(result) > 0
        assert "avc" in result or "hevc" in result
        assert "medium" in result
        assert "fps" in result
        assert "24fps" in result or "30fps" in result

    config = get_base_encoding_config()
    config.is_dash = True
    result_directories = config.get_all_result_directories()

    assert len(result_directories) == 16
    for result in result_directories:
        assert len(result) > 0
        assert "avc" in result or "hevc" in result
        assert "medium" in result
        assert "fps" in result
        assert "24fps" in result or "30fps" in result
