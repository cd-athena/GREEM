import json

import pytest
from greem.utility.configuration_classes import (
    Resolution,
    Representation,
    EncodingConfigDTO,
    EncodingConfig,
)

from greem.utility.ffmpeg import CodecProcessing, get_lib_codec

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


def get_base_rendition() -> Representation:
    return Representation(
        height=HEIGHT_BASE_VALUE, width=WIDTH_BASE_VALUE, bitrate=BITRATE_BASE_VALUE
    )


def get_base_encoding_config_dto() -> EncodingConfigDTO:
    return EncodingConfigDTO(
        codec="avc",
        preset="medium",
        representation=get_base_rendition(),
        segment_duration=1,
        framerate=10,
    )


def get_base_encoding_config() -> EncodingConfig:
    return EncodingConfig(
        codecs=["avc", "hevc"],
        presets=["medium"],
        representations=[get_base_rendition(), Representation.new()],
        segment_duration=[1, 2],
        framerate=[24, 30],
        encode_all_videos=True,
        videos_to_encode=[],
        input_directory_path=["input_path"],
    )


# '''
#    --------------------------------------------------------------------------------------------------

#                                                TEST CASES
#    --------------------------------------------------------------------------------------------------
# '''

def test_get_lib_codec():
    avc_lib = 'libx264'
    avc_cuda_lib = 'h264_nvenc'
    hevc_lib = 'libx265'
    hevc_cuda_lib = 'hevc_nvenc'
    av1_lib = 'libsvtav1'
    vp9_lib = 'libvpx-vp9'
    vvc_lib = 'vvc'
    # these codecs should exist
    # AVC
    assert get_lib_codec('avc') == avc_lib
    assert get_lib_codec('h264') == avc_lib
    # AVC with CUDA
    assert get_lib_codec(value='avc', cuda_mode=True) == avc_cuda_lib
    assert get_lib_codec(value='h264', cuda_mode=True) == avc_cuda_lib
    # HEVC
    assert get_lib_codec('hevc') == hevc_lib
    assert get_lib_codec('h265') == hevc_lib
    # HEVC with CUDA
    assert get_lib_codec(value='hevc', cuda_mode=True) == hevc_cuda_lib
    assert get_lib_codec(value='h265', cuda_mode=True) == hevc_cuda_lib
    # AV1
    assert get_lib_codec('av1') == av1_lib
    # VP9
    assert get_lib_codec('vp9') == vp9_lib
    # VVC
    assert get_lib_codec('vvc') == vvc_lib

    # should also work with strings not being lowercase
    assert get_lib_codec('avc'.upper()) == avc_lib
    assert get_lib_codec('h264'.upper()) == avc_lib
    assert get_lib_codec('hevc'.upper()) == hevc_lib
    assert get_lib_codec('h265'.upper()) == hevc_lib
    assert get_lib_codec('av1'.upper()) == av1_lib
    assert get_lib_codec('vp9'.upper()) == vp9_lib
    assert get_lib_codec('vvc'.upper()) == vvc_lib

# '''
#    --------------------------------------------------------------------------------------------------

#                                         CODEC PROCESSING TEST CASES
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

    # AV1 is currently not supported
    assert not cp.is_codec_supported('av1')

    # VP9 is currently not supported
    assert not cp.is_codec_supported('vp9')

    # VVC is currently not supported
    assert not cp.is_codec_supported('vvc')


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
    assert str(dto.representation.bitrate) in sequential_cmd
    assert str(dto.representation.height) in sequential_cmd
    assert str(dto.representation.width) in sequential_cmd
