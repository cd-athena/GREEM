import os
from math import ceil

from pydantic import BaseModel

from gaia.video.video_info import VideoInfo

from gaia.utils.configuration_classes import Rendition, EncodingConfig, EncodingConfigDTO
# https://www.streamingmedia.com/Articles/ReadArticle.aspx?ArticleID=157714

QUIET_FLAG: str = '-hide_banner -loglevel error'
CUDA_ENC_FLAG: str = '-hwaccel cuda'
CUDA_DEC_FLAG: str = '-hwaccel cuvid'


def get_join_string(pretty_print: bool) -> str:
    return ' \n' if pretty_print else ' '


def get_lib_codec(value: str, cuda_mode: bool = False) -> str:
    '''Returns the codec for the ffmpeg command'''
    value = value.lower()
    if value in ['h264', 'avc']:
        return 'h264_nvenc' if cuda_mode else 'libx264'
    elif value in ['h265', 'hevc']:
        return 'hevc_nvenc' if cuda_mode else 'libx265'
    elif value in ['av1']:
        return 'libsvtav1'
    elif value in ['vp9']:
        return 'libvpx-vp9'
    elif value in ['vvc']:
        return 'vvc'
    else:
        raise ValueError('Provided codec value not supported')


def get_representation_ffmpeg_flags(
    renditions: list[Rendition],
    preset: str,
    codec: str,
    fps: str = '',
) -> list[str]:
    '''Returns the ffmpeg flags for the renditions'''
    representations: list[str] = []

    fps_repr: str = '' if len(fps) == 0 else f',fps={fps}'

    for idx, rendition in enumerate(renditions):
        bitrate = rendition.bitrate
        height = rendition.height
        width = rendition.width
        representation: list[str] = [
            f'-b:v:{idx} {bitrate}k',
            f'-b:v:{idx} {bitrate}k -minrate {bitrate}k -maxrate {
                bitrate}k -bufsize {3*int(bitrate)}k',
            f'-c:v:{idx} {get_lib_codec(codec)} -filter:v:{idx}',
            f'"scale={width}:{height} {fps_repr}"',
            f'-preset {preset}'
        ]

        representations.extend(representation)

    return representations


def create_sequential_encoding_cmd(
    input_file_path: str,
    input_file_name: str,
    output_dir_path: str,
    encoding_dto: EncodingConfigDTO,
    constant_rate_factor: int = -1,
    cuda_enabled: bool = False,
    quiet_mode: bool = False,
) -> str:
    codec_processing = CodecProcessing(
        cuda_encoding=cuda_enabled, quiet_mode=quiet_mode)

    return codec_processing.create_sequential_encoding_cmd(
        input_file_path=input_file_path,
        input_file_name=input_file_name,
        output_dir_path=output_dir_path,
        dto=encoding_dto,
        constant_rate_factor=constant_rate_factor
    )


# def create_ffmpeg_encoding_command(
#     input_file_path: str,
#     output_dir: str,
#     rendition: Rendition,
#     preset: str,
#     segment_duration: int,
#     codec: str,
#     framerate: int = 0,
#     constant_rate_factor: int = -1,
#     use_dash: bool = False,
#     cuda_enabled: bool = False,
#     quiet_mode: bool = False,
#     pretty_print: bool = False
# ) -> str:
#     '''Creates the ffmpeg command for encoding a video file'''
#     cmd: list[str] = ['ffmpeg -y']
#     if cuda_enabled:
#         cmd.append(CUDA_ENC_FLAG)
#     if quiet_mode:
#         cmd.append(QUIET_FLAG)

#     cmd.append(f'-re -i {input_file_path}')

#     if constant_rate_factor > -1:
#         cmd.append(f'-crf {constant_rate_factor}')

#     fps_str: str = ''
#     if framerate > 0:
#         fps_str = str(framerate)  # type: ignore

#     cmd.extend(get_representation_ffmpeg_flags(
#         [rendition], preset, codec, fps=fps_str))

