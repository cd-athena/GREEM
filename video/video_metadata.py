from dataclasses import dataclass, field
import subprocess
import json
from typing import Type
from dacite import from_dict as fd


@dataclass
class VideoFormatTags():

    major_brand: str
    minor_version: str
    compatible_brands: str
    encoder: str


@dataclass
class VideoFormat():

    filename: str
    nb_streams: int
    nb_programs: int
    format_name: str
    format_long_name: str
    start_time: str
    duration: str
    size: str
    bit_rate: str
    probe_score: int
    tags: VideoFormatTags


@dataclass
class StreamDisposition():

    default: int
    dub: int
    original: int
    comment: int
    lyrics: int
    karaoke: int
    forced: int
    hearing_impaired: int
    visual_impaired: int
    clean_effects: int
    attached_pic: int
    timed_thumbnails: int
    captions: int
    descriptions: int
    metadata: int
    dependent: int
    still_image: int


@dataclass
class StreamTags():

    language: str
    handler_name: str
    vendor_id: str


@dataclass
class VideoStreamTags(StreamTags):

    encoder: str


@dataclass
class BaseStream():
    """Base Stream class that is the parent class for both video and audio streaming format"""

    avg_frame_rate: str
    r_frame_rate: str
    disposition: StreamDisposition
    extradata_size: int
    codec_long_name: str
    start_time: str
    time_base: str
    codec_type: str
    codec_tag_string: str
    codec_tag: str
    duration_ts: int
    start_pts: int
    nb_frames: str
    tags: VideoStreamTags | StreamTags
    codec_name: str
    duration: str
    bit_rate: str
    profile: str
    id: str
    index: int
    average_fps: float = field(init=False)

    @classmethod
    def from_dict(cls: Type['BaseStream'], data: dict):
        print('width' in data.keys())
        if 'width' in data.keys():
            return fd(data_class=VideoStream, data=data)
        elif 'channel_layout' in data.keys():
            return fd(data_class=AudioStream, data=data)
        return fd(data_class=BaseStream, data=data)
    
    def __post_init__(self):
        avg_fps = self.avg_frame_rate.split('/')[0]
        self.average_fps = float(avg_fps) / 1000


@dataclass
class VideoStream(BaseStream):

    width: int
    height: int
    coded_width: int
    coded_height: int
    closed_captions: int
    film_grain: int
    has_b_frames: int
    sample_aspect_ratio: str
    display_aspect_ratio: str
    pix_fmt: str
    level: int
    color_range: str
    color_space: str
    color_transfer: str
    color_primaries: str
    chroma_location: str
    field_order: str
    refs: int
    is_avc: str
    nal_length_size: str
    start_pts: int
    bits_per_raw_sample: str


@dataclass
class AudioStream(BaseStream):

    channel_layout: str
    initial_padding: int
    bits_per_sample: int
    channels: int
    sample_fmt: str
    sample_rate: str


@dataclass
class VideoMetadata():

    streams: list[VideoStream | AudioStream]
    format: VideoFormat

    @classmethod
    def from_dict(cls: Type['VideoMetadata'], data: dict) -> Type['VideoMetadata']:
        vm: VideoMetadata = fd(data_class=VideoMetadata, data=data)
        return vm

    @classmethod
    def from_file(cls: Type['VideoMetadata'], file_path: str) -> Type['VideoMetadata']:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format', '-show_streams',
            file_path,
        ]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, universal_newlines=True)
        output, _ = p.communicate()

        return cls.from_dict(
            VideoMetadata.__convert_pipe_output_to_dict(output)
        )

    @staticmethod
    def __convert_pipe_output_to_dict(pipe_output: str) -> dict:
        if len(pipe_output) > 0:
            return json.loads(pipe_output)
        else:
            return dict()

    def get_video_streams(self) -> list[VideoStream]:
        return [stream for stream in self.streams if isinstance(stream, VideoStream)]

    def get_audio_streams(self) -> list[VideoStream]:
        return [stream for stream in self.streams if isinstance(stream, AudioStream)]


if __name__ == '__main__':
    vm = VideoMetadata.from_file('../data/Eldorado.mp4')
    # print(vm.streams)
    # print(vm)
    print(vm)
