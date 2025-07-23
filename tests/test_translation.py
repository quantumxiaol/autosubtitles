import asyncio

from audio_transcribe import processVideofiletoTexts,write_bilingual_srt

audio_path="YouTubeRewind.webm"
text=processVideofiletoTexts("./tempfile",audio_path)
print(text)
asyncio.run(write_bilingual_srt(text,"English","Chinese","./tempfile","outtest.srt",20))
