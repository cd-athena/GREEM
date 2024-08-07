import os

from greem.testbeds.download_utility import download_parallel

# Source: https://www.cablelabs.com/4k

all_video_urls: dict[str, str] = {
    "AncientThought": "https://www.youtube.com/watch?v=60Nkt4JvteE",
    "Eldorado": "https://www.youtube.com/watch?v=qp54o2_HQvM",
    "Indoor Soccer": "https://www.youtube.com/watch?v=H_TzQ05qM_Y",
    "Lifting Off": "https://www.youtube.com/watch?v=32u4MhmHs9s",
    "LiveUntouched": "https://www.youtube.com/watch?v=J9sshEhi0Pc",
    "Moment of Intensity": "https://www.youtube.com/watch?v=JLTmjZmqiNc",
    "Seconds That Count": "https://www.youtube.com/watch?v=xMKmFU50deA",
    "Skateboading": "https://www.youtube.com/watch?v=xp0-mVmnQJk",
    "Unspoken Friend": "https://www.youtube.com/watch?v=K-MGvhjD4tg",
    "Portugal": "https://www.youtube.com/watch?v=pIWVqgtg-Js",
}


def convert_webm_to_mp4() -> None:
    video_file_paths = [video for video in os.listdir() if video.endswith("webm")]

    for video in video_file_paths:
        output_name: str = video.split(" HEVC")[0].replace(" ", "_")
        ffmpeg_call = f'ffmpeg -hwaccel cuda -y -i "{video}" {output_name}.mp4'

        os.system(ffmpeg_call)


def rename_videos(dir_path: str = ".") -> None:
    file_list: list[str] = os.listdir(dir_path)
    file_list = [file for file in file_list if file.endswith("mp4")]
    output_names: list[str] = [
        f"{file.split(' HEVC')[0].replace(' ', '_')}.mp4" for file in file_list
    ]

    for i, o in zip(file_list, output_names):
        i = f"{dir_path}{i}"
        o = f"{dir_path}{o}"
        os.rename(i, o)


if __name__ == "__main__":
    download_parallel(list(all_video_urls.values()))
    convert_webm_to_mp4()
    rename_videos()
