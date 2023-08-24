import sys
sys.path.append("..")

from monitoring.gpu_monitoring import GpuMonitoring
from utils.ffmpeg import create_ffmpeg_command_all_renditions
from utils.config import EncodingConfig, Rendition, EncodingVariant
from utils.timing import TimingMetadata, measure_time_of_system_cmd, IdleTimeEnergyMeasurement
from hardware.intel import intel_rapl_workaround
from encoding_utility import get_video_input_files, prepare_data_directories



ENCODING_CONFIG_PATHS: list[str] = [
    # 'config_files/encoding_test_1.yaml',
    # 'config_files/encoding_test_2.yaml',
    # 'config_files/default_encoding_config.yaml',
    'config_files/test_encoding_config.yaml',
    # 'config_files/encoding_config_h264.yaml',
    # 'config_files/encoding_config_h265.yaml'
]

INPUT_FILE_DIR: str = 'data'
RESULT_ROOT: str = 'batch_results'
COUNTRY_ISO_CODE: str = 'AUT'

DRY_RUN: bool = False  # if True, no encoding will be executed
INCLUDE_CODE_CARBON: bool = False


def execute_encoding_benchmark(encoding_configs: list[EncodingConfig], timing_metadata: dict[int, dict], encoding_variant: EncodingVariant):
    # TODO, think about a way to combine the benchmarks and use an enum to determine which is used

    for encoding_config in encoding_configs:
        input_files: list[str] = get_video_input_files(
            INPUT_FILE_DIR, encoding_config)
        
        encode(encoding_config, input_files, timing_metadata, encoding_variant)


def prepare_all_video_directories(encoding_configs: list[EncodingConfig], encoding_variant: EncodingVariant) -> None:
    for encoding_config in encoding_configs:
        video_files: list[str] = get_video_input_files(
            INPUT_FILE_DIR, encoding_config)

        prepare_data_directories(
            encoding_config, RESULT_ROOT, video_files, encoding_variant)


def encode(
        encoding_config: EncodingConfig,
        input_files: list[str],
        timing_metadata: dict[int, dict],
        encoding_variant: EncodingVariant
):

    if encoding_variant == EncodingVariant.BATCH:
        encode_batch(encoding_config, input_files, timing_metadata)

    elif encoding_variant == EncodingVariant.SEQUENTIAL:
        pass
    else:
        print('WTF??')


def encode_batch(
        encoding_config: EncodingConfig,
        input_files: list[str],
        timing_metadata: dict[int, dict],
) -> None:
    global gpu_monitoring
    for segment_duration in encoding_config.segment_duration:
        for video in input_files:
            for codec in encoding_config.codecs:
                for preset in encoding_config.presets:

                    input_file_path: str = f'{INPUT_FILE_DIR}/{video}'
                    if any([x in video for x in ['.webm', '.mp4']]):
                        video_name = video.removesuffix(
                            '.webm').removesuffix('.mp4')

                    gpu_monitoring.current_video = video_name
                    output_dir: str = f'{RESULT_ROOT}/{codec}/{video_name}/{segment_duration}s/{preset}'

                    cmd = create_ffmpeg_command_all_renditions(
                        input_file_path,
                        output_dir,
                        encoding_config.renditions,
                        preset,
                        codec,
                        segment_duration,
                        pretty_print=DRY_RUN
                    )

                    gpu_monitoring.start()
                    start_time, end_time, elapsed_time = measure_time_of_system_cmd(
                        cmd)
                    gpu_monitoring.stop()
                    metadata = TimingMetadata(
                        start_time, end_time, elapsed_time, video_name, codec, preset, Rendition.get_batch_rendition(), segment_duration)
                    timing_metadata[len(
                        timing_metadata)] = metadata.to_dict()


def execute_batch_encoding(
        cmd: str,
        video_name: str,
        codec: str,
        preset: str,
        renditions: list[Rendition],
        duration: int,
        timing_metadata: dict[int, dict]
) -> None:
    pass


if __name__ == '__main__':
    intel_rapl_workaround()
    IdleTimeEnergyMeasurement.measure_idle_energy_consumption(
        result_path='encoding_idle_time.csv', idle_time_in_seconds=1)

    configs: list[EncodingConfig] = [EncodingConfig.from_file(
        file_path) for file_path in ENCODING_CONFIG_PATHS]
    timing_metadata: dict[int, dict] = dict()

    prepare_all_video_directories(configs, EncodingVariant.BATCH)
    gpu_monitoring = GpuMonitoring(RESULT_ROOT)
    execute_encoding_benchmark(configs, timing_metadata, EncodingVariant.BATCH)
