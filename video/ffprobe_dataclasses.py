from dataclasses import dataclass, field
import subprocess
import json
from typing import Type
from dacite import from_dict as fd


@dataclass
class VideoTagsFFP():

    major_brand: str
    minor_version: str
    compatible_brands: str
    encoder: str


@dataclass
class VideoFormatFFP():

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
    tags: VideoTagsFFP


@dataclass
class StreamDispositionFFP():

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
class StreamTagsFFP():

    language: str
    handler_name: str
    vendor_id: str
    encoder: str


@dataclass
class BaseStream():

    avg_frame_rate: str
    r_frame_rate: str
    disposition: StreamDispositionFFP
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
    tags: dict
    codec_name: str
    duration: str
    bit_rate: str
    profile: str
    id: str
    index: int

    @classmethod
    def from_dict(cls: Type['BaseStream'], data: dict):
        print('width' in data.keys())
        if 'width' in data.keys():
            return fd(data_class=VideoStreamFFP, data=data)
        elif 'channel_layout' in data.keys():
            return fd(data_class=AudioStreamFFP, data=data)
        return fd(data_class=BaseStream, data=data)


@dataclass
class VideoStreamFFP(BaseStream):

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
class AudioStreamFFP(BaseStream):

    channel_layout: str
    initial_padding: int
    bits_per_sample: int
    channels: int
    sample_fmt: str
    sample_rate: str


@dataclass
class VideoMetadataFFP():

    streams: list[VideoStreamFFP | AudioStreamFFP]
    format: VideoFormatFFP

    @classmethod
    def from_dict(cls: Type['VideoMetadataFFP'], data: dict) -> Type['VideoMetadataFFP']:
        vm: VideoMetadataFFP = fd(data_class=VideoMetadataFFP, data=data)
        return vm

    @classmethod
    def from_file(cls: Type['VideoMetadataFFP'], file_path: str) -> Type['VideoMetadataFFP']:
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
            VideoMetadataFFP.__convert_pipe_output_to_dict(output)
        )

    @staticmethod
    def __convert_pipe_output_to_dict(pipe_output: str) -> dict:
        if len(pipe_output) > 0:
            return json.loads(pipe_output)
        else:
            return dict()
        
    def get_video_streams(self) -> list[VideoStreamFFP]:
        return [stream for stream in self.streams if isinstance(stream, VideoStreamFFP)]
    
    def get_audio_streams(self) -> list[VideoStreamFFP]:
        return [stream for stream in self.streams if isinstance(stream, AudioStreamFFP)]


if __name__ == '__main__':
    vm = VideoMetadataFFP.from_file('../data/AncientThought.mp4')
    print(vm.streams)