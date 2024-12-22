import os


def bool_env(key, default=False):
    value = os.getenv(key, str(default)).lower()
    return value in {'1', 'true', 't', 'yes', 'y'}
