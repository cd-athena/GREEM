from enum import Enum
from gaia.utils.config import Rendition

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
        if self.value == 'h264':
            return 'h264_nvenc' if cuda_mode else 'libx264'
        if self.value == 'h265':
            return 'hevc_nvenc' if cuda_mode else 'libx265'
        if self.value == 'av1':
            return 'libsvtav1'
        if self.value == 'vp9':
            return 'libvpx-vp9'
        if self.value == 'vvc':
            return 'vvc'
            
        return ''

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

    ) -> list[str]:
        pass