#     fps: int = ceil(VideoInfo(input_file_path).get_fps()
#                     ) if framerate is None or framerate == 0 else framerate
#     keyframe: int = fps * segment_duration

#     cmd.extend([
#         f'-keyint_min {keyframe}',
#         f'-g {keyframe}',
#     ])

#     if use_dash:
#         cmd.extend([
#             f'-seg_duration {segment_duration}',
#             '-adaptation_sets "id=0,streams=v  id=1,streams=a"',
#             f'-f dash {output_dir}/manifest.mpd'
#         ])
#     else:
#         cmd.extend([
#             f'{output_dir}/output.mp4'
#         ])

#     join_string: str = ' \n' if pretty_print else ' '

#     return join_string.join(cmd)

def create_dash_ffmpeg_cmd(
    input_file_path: str,
    output_dir: str,
    renditions: list[Rendition],
    preset: str,
    codec: str,
    segment_seconds: int = 4,
    pretty_print: bool = False
) -> str:
    """Creates dash ffmpeg command with the provided parameters

    Parameters
    ----------
    input_file_path : str
        the input file to process
    output_dir : str
        output directory the processed video file will be stored
    renditions : list[Rendition]
        the renditions included in the process
    preset : str
        the preset what will be used
    codec : str
        the codec used for video processing
    segment_seconds : int, optional
        the length in seconds of each dash segment, by default 4
    pretty_print : bool, optional
        more readable cmd string formatting for debugging (Note, will not be executable), by default False

    Returns
    -------
    str
        ffmpeg command for DASH segments
    """

    cmd: list[str] = [
        'ffmpeg', f'-re -i {input_file_path}',
    ]

    cmd.extend(get_representation_ffmpeg_flags(renditions, preset, codec))
    fps: int = ceil(VideoInfo(input_file_path).get_fps())
    keyframe: int = fps * segment_seconds

    cmd.extend([
        f'-keyint_min {keyframe}',
        f'-g {keyframe}',
        f'-seg_duration {segment_seconds}',
        f'-init_seg_name "{output_dir}/\$RepresentationID\$/init.\$ext\$"',
        f'-media_seg_name "{output_dir}/\$RepresentationID\$/seg-\$Number%05d\$.\$ext\$"',
        '-adaptation_sets "id=0,streams=v  id=1,streams=a"',
        f'-f dash {output_dir}/manifest.mpd'
    ])

    join_string: str = ' \n' if pretty_print else ' '

    return join_string.join(cmd)


def create_simple_multi_video_ffmpeg_command(
    video_input_file_paths: list[str],
    output_directories: list[str],
    renditions: list[Rendition],
    preset: str,
    codec: str,
    segment_seconds: int = 4,
    cuda_mode: bool = False,
    quiet_mode: bool = False,
    pretty_print: bool = False
) -> str:
    cmd: list[str] = [
        'ffmpeg', '-y',
    ]

    if cuda_mode:
        cmd.append(CUDA_ENC_FLAG)

    if quiet_mode:
        cmd.append(QUIET_FLAG)

    # add all input videos
    cmd.extend([f'-i {video}' for video in video_input_file_paths])

    for idx in range(len(video_input_file_paths)):
        # map_cmd = f'-map {idx} -c:v mpeg4 -q:v 1 -seg_duration 4 -f dash {output_directories[idx]}/{idx}/video{idx}.mpd'
        # cmd.append(map_cmd)
        map_cmd: list[str] = [
            f'-map {idx}',
            f'-c:v {get_lib_codec(codec, cuda_mode=cuda_mode)}',
            '-q:v 1',
            # f'-seg_duration {segment_seconds}',

            # TODO probably add resolution etc here.
            # get_representation_ffmpeg_flags(renditions, preset, codec),
        ]

        cmd.extend(map_cmd)

        # cmd.extend(get_representation_ffmpeg_flags(renditions, preset, codec, is_multi_video=False))

        cmd.extend([
            f'{output_directories[idx]}/output.mp4'
        ])

    join_string: str = ' \n' if pretty_print else ' '

    return join_string.join(cmd)


