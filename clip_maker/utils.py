from os.path import exists
from typing import Optional, Union
from moviepy import ImageClip, VideoFileClip
from moviepy.video.fx import Resize

from clip_maker import VIDEO_EXTENSIONS, IMAGE_EXTENSIONS, AUDIO_EXTENSIONS, TimeTuple, Numerical


def _get_extension(path: str) -> str:
    return path.split(".")[-1].upper()


def _abs_diffr(x: Numerical, y: Numerical) -> Numerical:
    return abs(y - x)


def _initial_input_verification(media_paths: list[str], media_timing: list[Numerical], audio_path: str) -> None:
    last_media_ext: str = _get_extension(media_paths[-1])

    if len(media_paths) != len(media_timing) + 1 and last_media_ext in IMAGE_EXTENSIONS:
        raise UnboundLocalError(
            "Size of 'media_paths' must be one more than 'media_timeing' if last media is an image!")

    elif len(media_paths) == len(media_timing) and last_media_ext not in VIDEO_EXTENSIONS:
        raise UnboundLocalError(
            "If Size of 'media_paths' equals size of 'media_timeing', then last media must be a video!")

    if not exists(audio_path):
        raise FileExistsError(f'The {audio_path} does not exist!')

    if _get_extension(audio_path) not in AUDIO_EXTENSIONS + VIDEO_EXTENSIONS:
        raise ValueError(f"Audio file cannot have the {_get_extension(audio_path).lower()} extension!")

    if any([not exists(md_path) for md_path in media_paths]):
        raise FileExistsError("At least one of provided media files does not exist!")

    visual_extensions: list[str] = VIDEO_EXTENSIONS + IMAGE_EXTENSIONS

    if any([_get_extension(md_path) not in visual_extensions for md_path in media_paths]):
        raise ValueError(
            f"One of media files have non-supported extensions! Supported extensions are: {visual_extensions}!")


def _get_total_length_of_media_clip(media_timeing: list[Union[Numerical, TimeTuple]]) -> Numerical:
    return sum(
        [md_time if not isinstance(md_time, tuple) else _abs_diffr(*md_time) for md_time in media_timeing])


def _cut_length_of_audio_or_last_video(audio_length: TimeTuple,
                                       total_length_mds: Numerical,
                                       last_md_ext: str,
                                       last_md_time: Optional[Union[Numerical, TimeTuple]] = None) -> tuple[
    TimeTuple, Union[Numerical, TimeTuple]]:
    alen: Numerical = _abs_diffr(*audio_length)

    if last_md_ext in IMAGE_EXTENSIONS:
        return audio_length, alen - total_length_mds

    if last_md_time is None or not isinstance(last_md_time, tuple):
        raise ValueError("For non-image extensions 'last_md_time' must be provided as tuple!")

    last_len: Numerical = _abs_diffr(*last_md_time)

    if alen == total_length_mds:
        return audio_length, last_md_time

    elif alen > total_length_mds:
        aud_start: Numerical = min(audio_length[0], audio_length[1])
        return (aud_start, aud_start + total_length_mds), last_md_time

    elif total_length_mds - alen < last_len:
        lmd_start: Numerical = min(last_md_time[0], last_md_time[1])
        return audio_length, (lmd_start, lmd_start + total_length_mds - alen)

    else:
        raise UnboundLocalError(
            "Too many media files provided! Length of the last video cannot be shortened in such a way that the total"
            " length of medias cover the length of the audiofile!")


def _read_media_set_duration(media_paths: list[str],
                             common_size: tuple[int, int],
                             media_timing: list[Union[Numerical, TimeTuple]]) -> list[Union[ImageClip, VideoFileClip]]:
    mds: list[Union[ImageClip, VideoFileClip]] = []

    for i in range(len(media_paths)):

        if _get_extension(media_paths[i]) in IMAGE_EXTENSIONS:
            mds.append(ImageClip(media_paths[i]).with_effects([Resize(common_size)]))

        else:
            mds.append(VideoFileClip(media_paths[i]).with_effects([Resize(common_size)]))
            mds[i] = mds[i].subclipped(*media_timing[i])

        mds[i].duration = media_timing[i] if isinstance(media_timing[i], Numerical) else _abs_diffr(*media_timing[i])

    return mds
