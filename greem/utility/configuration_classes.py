import itertools
# Sources:
# * https://stackoverflow.com/questions/51286748/make-the-python-json-encoder-support-pythons-new-dataclasses

import yaml
from dacite import from_dict as fd
from dataclasses import dataclass
from typing import Type, Optional
from enum import Enum

from pydantic import BaseModel


class EncodingVariant(Enum):
    SEQUENTIAL = 1
    BATCH = 2


def read_yaml(file_path: str) -> dict:
    '''Reads a YAML file and returns a Python dictionary'''
    with open(file_path, 'r', encoding='utf-8') as stream:
        try:
            yaml_file = yaml.safe_load(stream)
            return yaml_file
        except yaml.YAMLError as err:
            print(err)
            return {}


class Resolution(BaseModel):
    '''Represents a resolution in the form of height x width

    Example: 1080x1920
    '''
    height: int
    width: int

    def get_resolution_dir_representation(self) -> str:
        return f'{self.width}x{self.height}'


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
            bitrate=int(bitrate),
            height=int(height),
            width=int(width)
        )

    @classmethod
    def new(cls: Type['Rendition']):
        """Returns a new Rendition instance with all values set to zero

        Returns
        -------
        Rendition
            Rendition(bitrate=0, height=0, width=0)
        """
        return cls(
            bitrate=int(0),
            height=int(0),
            width=int(0)
        )


class EncodingConfigDTO(BaseModel):
    """Data type object consisting of one encoding configuration

    Parameters
    ----------
    BaseModel : Pydantic.BaseModel
        Pydantic dataclass

    Returns
    -------
    `EncodingConfigDTO`
    """
    codec: str
    preset: str
    rendition: Rendition
    segment_duration: int = 4
    framerate: int = 0
    is_dash: bool = False

    def get_output_directory(
        self,
    ) -> str:
        '''Returns the output directory for the encoded video'''

        output_dir: str = f'{self.codec}/{self.preset}/{self.rendition.get_rendition_dir_representation()}'
        # use this folder structure if dash segments are created
        # output_dir: str = f'{self.codec}/{self.segment_duration}s/{self.preset}/{self.rendition.get_rendition_dir_representation()}'
        if self.framerate is not None and self.framerate > 0:
            output_dir = f'{output_dir}/{self.framerate}fps'

        return output_dir


class EncodingConfig(BaseModel):
    '''Represents the configuration for the video encoding'''
    codecs: list[str]
    presets: list[str]
    renditions: list[Rendition]
    segment_duration: list[int]
    framerate: list[int]
    encode_all_videos: bool
    videos_to_encode: Optional[list[str]]
    input_directory_path: list[str]
    is_dash: bool = False

    @classmethod
    def from_file(cls: Type['EncodingConfig'], file_path: str):
        '''Creates an EncodingConfig object from a YAML file'''
        yaml_file = read_yaml(file_path)
        return cls(**yaml_file)

    def get_all_result_directories(self) -> list[str]:
        '''Returns a list of all possible result directories'''
        directory_list: list[str] = [
            dto.get_output_directory()
            for dto in self.get_encoding_dtos()
        ]

        return directory_list

    def get_encoding_dtos(self) -> list[EncodingConfigDTO]:
        encoding_dtos: list[EncodingConfigDTO] = []

        segment_duration: list[int] = self.segment_duration if self.is_dash else [
            4]

        for duration, preset, rendition, codec, fr in itertools.product(
                segment_duration,
                self.presets, self.renditions, self.codecs,
                self.framerate if self.framerate is not None and len(self.framerate) > 0 else []):
            enc_dto = EncodingConfigDTO(
                codec=codec, preset=preset, rendition=rendition, segment_duration=duration, framerate=fr, is_dash=self.is_dash)
            encoding_dtos.append(enc_dto)

        return encoding_dtos

# TODO ParallelEncodingConfig classs-


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


class DecodingConfig(BaseModel):
    '''Represents the configuration for the video decoding'''
    scaling_enabled: bool
    scaling_resolutions: list[Resolution]
    framerate: list[int]
    decoding_sleep: float
    decode_all_videos: bool
    encoding_codecs: list[str]
    encoding_preset: list[str]
    encoding_renditions: list[Rendition]

    @classmethod
    def from_file(cls: Type['DecodingConfig'], file_path: str):
        '''Creates a DecodingConfig object from a YAML file'''
        yaml_file = read_yaml(file_path)
        return cls(**yaml_file)

    def get_decoding_dtos(self) -> list[DecodingConfigDTO]:
        decoding_dtos: list[DecodingConfigDTO] = []

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


@dataclass
class NtfyConfig():
    base_url: str = "<ip-addess>"

    @classmethod
    def from_dict(cls: Type['NtfyConfig'], data: dict):
        nc: NtfyConfig = fd(data_class=NtfyConfig, data=data)
        return nc

    @classmethod
    def from_file(cls: Type['NtfyConfig'], file_path: str):
        return cls.from_dict(read_yaml(file_path))
