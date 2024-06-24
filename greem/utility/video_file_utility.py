def abbreviate_video_name(video_name: str) -> str:
    video_name_no_ext: str = video_name.replace('.265', '')

    upper_case: str = ''.join(
        [
            f'{c}{video_name_no_ext[video_name_no_ext.find(c) + 1]}'
            for c in video_name_no_ext if c.isupper()
        ])
    numbers: str = ''.join([c for c in video_name_no_ext if c.isnumeric()])
    abbreviate: str = f'{upper_case}_{numbers}'

    return abbreviate


def remove_media_extension(file_name: str) -> str:
    return file_name.removesuffix('.265').removesuffix('.webm').removesuffix('.mp4')


def get_media_extension(file_name: str) -> str:
    return file_name.split('.')[-1]
