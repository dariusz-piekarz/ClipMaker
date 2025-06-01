from typing import Union


AUDIO_EXTENSIONS: list[str] = ['MP3','WMA', "FLAC", "AAC", "OGG"]
VIDEO_EXTENSIONS: list[str] = ["MP4", "MOV", "AVI", "WMV", "FLV"]
IMAGE_EXTENSIONS: list[str] = ["JPG", "JPEG", "PNG", 'GIF', 'WEBP']


Numerical: type = Union[float, int]
TimeTuple: type = tuple[Numerical, Numerical]
