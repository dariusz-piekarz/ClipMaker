from json5 import loads
from pathlib import Path
from os.path import join

from clip_maker.main import clipper_from_dict


def clip_maker() -> None:
    """
    Run ClipMaker from json file.

    :return: None
    """

    dt: dict[str, ...] = loads(join(Path(__name__), "config.json"))
    dt.update({'clip_size': tuple(dt['clip_size']), 'audio_time': tuple(dt['audio_time'])})

    clipper_from_dict(dt)


if __name__ == "__main__":
    clip_maker()