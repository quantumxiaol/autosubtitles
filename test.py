import asyncio
from processYoutube import process_youtube_video
from youtube_video_download import download_youtube_subtitles
if __name__ == "__main__":
    # 3b1b 动画
    youtube_url = "https://www.youtube.com/watch?v=LPZh9BOjkQs"
    
    asyncio.run(
        process_youtube_video(
            url=youtube_url,
            output_dir="./tempfile",
            download_audio=True,
            original_language="English",
            target_language="Chinese"
        )
    )
    download_youtube_subtitles(youtube_url,"./tempfile")
