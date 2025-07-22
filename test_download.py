from youtube_video_download import download_youtube,download_youtube_audio

# 示例调用
url = "https://www.youtube.com/watch?v=2lAe1cqCOXo"
downloaded_file = download_youtube_audio(url, output_path="./tempfile")
if downloaded_file:
    print(f"Video saved to: {downloaded_file}")

