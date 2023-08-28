# Sources:
# * https://stackoverflow.com/questions/51286748/make-the-python-json-encoder-support-pythons-new-dataclasses

import yaml
from dacite import from_dict as fd
from dataclasses import dataclass, asdict
from typing import Type
from enum import Enum

class EncodingVariant(Enum):
    SEQUENTIAL = 1
    BATCH = 2


def read_yaml(file_path: str) -> dict:
    '''Reads a YAML file and returns a Python dictionary'''
    with open(file_path, 'r') as stream:
        try:
            yaml_file = yaml.safe_load(stream)
            return yaml_file
        except yaml.YAMLError as err:
            print(err)
            return {}


@dataclass
class Resolution:
    '''Represents a resolution in the form of height x width

    Example: 1080x1920
    '''
    height: int
    width: int


@dataclass
class Rendition(Resolution):
    '''Represents a rendition of a video file
    
    Example: 
    `Rendition(1080, 1920, 8100)` represents a rendition with a height of 1080, a width of 1920 and a bitrate of 8100KB
    '''
    bitrate: int

    def dir_representation(self) -> str:
        return f'{self.bitrate}k_{self.width}x{self.height}'

    @classmethod
    def from_dir_representation(cls: Type['Rendition'], dir_repr: str):
        if '/' in dir_repr:
            dir_repr = dir_repr.split('/')[-1]

        bitrate, resolution = dir_repr.split('_')
        bitrate = bitrate.removesuffix('k')

        width, height = resolution.split('x')

        return cls(
            int(bitrate),
            int(height),
            int(width)
        )
    
    @classmethod
    def get_batch_rendition(cls: Type['Rendition']):
        return cls(
            int(0),
            int(0),
            int(0)
        )
    
    def to_dict(self) -> dict:
        return {k: str(v) for k, v in asdict(self).items()}


@dataclass
class EncodingConfig():
    '''Represents the configuration for the video encoding'''
    codecs: list[str]
    presets: list[str]
    renditions: list[Rendition]
    segment_duration: list[int]
    encode_all_videos: bool
    videos_to_encode: list[str]

    @classmethod
    def from_dict(cls: Type['EncodingConfig'], data: dict):
        '''Creates an EncodingConfig object from a Python dictionary'''
        ec: EncodingConfig = fd(data_class=EncodingConfig, data=data)
        return ec

    @classmethod
    def from_file(cls: Type['EncodingConfig'], file_path: str):
        '''Creates an EncodingConfig object from a YAML file'''
        return cls.from_dict(read_yaml(file_path))

    def get_all_result_directories(self, video_names: list[str]) -> list[str]:
        '''Returns a list of all possible result directories'''
        return [
            # f'{codec}/{duration}s/{video}/{preset}/{rendition.dir_representation()}'
            get_output_directory(codec, video, duration, preset, rendition)
            for rendition in self.renditions
            for preset in self.presets
            for video in video_names
            for duration in self.segment_duration
            for codec in self.codecs
        ]

    # TODO find a way to store the metadata in a file


def get_output_directory(
    codec: str,
    video_name: str,
    duration: int,
    preset: str,
    rendition: Rendition
) -> str:
    '''Returns the output directory for the encoded video'''
    if any([x in video_name for x in ['.webm', '.mp4']]):
        video_name = video_name.removesuffix('.webm').removesuffix('.mp4')
    return f'{codec}/{video_name}/{duration}s/{preset}/{rendition.dir_representation()}'


@dataclass
class DecodingConfig():
    '''Represents the configuration for the video decoding'''
    scaling_enabled: bool
    scaling_resolutions: list[Resolution]
    decoding_sleep: float
    decode_all_videos: bool
    encoding_codecs: list[str]
    encoding_preset: list[str]
    encoding_renditions: list[Rendition]

    @classmethod
    def from_dict(cls: Type['DecodingConfig'], data: dict):
        '''Creates a DecodingConfig object from a Python dictionary'''
        dc: DecodingConfig = fd(data_class=DecodingConfig, data=data)
        return dc

    @classmethod
    def from_file(cls: Type['DecodingConfig'], file_path: str):
        '''Creates a DecodingConfig object from a YAML file'''
        return cls.from_dict(read_yaml(file_path))


if __name__ == '__main__':
    ec = EncodingConfig.from_file(
        '../config_files/default_encoding_config.yaml')
    print(ec)

    config = read_yaml('../config_files/default_decoding_config.yaml')
    dc = DecodingConfig.from_dict(config)
    print(dc)