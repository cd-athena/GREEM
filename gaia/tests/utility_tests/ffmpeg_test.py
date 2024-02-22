import json

import pytest
from gaia.utils.configuration_classes import (
    Resolution,
    Rendition,
    EncodingConfigDTO,
    EncodingConfig)

from gaia.utils.ffmpeg import CodecProcessing

BITRATE: str = 'bitrate'
BITRATE_BASE_VALUE: int = 1000

WIDTH: str = 'width'
WIDTH_BASE_VALUE: int = 200

HEIGHT: str = 'height'
HEIGHT_BASE_VALUE: int = 100


# '''
#    --------------------------------------------------------------------------------------------------

#                                                HELPER FUNCTIONS
#    --------------------------------------------------------------------------------------------------
# '''


def get_base_resolution() -> Resolution:
    return Resolution(height=HEIGHT_BASE_VALUE, width=WIDTH_BASE_VALUE)


def get_base_rendition() -> Rendition:
    return Rendition(height=HEIGHT_BASE_VALUE, width=WIDTH_BASE_VALUE, bitrate=BITRATE_BASE_VALUE)


def get_base_encoding_config_dto() -> EncodingConfigDTO:
    return EncodingConfigDTO(codec='avc', preset='medium',
                             rendition=get_base_rendition(), segment_duration=1, framerate=10)


def get_base_encoding_config() -> EncodingConfig:
    return EncodingConfig(
        codecs=['avc', 'hevc'],
        presets=['medium'],
        renditions=[get_base_rendition(), Rendition.new()],
        segment_duration=[1, 2],
        framerate=[24, 30],
        encode_all_videos=True,
        videos_to_encode=[],
        input_directory_path=['input_path'])


# '''
#    --------------------------------------------------------------------------------------------------

#                                                TEST CASES
#    --------------------------------------------------------------------------------------------------
# '''

def test_basic_codec_processing_init():
    cp = CodecProcessing()

    assert cp is not None
    assert cp.cuda_encoding is False
    assert cp.quiet_mode is False

    cp = CodecProcessing(cuda_encoding=True)

    assert cp is not None
    assert cp.cuda_encoding is True
    assert cp.quiet_mode is False

    cp = CodecProcessing(quiet_mode=True)

    assert cp is not None
    assert cp.cuda_encoding is False
    assert cp.quiet_mode is True

    cp = CodecProcessing(cuda_encoding=True, quiet_mode=True)

    assert cp is not None
    assert cp.cuda_encoding is True
    assert cp.quiet_mode is True



def test_codec_processing_is_codec_supported():
    cp = CodecProcessing()

    # test AVC support
    assert cp.is_codec_supported('h264')
    assert cp.is_codec_supported('avc')

    # test HEVC support
    assert cp.is_codec_supported('h265')
    assert cp.is_codec_supported('hevc')


def test_codec_processing_create_sequential_cmd():
    cp = CodecProcessing()

    input_file_path = 'input_file_path'
    input_file_name = 'input_file_name'
    output_dir_path = 'output_dir_path'
    dto = get_base_encoding_config_dto()

    sequential_cmd = cp.create_sequential_encoding_cmd(
        input_file_path, 
        input_file_name, 
        output_dir_path, 
        dto)

    assert sequential_cmd is not None
    assert len(sequential_cmd) > 0
    # function parameters are expected to be included
    assert input_file_path in sequential_cmd
    assert input_file_name in sequential_cmd
    assert output_dir_path in sequential_cmd

    # preset should be included
    assert dto.preset in sequential_cmd
    # output directory path should include the dto output path
    assert dto.get_output_directory() in sequential_cmd
    # full output directory path
    assert f'{output_dir_path}/{dto.get_output_directory()}' in sequential_cmd

    # rendition values should be included
    assert str(dto.rendition.bitrate) in sequential_cmd
    assert str(dto.rendition.height) in sequential_cmd
    assert str(dto.rendition.width) in sequential_cmd

    