def create_multi_video_ffmpeg_command(
    video_input_file_paths: list[str],
    output_directories: list[str],
    dto: EncodingConfigDTO,
    segment_seconds: int = 4,
    cuda_mode: bool = False,
    quiet_mode: bool = False,
    pretty_print: bool = False,
    output_file_name: str = 'output.mp4'
) -> str:
    cmd: list[str] = [
        'ffmpeg', '-y',
        '-hide_banner',
    ]

    if quiet_mode:
        cmd.append(QUIET_FLAG)

    # add all input videos
    if cuda_mode:
        cmd.extend(
            [f'{CUDA_ENC_FLAG} -i {video}' for video in video_input_file_paths])
    else:
        cmd.extend([f'-i {video}' for video in video_input_file_paths])

    bitrate = int(dto.rendition.bitrate)
    # TODO take a look into how to integrate FPS to the encoding
    # fps_repr: str = '' if dto.framerate == 0 else f'fps={dto.framerate}'

    for idx in range(len(video_input_file_paths)):
        map_cmd: list[str] = [
            f'-map {idx}:0',
            f'-c:v {get_lib_codec(dto.codec, cuda_mode)} -preset {dto.preset}',
            f'-minrate {bitrate}k -maxrate {bitrate}k -bufsize {5*bitrate}k',

            f'-vf "scale={dto.rendition.get_resolution_dir_representation()}"',

            # f'-seg_duration {segment_seconds}',
        ]

        cmd.extend(map_cmd)
        cmd.extend([
            f'{output_directories[idx]}/{output_file_name}'
        ])

    join_string: str = ' \n' if pretty_print else ' '
    return join_string.join(cmd)


def get_slice_video_command(
    input_video_path: str,
    output_path: str,
    output_file_name: str,
    segment_duration: int,
) -> str:
    '''https://unix.stackexchange.com/questions/1670/how-can-i-use-ffmpeg-to-split-mpeg-video-into-10-minute-chunks'''
    duration: str = f'{segment_duration}' if segment_duration > 9 else f'0{
        segment_duration}'

    cmd: list[str] = [
        'ffmpeg -n',
        f'-i {input_video_path}',
        # '-vcodec copy',
        # '-c copy',
        '-map 0',
        '-strict -2',
        '-async 1',
        '-f segment',
        f'-segment_time 00:00:{duration}',
        '-reset_timestamps 1',

        f'{output_path}/{output_file_name}_{segment_duration}s_\%02d.mp4'
    ]

    return ' '.join(cmd)


def get_slice_video_commands(
    input_video_path: str,
    output_path: str,
    output_file_name: str,
    segment_duration: int,
) -> list[str]:
    '''
    - https://unix.stackexchange.com/questions/1670/how-can-i-use-ffmpeg-to-split-mpeg-video-into-10-minute-chunks
    - https://stackoverflow.com/questions/18444194/cutting-the-videos-based-on-start-and-end-time-using-ffmpeg
    '''
    video_info = VideoInfo(input_video_path)
    max_duration = int(video_info.get_total_duration_in_sec())
    cmd_list: list[str] = []

    for start_segment in range(0, int(max_duration), segment_duration):
        end_segment = start_segment + segment_duration
        end_segment = end_segment if end_segment < max_duration else max_duration

        cmd: list[str] = [
            'ffmpeg -n',
            '-loglevel error',
            f'-i {input_video_path}',
            f'-ss {start_segment}',
            f'-to {end_segment}',
            '-map 0',
            '-strict -2',
            '-async 1',
            '-reset_timestamps 1',
            f'{output_path}/{output_file_name}_{segment_duration}s_{start_segment //
                                                                    segment_duration}.mp4'
        ]

        cmd_list.append(' '.join(cmd))

    return cmd_list


def get_video_without_extension(video: str) -> str:
    return video.removesuffix('.webm').removesuffix('.mp4').removesuffix('.265')


