"""
Module for managing video encoding and decoding configurations.

This module defines classes and functions to handle various configurations and 
operations related to video encoding and decoding, including reading from YAML files, 
representing resolutions and renditions, and generating encoding and decoding DTOs.

Classes:
    EncodingVariant: Enum representing encoding variants (SEQUENTIAL, BATCH).
    Resolution: Pydantic BaseModel representing a video resolution.
    Rendition: Pydantic BaseModel representing a video rendition, inheriting from Resolution.
    EncodingConfigDTO: Pydantic BaseModel representing a single encoding configuration.
    EncodingConfig: Pydantic BaseModel representing the configuration for video encoding.
    DecodingConfigDTO: Dataclass representing the configuration for video decoding.
    DecodingConfig: Pydantic BaseModel representing the configuration for video decoding.

Functions:
    read_yaml(file_path: str) -> dict:
        Reads a YAML file and returns its contents as a Python dictionary.
"""
import itertools

from dataclasses import dataclass
from typing import Type
from enum import Enum
import yaml

from pydantic import BaseModel


class EncodingVariant(Enum):
    '''EncodingVariant: Enum representing encoding variants (SEQUENTIAL, BATCH).'''
    SEQUENTIAL = 1
    BATCH = 2

# Sources:
# * https://stackoverflow.com/questions/51286748/make-the-python-json-encoder-support-pythons-new-dataclasses

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
        """Creates a string representing the directory path of the instance.

        Example:
        `Resolution(1080, 1920)` is represented as a String `1920x1080`

        Returns
        -------
        str
            Returns the `Resolution` instance as a string representing the directory path
        """
        return f'{self.width}x{self.height}'


