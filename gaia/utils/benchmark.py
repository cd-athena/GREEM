import argparse


class BenchmarkParser():
    "Source: https://docs.python.org/3/library/argparse.html"

    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            description='Parser for Benchmark Flags')

        self.__add_arguments()

        self.arguments = self.parser.parse_args()

    def __add_arguments(self) -> None:
        self.parser.add_argument(
            '--cuda',
            action=argparse.BooleanOptionalAction,
            default=False,
            help='Enables/Disables CUDA support for FFMPEG'
        )

        self.parser.add_argument(
            '--quiet',
            '--quiet-ffmpeg',
            action=argparse.BooleanOptionalAction,
            default=False,
            help='Suppresses CLI output of FFMPEG'
        )

    def is_cuda_enabled(self) -> bool:
        """Cuda Enabled is used to add the flag for GPU hardware acceleration.

        Flags:
            * `--cuda` -> `True`
            * `--no-cuda` -> `False`

        Default:
            `False`

        Usage:
            `$ python <python_file_name>.py --cuda`

        Returns:
            `bool`: `True` if the CLI argument provided was set to true, else returns `False` if set to `--no-cuda`
        """
        return self.arguments.cuda

    def is_quiet_ffmpeg(self) -> bool:
        """Quiet FFMPEG is used to set the logging level to quiet, so no log will be produced by FFMPEG.

        Flags:
            * `--quiet` -> `True`, 
            * `--no-quiet` -> `False`
            * `--quiet-ffmpeg` -> `True`,
            * `--no-quiet-ffmpeg` -> `False`

        Default:
            `False`

        Usage:
            `$ python <python_file_name>.py --quiet`

        Returns:
            `bool`: `True` if the CLI argument provided was set to true, else returns `False`
        """
        return self.arguments.quiet

    def get_ffmpeg_cuda_flag(self) -> str:
        return '-hwaccel cuda' if self.is_cuda_enabled() else ''

    def get_ffmpeg_quiet_flag(self) -> str:
        return '-v quiet' if self.is_quiet_ffmpeg() else ''


if __name__ == '__main__':
    parser = BenchmarkParser()
    # print(parser.parser.print_help())
