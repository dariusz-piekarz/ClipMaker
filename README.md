# ClipMaker

ClipMaker builds an MP4 video from images, video segments, and a soundtrack.

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Python 3.14.8, installed automatically by uv from `.python-version`

The project uses Python 3.14 because MoviePy 2.2.1 requires Pillow `<12`, while the available Pillow wheels for Python 3.15 require Pillow 12 or newer. Python 3.15 remains installed separately and available for other projects.

## Run

```powershell
uv sync --locked
uv run --locked python -m clip_maker config.json
```

The command reads `config.json` from the current directory by default. Pass a different JSON file as the argument if needed. The tracked `config.json` still contains paths from another computer (`C:\Users\Daric\...`); replace them with existing media paths before rendering.

Example configuration:

```json
{
  "media_files": ["intro.mp4", "photo1.jpg", "photo2.jpg"],
  "clip_size": [554, 860],
  "media_time_schedule": [[0, 2.92], 2],
  "audio_file": "music.mp3",
  "audio_time": [20, 27],
  "result_file": "output.mp4"
}
```

Each video file needs a `[start, end]` range in seconds. Each image except the last needs a duration in seconds. A final image fills the remaining soundtrack time. If the final file is a video, include its range; it will be trimmed if it extends beyond the soundtrack. Omit `audio_time` to use the entire soundtrack.

Before writing the output, ClipMaker checks that every requested video and audio range fits its source file. It also rejects videos without an audio track when used as the soundtrack, missing output directories, and output paths that would overwrite an input file.

## Test

```powershell
uv sync --locked --all-groups
uv run --locked --all-groups python -m unittest discover -s tests -v
```

GitHub Actions runs the same tests on Windows and Linux. The tests generate short media files and verify the rendered video, so no personal media files are needed.

## Roadmap

See [to_do.md](to_do.md) for planned reliability and editing improvements.
