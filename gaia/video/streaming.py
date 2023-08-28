import os
from dataclasses import dataclass, field
from gaia.utils.config import Rendition

@dataclass
class StreamingContainer:
    '''Represents a container for a streaming video'''
    directory_path: str
    video_stream: list[str] = field(init=False, repr=False, default_factory=list)
    audio_stream: list[str] = field(init=False, repr=False, default_factory=list)
    video_stream_channel: str = field(default='stream0')
    audio_stream_channel: str = field(default='stream1')
    num_of_streams: int = field(init=False, default=0)
    output_file_name: str = field(default='output')
    rendition: Rendition = field(init=False)
    encoding_preset: str = field(init=False)
    segment_length: str = field(init=False)
    video_name: str = field(init=False)
    encoding_codec: str = field(init=False)
    
    
    def __len__(self) -> int:
        return self.num_of_streams
    
    def __post_init__(self):
        streams: list[str] = [stream for stream in os.listdir(self.directory_path) if stream.endswith('.m4s')]
        self.__init_streams(streams)
        self.__init_metadata()
    
    
    def __init_streams(self, streams: list[str]) -> None:
        for stream in streams:
            if self.video_stream_channel in stream:
                self.video_stream.append(stream)
            elif self.audio_stream_channel in stream:
                self.audio_stream.append(stream)
                
        self.video_stream = sorted(self.video_stream)
        self.audio_stream = sorted(self.audio_stream)
        
        assert len(self.video_stream) > 0, 'video stream chunk list must not be empty'
        assert len(self.audio_stream) > 0, 'audio stream chunk list must not be empty'
        
        # init files are the last element in list, pop them to insert them in front
        video_init: str = self.video_stream.pop()
        audio_init: str = self.audio_stream.pop()
        self.video_stream.insert(0, video_init)
        self.audio_stream.insert(0, audio_init)
        
    def __init_metadata(self) -> None:
        self.num_of_streams = len(self.video_stream)
        metadata: list[str] = self.directory_path.split('/')
        
        rendition = metadata.pop()
        self.rendition = Rendition.from_dir_representation(rendition)
        self.encoding_preset = metadata.pop()
        self.segment_length = metadata.pop()
        self.video_name = metadata.pop()
        self.encoding_codec = metadata.pop()

        
    def create_video_file_from_stream(self, output_dir_path: str = '', output_file_name: str = '') -> str:
        if len(output_dir_path) == 0:
            output_dir_path = self.directory_path
        if len(output_file_name) == 0:
            output_file_name = self.output_file_name
        output_file_path: str = f'{output_dir_path}/{output_file_name}'
        if not output_file_name.endswith('.mp4'):
            output_file_path += '.mp4'
        video_stream_dir_paths: list[str] = [f'{self.directory_path}/{stream}' for stream in self.video_stream]
        audio_stream_dir_paths: list[str] = [f'{self.directory_path}/{stream}' for stream in self.audio_stream]
        
        video_tmp_output: str = f'{output_dir_path}/video_tmp.m4s'
        audio_tmp_output: str = f'{output_dir_path}/audio_tmp.m4s'
        
        for stream in video_stream_dir_paths:
            os.system(f'cat {stream} >> {video_tmp_output}')
            
        for stream in audio_stream_dir_paths:
            os.system(f'cat {stream} >> {audio_tmp_output}')
            
        os.system(f'ffmpeg -i {video_tmp_output} -i {audio_tmp_output} -c:v copy -c:a aac {output_file_path} -y')
        
        os.remove(video_tmp_output)
        os.remove(audio_tmp_output)
        
        return output_file_path
        
if __name__ == '__main__':
    test = StreamingContainer('../results/h265/AncientThought/2s/faster/145k_640x360')
    print(test)
    
    # print(test.create_video_file_from_stream(test.directory_path, 'output'))