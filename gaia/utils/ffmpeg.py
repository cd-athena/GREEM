from math import ceil

from gaia.video.video_info import VideoInfo

from gaia.utils.config import Rendition
from gaia.utils.benchmark import BenchmarkParser


cli_parser = BenchmarkParser()


def get_lib_codec(codec: str) -> str:
    '''Returns the codec for the ffmpeg command'''
    if codec == 'h264':
        return 'libx264'
    elif codec == 'h265':
        return 'libx265'
    else:
        raise ValueError('Provided codec value not supported')


def get_representation_ffmpeg_flags(renditions: list[Rendition], preset: str, codec: str) -> list[str]:
    '''Returns the ffmpeg flags for the renditions'''
    representations: list[str] = list()
    maps: list[str] = ['-map 0:v:0'] * len(renditions)
    representations.extend(maps)
    representations.append('-map 0:a:0')

    for idx, rendition in enumerate(renditions):
        bitrate = rendition.bitrate
        height = rendition.height
        width = rendition.width
        representation: list[str] = [
            f'-b:v:{idx} {bitrate}k -minrate {bitrate}k -maxrate {bitrate}k -bufsize {3*int(bitrate)}k',
            f'-c:v:{idx} {get_lib_codec(codec)} -filter:v:{idx} "scale={width}:{height}"',
            f'-preset {preset}'
        ]

        representations.extend(representation)

    return representations


def create_ffmpeg_encoding_command(
    input_file_path: str,
    output_dir: str,
    rendition: Rendition,
    preset: str,
    segment_duration: int,
    codec: str,
    pretty_print: bool = False
) -> str:
    '''Creates the ffmpeg command for encoding a video file'''
    cmd: list[str] = ['ffmpeg -y']
    if cli_parser.is_cuda_enabled():
        cmd.append(cli_parser.get_ffmpeg_cuda_flag())
    if cli_parser.is_quiet_ffmpeg():
        cmd.append(cli_parser.get_ffmpeg_quiet_flag())

    cmd.append(f'-re -i {input_file_path}')

    cmd.extend(get_representation_ffmpeg_flags([rendition], preset, codec))
    fps: int = ceil(VideoInfo(input_file_path).get_fps())
    keyframe: int = fps * segment_duration

    cmd.extend([
        f'-keyint_min {keyframe}',
        f'-g {keyframe}',
        f'-seg_duration {segment_duration}',
        '-adaptation_sets "id=0,streams=v  id=1,streams=a"',
        f'-f dash {output_dir}/manifest.mpd'
    ])

    join_string: str = ' \n' if pretty_print else ' '

    return join_string.join(cmd)


def create_ffmpeg_command_all_renditions(
    input_file_path: str,
    output_dir: str,
    renditions: list[Rendition],
    preset: str,
    codec: str,
    segment_seconds: int = 4,
    pretty_print: bool = False
) -> str:

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
        # '-init_seg_name "\$RepresentationID\$/init.\$ext\$"',
        # '-media_seg_name "\$RepresentationID\$/seg-\$Number%05d\$.\$ext\$"',
        '-adaptation_sets "id=0,streams=v  id=1,streams=a"',
        f'-f dash {output_dir}/manifest.mpd'
    ])

    join_string: str = ' \n' if pretty_print else ' '

    return join_string.join(cmd)

def create_multi_video_ffmpeg_command(
    video_input_file_paths: list[str],
    output_directories: list[str],
    renditions: list[Rendition],
    preset: str,
    codec: str,
    segment_seconds: int = 4,
    pretty_print: bool = False
) -> str:
    
    cmd: list[str] = [
        'ffmpeg', '-y'
    ]
    # add all input videos
    cmd.extend([f'-i {video}' for video in video_input_file_paths])
    
    for idx in range(len(video_input_file_paths)):
        # map_cmd = f'-map {idx} -c:v mpeg4 -q:v 1 -seg_duration 4 -f dash {output_directories[idx]}/{idx}/video{idx}.mpd'
        # cmd.append(map_cmd)
        map_cmd: list[str] = [
            f'-map {idx}',
            f'-c:v {codec}', '-q:v 1',
            f'-seg_duration {segment_seconds}',
            
            '-f dash',
            f'{output_directories}/manifest.mpd'
            
        ]
        
    
    join_string: str = ' \n' if pretty_print else ' '
    
    return join_string.join(cmd)



if __name__ == '__main__':
    print('')
    