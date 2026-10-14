from math import isfinite
from pathlib import Path

from clip_maker import AUDIO_EXTENSIONS, IMAGE_EXTENSIONS, VIDEO_EXTENSIONS


def extension(path: str) -> str:
    return Path(path).suffix.removeprefix('.').upper()


def duration(value: float | int | tuple[float | int, float | int]) -> float:
    if isinstance(value, (tuple, list)):
        if len(value) != 2 or not all(_valid_number(x) for x in value):
            raise ValueError('A time range must contain two finite numbers.')
        start, end = value
        if start < 0 or end <= start:
            raise ValueError('A time range must have 0 <= start < end.')
        return float(end - start)
    if not _valid_number(value) or value <= 0:
        raise ValueError('A duration must be a positive finite number.')
    return float(value)


def _valid_number(value: object) -> bool:
    return isinstance(value, (float, int)) and not isinstance(value, bool) and isfinite(value)


def validate_inputs(media_paths, common_size, media_timing, soundtrack_path, soundtrack_timing) -> None:
    if not media_paths:
        raise ValueError('At least one media file is required.')
    if len(common_size) != 2 or any(not isinstance(x, int) or isinstance(x, bool) or x <= 0 for x in common_size):
        raise ValueError('clip_size must contain a positive width and height.')
    for path in media_paths:
        if not Path(path).is_file():
            raise FileNotFoundError(path)
        if extension(path) not in IMAGE_EXTENSIONS + VIDEO_EXTENSIONS:
            raise ValueError(f'Unsupported visual media format: {path}')
    if not Path(soundtrack_path).is_file():
        raise FileNotFoundError(soundtrack_path)
    if extension(soundtrack_path) not in AUDIO_EXTENSIONS + VIDEO_EXTENSIONS:
        raise ValueError(f'Unsupported soundtrack format: {soundtrack_path}')
    expected = len(media_paths) - (extension(media_paths[-1]) in IMAGE_EXTENSIONS)
    if len(media_timing) != expected:
        raise ValueError(f'media_time_schedule needs {expected} entries for {len(media_paths)} media files.')
    for path, timing in zip(media_paths, media_timing):
        if extension(path) in IMAGE_EXTENSIONS and isinstance(timing, (tuple, list)):
            raise ValueError('Image timing must be a duration.')
        if extension(path) in VIDEO_EXTENSIONS and not isinstance(timing, (tuple, list)):
            raise ValueError('Video timing must be a [start, end] range.')
        duration(timing)
    if soundtrack_timing is not None:
        duration(soundtrack_timing)
