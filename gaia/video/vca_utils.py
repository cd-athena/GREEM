from dataclasses import dataclass, field
import pandas as pd

from gaia.video.video_info import VideoDTO


@dataclass
class VCAContainer():
    
    videoDTO: VideoDTO
    csv_file_path: str
    dataframe: pd.DataFrame = field(init=False, repr=False)
    description_df: pd.DataFrame = field(init=False, repr=False)
    total_frames: int = field(init=False)
    
    
    def __post_init__(self):
        """
        Sets instance variable values after the `__init__` function is completed
        """
        self.dataframe: pd.DataFrame = pd.read_csv(self.csv_file_path)
        self.description_df = self.dataframe.describe()
        self.total_frames = len(self.dataframe)