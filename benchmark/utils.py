import sys
sys.path.append("..")

from utils.config import EncodingConfig

def prepare_data_directories(
    encoding_config: EncodingConfig,
    result_root: str,
    video_names: list[str]
) -> list[str]:
    '''Generate all directories that are used for the video encoding

    Returns:
        list[str]: returns a list of all directories that were created
    '''
    data_directories = encoding_config.get_all_result_directories(video_names)

    for directory in data_directories:
        directory_path: str = f'{result_root}/{directory}'
        Path(directory_path).mkdir(parents=True, exist_ok=True)
    return data_directories


def get_video_input_files(
    video_dir: str,
    encoding_config: EncodingConfig
) -> list[str]:
    input_files: list[str] = [file_name for file_name in os.listdir(
        video_dir) if encoding_config.encode_all_videos or file_name.split('.')[0] in encoding_config.videos_to_encode]

    if len(input_files) == 0:
        raise ValueError('no video files to encode')

    return input_files
