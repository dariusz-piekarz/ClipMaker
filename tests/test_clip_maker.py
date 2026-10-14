import math
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np
from PIL import Image
from moviepy import AudioFileClip, ImageClip, VideoFileClip

from clip_maker.core import visual_media_and_soundtrack_to_clip
from clip_maker.utils import duration, validate_inputs


class ClipMakerTests(unittest.TestCase):
    @staticmethod
    def make_audio(path: Path, seconds: float) -> None:
        with wave.open(str(path), 'wb') as stream:
            stream.setnchannels(1)
            stream.setsampwidth(2)
            stream.setframerate(8000)
            stream.writeframes(np.zeros(round(seconds * 8000), dtype=np.int16).tobytes())

    @staticmethod
    def make_video(path: Path, color: str, seconds: float, audio_path: Path | None = None) -> None:
        image = path.with_suffix('.png')
        Image.new('RGB', (16, 16), color).save(image)
        with ImageClip(str(image)).with_duration(seconds) as clip:
            if audio_path is None:
                clip.write_videofile(str(path), fps=10, codec='libx264', logger=None)
            else:
                with AudioFileClip(str(audio_path)) as audio:
                    with clip.with_audio(audio) as voiced:
                        voiced.write_videofile(str(path), fps=10, codec='libx264', audio_codec='aac', logger=None)

    def test_duration_rejects_invalid_ranges(self):
        for value in ((2, 1), (1, 1), -1, float('nan'), True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                duration(value)

    def test_schedule_requires_one_entry_less_for_final_image(self):
        with tempfile.TemporaryDirectory() as root:
            image = Path(root, 'image.png')
            audio = Path(root, 'audio.wav')
            image.touch()
            audio.touch()
            with self.assertRaisesRegex(ValueError, 'needs 0 entries'):
                validate_inputs([str(image)], (32, 32), [1], str(audio), None)

    def test_writes_video_with_final_image_and_sound(self):
        with tempfile.TemporaryDirectory() as root:
            first = Path(root, 'first.png')
            last = Path(root, 'last.png')
            audio = Path(root, 'audio.wav')
            output = Path(root, 'output.mp4')
            Image.new('RGB', (16, 16), 'red').save(first)
            Image.new('RGB', (16, 16), 'blue').save(last)
            samples = np.zeros(8000, dtype=np.int16)
            with wave.open(str(audio), 'wb') as stream:
                stream.setnchannels(1)
                stream.setsampwidth(2)
                stream.setframerate(8000)
                stream.writeframes(samples.tobytes())
            visual_media_and_soundtrack_to_clip(
                [str(first), str(last)], (16, 16), [0.4], str(audio), str(output)
            )
            with VideoFileClip(str(output)) as result:
                self.assertTrue(math.isclose(result.duration, 1, abs_tol=0.05))
                self.assertIsNotNone(result.audio)
                self.assertGreater(result.get_frame(0.1)[0, 0, 0], 200)
                self.assertGreater(result.get_frame(0.8)[0, 0, 2], 200)

    def test_trims_final_video_to_audio(self):
        with tempfile.TemporaryDirectory() as root:
            image = Path(root, 'image.png')
            source = Path(root, 'source.mp4')
            audio = Path(root, 'audio.wav')
            output = Path(root, 'output.mp4')
            Image.new('RGB', (16, 16), 'red').save(image)
            with ImageClip(str(image)).with_duration(1) as clip:
                clip.write_videofile(str(source), fps=10, codec='libx264', logger=None)
            with wave.open(str(audio), 'wb') as stream:
                stream.setnchannels(1)
                stream.setsampwidth(2)
                stream.setframerate(8000)
                stream.writeframes(np.zeros(4800, dtype=np.int16).tobytes())
            visual_media_and_soundtrack_to_clip(
                [str(image), str(source)], (16, 16), [0.2, (0, 1)], str(audio), str(output)
            )
            with VideoFileClip(str(output)) as result:
                self.assertTrue(math.isclose(result.duration, 0.6, abs_tol=0.05))

    def test_multiple_videos_and_video_soundtrack(self):
        with tempfile.TemporaryDirectory() as root:
            first = Path(root, 'first.mp4')
            second = Path(root, 'second.mp4')
            soundtrack = Path(root, 'soundtrack.mp4')
            audio = Path(root, 'audio.wav')
            output = Path(root, 'output.mp4')
            self.make_video(first, 'red', 0.5)
            self.make_video(second, 'blue', 0.5)
            self.make_audio(audio, 0.7)
            self.make_video(soundtrack, 'green', 0.7, audio)
            visual_media_and_soundtrack_to_clip(
                [str(first), str(second)], (16, 16), [(0, 0.3), (0, 0.5)],
                str(soundtrack), str(output), (0, 0.7),
            )
            with VideoFileClip(str(output)) as result:
                self.assertTrue(math.isclose(result.duration, 0.7, abs_tol=0.05))
                self.assertIsNotNone(result.audio)
                self.assertGreater(result.get_frame(0.1)[0, 0, 0], 200)
                self.assertGreater(result.get_frame(0.5)[0, 0, 2], 200)

    def test_rejects_out_of_bounds_range_before_writing(self):
        with tempfile.TemporaryDirectory() as root:
            first = Path(root, 'first.mp4')
            second = Path(root, 'second.mp4')
            audio = Path(root, 'audio.wav')
            output = Path(root, 'output.mp4')
            self.make_video(first, 'red', 0.5)
            self.make_video(second, 'blue', 0.5)
            self.make_audio(audio, 1)
            for timings in ([(0, 0.6), (0, 0.3)], [(0, 0.3), (0, 0.6)]):
                with self.subTest(timings=timings), self.assertRaisesRegex(ValueError, 'Video range ends after the file'):
                    visual_media_and_soundtrack_to_clip(
                        [str(first), str(second)], (16, 16), timings, str(audio), str(output)
                    )
                self.assertFalse(output.exists())

    def test_rejects_video_without_audio_as_soundtrack(self):
        with tempfile.TemporaryDirectory() as root:
            image = Path(root, 'image.png')
            silent_video = Path(root, 'silent.mp4')
            output = Path(root, 'output.mp4')
            Image.new('RGB', (16, 16), 'red').save(image)
            self.make_video(silent_video, 'blue', 0.5)
            with self.assertRaisesRegex(ValueError, 'no audio track'):
                visual_media_and_soundtrack_to_clip(
                    [str(image)], (16, 16), [], str(silent_video), str(output)
                )
            self.assertFalse(output.exists())

    def test_rejects_audio_range_after_soundtrack(self):
        with tempfile.TemporaryDirectory() as root:
            image = Path(root, 'image.png')
            audio = Path(root, 'audio.wav')
            output = Path(root, 'output.mp4')
            Image.new('RGB', (16, 16), 'red').save(image)
            self.make_audio(audio, 0.5)
            with self.assertRaisesRegex(ValueError, 'audio_time ends after'):
                visual_media_and_soundtrack_to_clip(
                    [str(image)], (16, 16), [], str(audio), str(output), (0, 0.7)
                )
            self.assertFalse(output.exists())

    def test_rejects_output_overwriting_input(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root, 'source.mp4')
            audio = Path(root, 'audio.wav')
            source.touch()
            audio.touch()
            with self.assertRaisesRegex(ValueError, 'overwrite an input file'):
                validate_inputs([str(source)], (16, 16), [(0, 0.5)], str(audio), None, str(source))


if __name__ == '__main__':
    unittest.main()
