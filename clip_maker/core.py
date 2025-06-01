from typing import Optional, Union
from moviepy import ImageClip, AudioFileClip, VideoFileClip, concatenate_videoclips

from clip_maker.utils import (_get_extension,
                              _read_media_set_duration,
                              _get_total_length_of_media_clip,
                              _cut_length_of_audio_or_last_video,
                              _initial_input_verification)
from clip_maker import AUDIO_EXTENSIONS, VIDEO_EXTENSIONS, TimeTuple, Numerical


def visual_media_and_soundtrack_to_clip(media_paths: list[str],
                                        common_size: tuple[int, int],
                                        media_timeing: list[Union[Numerical, TimeTuple]],
                                        soundtrack_path: str,
                                        output_file_name: str,
                                        soundtrack_timing: Optional[TimeTuple] = None) -> None:
    """
    Function for creating .mp4 video clips from provided images and soundtrack.

    The function displays images in the provided order for time specified in 'images_timeing'.
    Size of images is standardised by parameter 'common_size'. To images displayed in time there is attached soundtrack,
    therefore timing for images must cover one less length [in seconds] than number of images
     (the last image is displayed for the remaining time to the clip end).
     Soundtrack itself can be a part of a full soundtrack file, if such restriction is requested,
     then it should be specified in the parameter 'soundtrack_timing'.

    :param media_paths: list[str], list of paths to image files in order these appear in the final video clip
    :param common_size: tuple[int, int], common width and height of images read from images_paths
    :param media_timeing: list[Union[Numerical, TimeTuple]], list of display-time of images provided in images_paths
    :param soundtrack_path: str, path to a video clip or audio clip that should be in a target video file
    :param output_file_name: str, a path (containing a name of a file) to the output clip
    :param soundtrack_timing: Optional[tuple[Numerical, Numerical]], if None then full provided soundtrack is utilized,
     otherwise first coordinate is the start time (in seconds) and the second coordinate is the end time (in second) of
     the audio clip.

    :return: None
    """

    _initial_input_verification(media_paths, media_timeing, soundtrack_path)

    audio: AudioFileClip
    soundtrack_ext: str = _get_extension(soundtrack_path)

    if soundtrack_ext in VIDEO_EXTENSIONS:
        audio = VideoFileClip(soundtrack_path).audio

    elif soundtrack_ext in AUDIO_EXTENSIONS:
        audio = AudioFileClip(soundtrack_path)

    total_length_media: Numerical = _get_total_length_of_media_clip(media_timeing=media_timeing)

    aud_time: TimeTuple
    last_media_timing: Union[Numerical, TimeTuple]

    aud_time, last_media_timing = _cut_length_of_audio_or_last_video(
        audio_length=soundtrack_timing if soundtrack_timing is not None else (0, audio.duration),
        total_length_mds=total_length_media,
        last_md_ext=_get_extension(media_paths[-1]),
        last_md_time=media_timeing[-1] if isinstance(media_timeing[-1], tuple) else None)

    audio = audio.subclipped(*aud_time)

    media_time: list[Union[Numerical, TimeTuple]] = media_timeing

    if isinstance(media_timeing, tuple):
        media_time.pop(-1)

    media_time.append(last_media_timing)

    mds: list[Union[ImageClip, VideoFileClip]] = _read_media_set_duration(media_paths=media_paths,
                                                                          common_size=common_size,
                                                                          media_timing=media_time)

    video_clip: VideoFileClip = concatenate_videoclips(mds).with_audio(audio)
    video_clip.duration = audio.duration

    video_clip.write_videofile(output_file_name,
                               codec="libx264",
                               audio_codec="aac",
                               fps=24,
                               threads=4,
                               preset="fast")

    for md_clip in mds:
        md_clip.close()

    video_clip.close()
