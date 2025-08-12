#!/usr/bin/env python3
import whisper
import os
from config import config

# tiny, base, small, medium, large, turbo
#   1G    1G    2G      5G     10G    6G   

whisper_model = config.WHISPER_MODEL
whisper_cache = config.WHISPER_CACHE
print("WHISPER CACHE",os.environ['WHISPER_CACHE'])
model = whisper.load_model(
    name=whisper_model,
    device="cpu"
    )
