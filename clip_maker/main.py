from clip_maker.core import visual_media_and_soundtrack_to_clip


def clipper_from_dict(config: dict) -> None:
    """Map the JSON configuration fields to the renderer's arguments."""
    required = {'media_files', 'clip_size', 'media_time_schedule', 'audio_file', 'result_file'}
    missing = required - config.keys()
    if missing:
        raise ValueError(f'Missing config fields: {", ".join(sorted(missing))}')
    visual_media_and_soundtrack_to_clip(
        media_paths=config['media_files'],
        common_size=tuple(config['clip_size']),
        media_timeing=config['media_time_schedule'],
        soundtrack_path=config['audio_file'],
        output_file_name=config['result_file'],
        soundtrack_timing=config.get('audio_time'),
    )
