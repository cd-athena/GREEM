from enum import Enum
from typing import Literal
from greem.utility.configuration_classes import Rendition

def get_lib_codec(value: str, cuda_mode: bool = False) -> str:
    '''Returns the codec for the ffmpeg command'''
    if value == 'h264':
        return 'h264_nvenc' if cuda_mode else 'libx264'
    if value == 'h265':
        return 'hevc_nvenc' if cuda_mode else 'libx265'
    if value == 'av1':
        return 'libsvtav1'
    if value == 'vp9':
        return 'libvpx-vp9'
    if value == 'vvc':
        return 'vvc'
        
    return ''

class Codecs(str, Enum):
    """Enum class providing supported video processing codecs.

    Returns
    -------
    Codecs Enum
        _description_
        
    Functions
    ---------
    
    get_lib_codec(self, cuda_mode) -> str
        returns the FFmpeg library as string of the instance


    """
    H264 = 'h264'
    H265 = 'h265'
    AVC = 'h264'
    HEVC = 'h265'
    AV1 = 'av1'
    VP9 = 'vp9'
    VVC = 'vvc'

    def get_lib_codec(self, cuda_mode: bool = False) -> str:
        '''Returns the codec for the ffmpeg command'''
        return get_lib_codec(self.value, cuda_mode)
    
    @staticmethod
    def get_enum_from_str(codec: str):
        if codec == 'h264':
            return Codecs.H264
        if codec == 'h265':
            return Codecs.H265
        if codec == 'av1':
            return Codecs.AV1
        if codec == 'vp9':
            return Codecs.VP9
        if codec == 'vvc':
            return Codecs.VVC
            
        return None
        

class FFmpeg():

    @staticmethod
    def create_cmd_all_renditions(
            input_file_path: str,
            output_dir: str,
    ):
        pass


    @classmethod
    def _get_representation_ffmpeg_flags(
            cls,
            renditions: list[Rendition],
            preset: str,
            codec: str,
    ) -> list[str]:
        representations: list[str] = []
        
        for idx, rendition in enumerate(renditions):
            bitrate = rendition.bitrate
            height = rendition.height
            width = rendition.width
            
            representation: list[str] = [
            f'-b:v:{idx} {bitrate}k',
            # f'-b:v:{idx} {bitrate}k -minrate {bitrate}k -maxrate {bitrate}k -bufsize {3*int(bitrate)}k',
            f'-c:v:{idx} {get_lib_codec(codec)} -filter:v:{idx}',
            f'"scale={width}:{height}"',
            # f'{fps_repr}"',
            f'-preset {preset}'
            ]
            
            representations.extend(representation)
        
        return representations