def prepare_sliced_videos(
    encoding_configs: list[EncodingConfig],
    input_dir: str,
    output_dir: str,
    dry_run: bool = False
) -> None:

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    videos: set[str] = set()
    durations: set[int] = set()

    for config in encoding_configs:

        if config.encode_all_videos:
            videos.update([get_video_without_extension(file)
                          for file in os.listdir(input_dir)])
        else:
            videos.update(config.videos_to_encode)

        durations.update(config.segment_duration)

    input_files: list[str] = [
        file for file in os.listdir(input_dir) if get_video_without_extension(file) in videos
    ]
    output_files: list[str] = [
        get_video_without_extension(file) for file in input_files
    ]

    for duration in durations:
        for input_file, output_file in zip(input_files, output_files):

            cmd_list = get_slice_video_commands(
                f'{input_dir}/{input_file}',
                output_dir,
                output_file,
                duration
            )

            for cmd in cmd_list:
                if not dry_run:
                    os.system(cmd)
                else:
                    print(cmd)


class CodecProcessing(BaseModel):
    cuda_encoding: bool = False
    quiet_mode: bool = False

    @staticmethod
    def is_codec_supported(codec: str) -> bool:
        return codec in [
            'h264',
            'avc',
            'h265',
            'hevc',
            # 'av1',
            # 'vp9',
            # 'vvc'
        ]

    def create_sequential_encoding_cmd(
            self,
            input_file_path: str,
            input_file_name: str,
            output_dir_path: str,
            dto: EncodingConfigDTO,
            constant_rate_factor: int = -1,
    ) -> str:
        if not CodecProcessing.is_codec_supported(dto.codec):
            raise AssertionError('Codec is not supported')

        cmd: list[str] = ['ffmpeg -y']

        if self.cuda_encoding:
            cmd.append(CUDA_ENC_FLAG)
        if self.quiet_mode:
            cmd.append(QUIET_FLAG)

        cmd.append(f"-re -i {input_file_path}")

        # TODO the code for each codec here
        if dto.codec in ['avc', 'h264', 'hevc', 'h265']:
            cmd.extend(self.h26x_sequential_encoding_cmd(
                input_file_name, dto, constant_rate_factor))
        if dto.codec in ['av1']:
            raise NotImplementedError('AV1 codec is not implemented yet')
        if dto.codec in ['vp9']:
            raise NotImplementedError('VP9 codec is not implemented yet')
        if dto.codec in ['vvc']:
            raise NotImplementedError('VVC codec is not implemented yet')
            # cmd.extend(self.vvc_sequential_encoding_cmd(dto))

        cmd.append(
            f'{output_dir_path}/{dto.get_output_directory()}/{input_file_name}.mp4')

        join_string = get_join_string(False)
        return join_string.join(cmd)

    def h26x_sequential_encoding_cmd(self,
                                     input_file_path: str,
                                     dto: EncodingConfigDTO,
                                     constant_rate_factor: int
                                     ) -> list[str]:
        cmd: list[str] = []

        if constant_rate_factor > -1:
            cmd.append(f"-crf {constant_rate_factor}")

        fps_str: str = ""
        if dto.framerate > 0:
            fps_str = str(dto.framerate)  # type: ignore

        cmd.extend(get_representation_ffmpeg_flags(
            [dto.rendition], dto.preset, dto.codec, fps=fps_str))

        fps: int = (
            ceil(VideoInfo(input_file_path).get_fps())
            if dto.framerate is None or dto.framerate == 0
            else dto.framerate
        )
        keyframe: int = fps * dto.segment_duration

        cmd.extend(
            [
                f"-keyint_min {keyframe}",
                f"-g {keyframe}",
            ]
        )
        return cmd

    def av1_sequential_encoding_cmd(self, dto: EncodingConfigDTO) -> list[str]:
        pass

    def vvc_sequential_encoding_cmd(self,
                                    dto: EncodingConfigDTO,
                                    ) -> list[str]:
        cmd: list[str] = [
            '-vcodec omx_enc_vvc',
            # '-vcodec vvc',
            f'-b:v {dto.rendition.bitrate}',
            f'-period {dto.segment_duration}',  # GOP in seconds
            f'-preset {dto.preset}',
        ]

        return cmd
