import itertools
# Sources:
# * https://stackoverflow.com/questions/51286748/make-the-python-json-encoder-support-pythons-new-dataclasses

import yaml
from dacite import from_dict as fd
from dataclasses import dataclass, asdict
from typing import Type, Optional
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
    
    def get_resolution_dir_representation(self) -> str:
        return f'{self.width}x{self.height}'


@dataclass
class Rendition(Resolution):
    '''Represents a rendition of a video file

    Example: 
    `Rendition(1080, 1920, 8100)` represents a rendition with a height of 1080, a width of 1920 and a bitrate of 8100KB
    '''
    bitrate: int

    def get_rendition_dir_representation(self) -> str:
        return f'{self.bitrate}k_{self.get_resolution_dir_representation()}'

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
class EncodingConfigDTO():
    codec: str
    preset: str
    rendition: Rendition
    segment_duration: int
    framerate: int = 0

    def get_output_directory(
        self,
        video_name: str
    ) -> str:
        '''Returns the output directory for the encoded video'''
        if any([x in video_name for x in ['.webm', '.mp4']]):
            video_name = video_name.removesuffix('.webm').removesuffix('.mp4')
        output_dir: str = f'{self.codec}/{video_name}/{self.segment_duration}s/{self.preset}/{self.rendition.get_rendition_dir_representation()}'
        if self.framerate is not None and self.framerate > 0:
            output_dir = f'{output_dir}/{self.framerate}fps'

        return output_dir


@dataclass
class EncodingConfig():
    '''Represents the configuration for the video encoding'''
    codecs: list[str]
    presets: list[str]
    renditions: list[Rendition]
    segment_duration: list[int]
    framerate: list[int] | None
    encode_all_videos: bool
    videos_to_encode: Optional[list[str]]

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
        directory_list: list[str] = [
            get_output_directory(codec, video, duration, preset, rendition)
            for rendition in self.renditions
            for preset in self.presets
            for video in video_names
            for duration in self.segment_duration
            for codec in self.codecs
        ]

        if self.framerate is not None and len(self.framerate) > 0:
            directory_list = [
                f'{l}/{fr}' for l in directory_list for fr in self.framerate]

        return directory_list

    def get_encoding_dtos(self) -> list[EncodingConfigDTO]:
        encoding_dtos: list[EncodingConfigDTO] = list()

        for duration, preset, rendition, codec, fr in itertools.product(
                self.segment_duration,
                self.presets, self.renditions, self.codecs,
                self.framerate if self.framerate is not None and len(self.framerate) > 0 else []):
            dto = EncodingConfigDTO(codec, preset, rendition, duration, fr)
            encoding_dtos.append(dto)

        return encoding_dtos


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
    return f'{codec}/{video_name}/{duration}s/{preset}/{rendition.get_rendition_dir_representation()}'


@dataclass
class DecodingConfigDTO():
    scaling_resolution: Resolution
    framerate: int
    encoding_codec: str
    encoding_preset: str
    encoding_rendition: Rendition

    def get_output_dir(self, result_dir: str, video_name: str) -> str:
        """Returns the output path of the DecodingConfigDTO

        Parameters
        ----------
        result_dir : str
            root folder the rest of the path should be inserted in
        video_name : str
            video name that corresponds to the video getting decoded

        Returns
        -------
        str
            directory path of decoded video file
        """

        def rs(data: str) -> str:
            return data.removesuffix('/')
        
        output_sub_folders: list[str] = [
            rs(result_dir),
            self.encoding_codec,
            self.encoding_preset,
            self.encoding_rendition.get_rendition_dir_representation(),
            f'{self.framerate}fps',
            self.scaling_resolution.get_resolution_dir_representation(),
            video_name,
        ]
        
        output_dir_path: str = '/'.join(output_sub_folders)
        
        return output_dir_path
 

@dataclass
class DecodingConfig():
    '''Represents the configuration for the video decoding'''
    scaling_enabled: bool
    scaling_resolutions: list[Resolution]
    framerate: list[int] | None
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

    def get_decoding_dtos(self) -> list[DecodingConfigDTO]:
        decoding_dtos: list[DecodingConfigDTO] = list()

        for scale_resolution, framerate, encoding_codec, encoding_preset, encoding_rendition in itertools.product(
                self.scaling_resolutions,
                self.framerate,
                self.encoding_codecs,
                self.encoding_preset,
                self.encoding_renditions
        ):
            dto = DecodingConfigDTO(
                scale_resolution, framerate, encoding_codec, encoding_preset, encoding_rendition)
            decoding_dtos.append(dto)

        return decoding_dtos


if __name__ == '__main__':
    # ec = EncodingConfig.from_file(
    #     '../benchmark/config_files/test_encoding_config.yaml')

    # for dto in ec.get_encoding_dtos():
    #     print(dto.get_output_directory(video_name='test'))

    config = read_yaml('../benchmark/config_files/test_decoding_config.yaml')
    
    dc = DecodingConfig.from_dict(config)
    print(dc)
    
    for dto in dc.get_decoding_dtos():
        print(dto.get_output_dir('RESULT', 'VIDEO_NAME'))
        break