class Rendition(Resolution):
    '''Represents a rendition of a video file

    Example:
    `Rendition(1080, 1920, 8100)` represents a rendition with a height of 1080,
    a width of 1920 and a bitrate of 8100 kilobyte
    '''
    bitrate: int

    def get_rendition_dir_representation(self) -> str:
        """Creates a string representing the directory path of the instance.

        Example:
        `Rendition(1080, 1920, 8100)` is represented as a String `8100k_1920x1080`

        Returns
        -------
        str
            Returns the `Rendition` instance as a string representing the directory path
        """
        return f'{self.bitrate}k_{self.get_resolution_dir_representation()}'

    @classmethod
    def from_dir_representation(cls: Type['Rendition'], dir_repr: str) -> "Rendition":
        """
        Creates a Rendition object from a directory representation string.

        Args:
            dir_repr (str): The directory representation string in the format 'bitrate_resolution',
                            e.g., '800k_1920x1080'. If the string contains '/', only the part after the last '/' is used.

        Returns:
            Rendition: An instance of Rendition created from the directory representation.

        Examples:
            >>> Rendition.from_dir_representation('800k_1920x1080')
            Rendition(bitrate=800, height=1080, width=1920)

            >>> Rendition.from_dir_representation('/path/to/800k_1920x1080')
            Rendition(bitrate=800, height=1080, width=1920)
        """
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
    def new(cls: Type['Rendition']) -> "Rendition":
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
    """
    Data type object consisting of one encoding configuration.

    Attributes:
        codec(str): The codec to be used for encoding the video.
        preset(str): The encoding preset to be applied.
        rendition(Rendition): The rendition to be used during encoding.
        segment_duration(int): The segment duration for encoding. Defaults to 4.
        framerate(int): The frame rate to be used during encoding. Defaults to 0.
        is_dash(bool): Flag indicating if DASH(Dynamic Adaptive Streaming over HTTP) is used. Defaults to False.

    Methods:
        get_output_directory(self) -> str:
            Returns the output directory for the encoded video.
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

        if self.framerate is not None and self.framerate > 0:
            output_dir = f'{output_dir}/{self.framerate}fps'

        return output_dir


class EncodingConfig(BaseModel):
    """
    Represents the configuration for video encoding.

    Attributes:
        codecs(list[str]): List of codecs to be used for encoding videos.
        presets(list[str]): List of encoding presets to be applied.
        renditions(list[Rendition]): List of renditions to be used during encoding.
        segment_duration(list[int]): List of segment durations for encoding.
        framerate(list[int]): List of frame rates to be used during encoding.
        is_dash(bool): Flag indicating if DASH(Dynamic Adaptive Streaming over HTTP) is used. Defaults to False.

    Methods:
        from_file(cls, file_path: str) -> 'EncodingConfig':
            Creates an EncodingConfig object from a YAML file.

        get_all_result_directories(self) -> list[str]:
            Returns a list of all possible result directories.

        get_encoding_dtos(self) -> list[EncodingConfigDTO]:
            Creates a combination of all values provided in the encoding configuration file and
            returns a list consisting of EncodingConfigDTOs.
    """
    codecs: list[str]
    presets: list[str]
    renditions: list[Rendition]
    segment_duration: list[int]
    framerate: list[int]
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
        """Creates a combination of all values provided in the encoding configuration file and
        returns a list consisting of `EncodingConfigDTO`s

        Returns
        -------
        list[EncodingConfigDTO]
            A list consisting of all possible combinations of the provided configuration file
        """
        encoding_dtos: list[EncodingConfigDTO] = []

        segment_duration: list[int] = self.segment_duration if self.is_dash else [
            4]

        for duration, preset, rendition, codec, fr in itertools.product(
                segment_duration,
                self.presets, self.renditions, self.codecs,
                self.framerate if self.framerate is not None and len(self.framerate) > 0 else []):

            enc_dto = EncodingConfigDTO(
                codec=codec,
                preset=preset,
                rendition=rendition,
                segment_duration=duration,
                framerate=fr,
                is_dash=self.is_dash
            )
            encoding_dtos.append(enc_dto)

        return encoding_dtos


@dataclass
class DecodingConfigDTO():
    """
    Represents the configuration for video decoding.

    Attributes:
        scaling_resolution(Resolution): The resolution to which the video is scaled.
        framerate(int): The frame rate to be used during video decoding.
        encoding_codec(str): A filter to only decode videos encoded with a given video codec.
        encoding_preset(str): A filter to only decode videos encoded with a given video preset.
        encoding_rendition(Rendition): A filter to only decode videos encoded with a given video rendition.
    """
    scaling_resolution: Resolution
    framerate: int
    encoding_codec: str
    encoding_preset: str
    encoding_rendition: Rendition

    def get_output_dir(self, result_dir: str, video_name: str) -> str:
        """Returns the output path of the DecodingConfigDTO

        Parameters
        ----------
        result_dir: str
            root folder the rest of the path should be inserted in
        video_name: str
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
    """
    Represents the configuration for video decoding.

    Attributes:
        scaling_enabled(bool): Indicates if scaling is enabled for video decoding.
        scaling_resolutions(list[Resolution]): List of resolutions to which videos can be scaled.
        framerate(list[int]): List of frame rates to be used during video decoding.
        decoding_sleep(float): Sleep time in seconds between decoding operations.
        decode_all_videos(bool): Flag indicating whether to decode all videos or not .
        encoding_codecs(list[str]): List of codecs to be used for encoding videos after decoding.
        encoding_preset(list[str]): List of encoding presets to be applied during encoding.
        encoding_renditions(list[Rendition]): List of renditions to be used during encoding.
    """
    scaling_enabled: bool
    scaling_resolutions: list[Resolution]
    framerate: list[int]
    decoding_sleep: float
    decode_all_videos: bool
    encoding_codecs: list[str]
    encoding_preset: list[str]
    encoding_renditions: list[Rendition]

    @classmethod
    def from_file(cls: Type['DecodingConfig'], file_path: str) -> "DecodingConfig":
        '''Creates a DecodingConfig object from a YAML file'''
        yaml_file = read_yaml(file_path)
        return cls(**yaml_file)

    def get_decoding_dtos(self) -> list[DecodingConfigDTO]:
        """Creates a combination of all values provided in the encoding configuration file and
        returns a list consisting of `DecodingConfigDTO`s

        Returns
        -------
        list[DecodingConfigDTO]
            A list consisting of all possible combinations of the provided configuration file
        """
        decoding_dtos: list[DecodingConfigDTO] = []

        for scale_res, fps, enc_codec, enc_preset, enc_rendition in itertools.product(
                self.scaling_resolutions,
                self.framerate,
                self.encoding_codecs,
                self.encoding_preset,
                self.encoding_renditions
        ):
            dto = DecodingConfigDTO(
                scale_res, fps, enc_codec, enc_preset, enc_rendition)
            decoding_dtos.append(dto)

        return decoding_dtos
