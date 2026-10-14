import math
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np
from PIL import Image
from moviepy import ImageClip, VideoFileClip

from clip_maker.core import visual_media_and_soundtrack_to_clip
from clip_maker.utils import duration, validate_inputs


class ClipMakerTests(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
