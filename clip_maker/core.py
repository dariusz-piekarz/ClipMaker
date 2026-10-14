from contextlib import ExitStack

from moviepy import AudioFileClip, ImageClip, VideoFileClip, concatenate_videoclips

from clip_maker import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS
from clip_maker.utils import duration, extension, validate_inputs


def visual_media_and_soundtrack_to_clip(
    media_paths: list[str],
    common_size: tuple[int, int],
    media_timeing: list[float | int | tuple[float | int, float | int]],
    soundtrack_path: str,
    output_file_name: str,
    soundtrack_timing: tuple[float | int, float | int] | None = None,
) -> None:
    """Create a clip. A final image fills remaining audio; a final video may be trimmed."""
    validate_inputs(media_paths, common_size, media_timeing, soundtrack_path, soundtrack_timing)
    with ExitStack() as stack:
        if extension(soundtrack_path) in VIDEO_EXTENSIONS:
            soundtrack_video = stack.enter_context(VideoFileClip(soundtrack_path))
            if soundtrack_video.audio is None:
                raise ValueError('The soundtrack video has no audio track.')
            audio = soundtrack_video.audio
        else:
            audio = stack.enter_context(AudioFileClip(soundtrack_path))
        audio_start, audio_end = soundtrack_timing or (0, audio.duration)
        if audio_end > audio.duration + 1e-6:
            raise ValueError('audio_time ends after the soundtrack.')
        planned = sum(duration(item) for item in media_timeing)
        available = float(audio_end - audio_start)
        final_is_image = extension(media_paths[-1]) in IMAGE_EXTENSIONS
        if final_is_image:
            if planned >= available:
                raise ValueError('The soundtrack must be longer than the scheduled media so the last image is visible.')
            timings = [*media_timeing, available - planned]
            output_duration = available
        else:
            preceding = sum(duration(item) for item in media_timeing[:-1])
            if preceding >= available:
                raise ValueError('The soundtrack must extend past the preceding media.')
            last_start, last_end = media_timeing[-1]
            last_end = min(last_end, last_start + available - preceding)
            timings = [*media_timeing[:-1], (last_start, last_end)]
            output_duration = preceding + (last_end - last_start)
        clips = []
        for path, timing in zip(media_paths, timings):
            if extension(path) in IMAGE_EXTENSIONS:
                clip = stack.enter_context(ImageClip(path))
                clip = clip.resized(new_size=common_size).with_duration(duration(timing))
            else:
                source = stack.enter_context(VideoFileClip(path))
                start, end = timing
                if end > source.duration + 1e-6:
                    raise ValueError(f'Video range ends after the file: {path}')
                clip = source.subclipped(start, end).resized(new_size=common_size)
            clips.append(clip)
        sound = audio.subclipped(audio_start, audio_start + output_duration)
        result = concatenate_videoclips(clips).with_audio(sound)
        try:
            result.write_videofile(output_file_name, codec='libx264', audio_codec='aac', fps=24, threads=4, preset='fast')
        finally:
            result.close()
