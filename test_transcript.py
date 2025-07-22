from audiotranscribe import processVideofiletoTexts,process_YT_video_url

# audio_url="https://llm-image-quantumxiaol.oss-cn-beijing.aliyuncs.com/TaoteChing.mp3"
# text=process_audio_url(audio_url,output_path="./tempfile",model_name="turbo")
# print(text)

# video_url="https://www.youtube.com/watch?v=2lAe1cqCOXo"
# text=processVideofiletoTexts("./tempfile",video_url)
# text=processVideofiletoTexts("./tempfile","YouTube Rewind 2019： For the Record ｜ #YouTubeRewind.webm")
# text=process_YT_video_url(video_url,output_path="./tempfile",model_name="turbo")
audio_path="YouTubeRewind.webm"
text=processVideofiletoTexts("./tempfile",audio_path)
print(text)