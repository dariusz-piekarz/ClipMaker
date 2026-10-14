import argparse
import json
from pathlib import Path

from clip_maker.main import clipper_from_dict


def clip_maker() -> None:
    """Read a configuration file and invoke the renderer from the CLI."""
    parser = argparse.ArgumentParser(description='Create a video clip from a JSON configuration.')
    parser.add_argument('config', nargs='?', type=Path, default=Path('config.json'))
    args = parser.parse_args()
    with args.config.open(encoding='utf-8') as stream:
        config = json.load(stream)
    clipper_from_dict(config)


if __name__ == '__main__':
    clip_maker()
