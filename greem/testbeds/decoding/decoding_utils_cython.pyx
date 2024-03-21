import os
# import cython

# import libcpp

# from libcpp cimport bool


from greem.utility.config import DecodingConfigDTO

cdef str INPUT_FILE_DIR = '../encoding/results'
# cdef str INPUT_FILE_DIR = '../encoding/tmp'

def is_video(str file_name) -> bool:
    cdef bint file_is_video
    
    file_is_video = file_name is not None and \
        len(file_name) > 0 and \
        not file_name.endswith('.csv') and \
        not file_name.endswith('.txt')

    return file_is_video

def get_all_possible_video_files() -> list[str]:
    
    cdef list[str] input_files = list()
    
    for root, _, files in os.walk(INPUT_FILE_DIR):
            
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if is_video(file_path):
                input_files.append(file_path)  
            
    return input_files


def get_input_files(decoding_dto: DecodingConfigDTO, list[str] all_video_files) -> list[str]:    
    cdef list[str] input_files = list()
    
    for video_file in all_video_files:
        if f'{decoding_dto.encoding_codec}' in video_file and \
            f'{decoding_dto.encoding_preset}' in video_file and \
            f'{decoding_dto.encoding_rendition.get_rendition_dir_representation()}' in video_file and \
            f'{decoding_dto.framerate}fps' in video_file:
                
            input_files.append(video_file)         
        
    return sorted(input_files)