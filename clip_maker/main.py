from clip_maker.core import visual_media_and_soundtrack_to_clip


def clipper_from_dict(dt: dict[str, ...]) -> None:
    """
    Run tool for creating .mp4 video clips from provided images and soundtrack from a dictionary.

    :param dt: dict[str, ...],
    :return: None
    """

    fields: list[str] = ['media_files', 'clip_size', 'media_time_schedule', 'audio_file', 'result_file', 'audio_time']

    if any(field not in dt.keys() for field in fields):
        raise KeyError(f"Fields {fields} are mandatory!")

    visual_media_and_soundtrack_to_clip(media_paths=dt['media_files'],
                                        common_size=dt['clip_size'],
                                        media_timeing=dt['media_time_schedule'],
                                        soundtrack_path=dt['audio_file'],
                                        output_file_name=dt['result_file'],
                                        soundtrack_timing=dt['audio_time'])


if __name__ == '__main__':
    config: dict[str, ...] = {'media_files': [r"C:\Users\Daric\Desktop\wynik2.2.mp4",
                                              r"C:\Users\Daric\Desktop\image3.jpg",
                                              r"C:\Users\Daric\Desktop\image4.jpg"],
                              'clip_size': (554, 860),
                              'media_time_schedule': [(0.0, 2.92), 2],
                              'audio_file': r"C:\Users\Daric\Desktop\Jenkins, Ratledge - Cantus Iteratus.mp3",
                              'result_file': r"C:\Users\Daric\Desktop\wwww.mp4",
                              'audio_time': (20, 27)}

    clipper_from_dict(config)
