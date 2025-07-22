import os

import yt_dlp
import requests
import magic
import mimetypes

from pydub import AudioSegment
import whisper.whisper as whisper
import urllib.request
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv(".env")

proxy_host = os.getenv("PROXY_HOST")
proxy_port = os.getenv("PROXY_PORT")
proxy_url= os.getenv("PROXY_URL")
# 设置代理
proxies = {
    "http": f"http://{proxy_host}:{proxy_port}",
    "https": f"http://{proxy_host}:{proxy_port}",
}
proxy_handler = urllib.request.ProxyHandler(proxies)

print(f"🌐 Youtube 使用代理：{proxy_url}")
if not all([proxy_host,proxy_port]):
    raise ValueError("缺少必要的环境变量，请检查 .env 文件")
response = requests.get("https://www.youtube.com", proxies=proxies)
print(response.status_code)
def convert_webm_to_mp3(input_path: str, output_path: str = None):
    """
    将 .webm 文件转换为 .mp3 格式
    :param input_path: 输入文件路径
    :param output_path: 输出文件路径（可选）
    :return: 转换后的文件路径
    """
    if not output_path:
        base, _ = os.path.splitext(input_path)
        output_path = f"{base}.mp3"

    try:
        audio = AudioSegment.from_file(input_path, format="webm")
        audio.export(output_path, format="mp3")
        print(f"✅ 转换完成：{output_path}")
        return output_path
    except Exception as e:
        print(f"❌ 转换失败：{e}")
        raise
def add_suffix_to_filename(path: str, suffix: int) -> str:
    """
    给文件名添加序号后缀，例如：
    "video.mp4" -> "video (1).mp4"
    """
    base, ext = os.path.splitext(path)
    return f"{base} ({suffix}){ext}"

def get_filename_from_url(url: str) -> str:
    """
    从 URL 中提取文件名（包含扩展名），如果无法提取则返回 None
    """
    parsed_url = urlparse(url)
    path = parsed_url.path
    filename = os.path.basename(path)
    if '.' in filename:
        return filename
    return None
def get_available_filename(directory: str, filename: str) -> str:
    """
    检查文件是否已存在，如果存在则添加序号直到找到可用文件名
    """
    base_path = os.path.join(directory, filename)
    full_path = base_path
    counter = 1
    while os.path.exists(full_path):
        full_path = add_suffix_to_filename(base_path, counter)
        counter += 1
    return full_path
def download_youtube(url: str, output_path: str = ".", only_audio: bool = True):
    try:
        ydl_opts = {
            'format': 'bestaudio/best' if only_audio else 'bestvideo+bestaudio/best',  # 根据only_audio选择格式
            'outtmpl': os.path.join(output_path, '%(id)s'),  # 输出模板
            'proxy': f"http://{proxy_host}:{proxy_port}",  # 设置代理
            'noplaylist': True,  # 只下载单个视频而不是播放列表
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': True,
            'cookiefile': './cookies.txt',
            # 'cookies-from-browser': 'egde',
        }
        

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if ydl==None:
                raise Exception("ydl is None")
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title', None)
            video_ext = info_dict.get('ext', 'mp4')
            original_filename = f"{video_title}.{video_ext}"
            downloaded_path = get_available_filename(output_path, original_filename)

            print(f"Download completed! File saved to {downloaded_path}")
            return os.path.abspath(downloaded_path)

    except Exception as e:
        print(f"An error occurred: {e}")
        # return None
        raise e

def download_youtube_audio(url: str, output_path: str = ".", only_audio: bool = True):
    try:
        ydl_opts = {
            'format': 'bestaudio/best' if only_audio else 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(output_path, '%(id)s.%(ext)s'),  # 保留原始格式
            'proxy': f"http://{proxy_host}:{proxy_port}",
            'noplaylist': True,
            'user_agent': 'Mozilla/5.0',
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': True,
            'cookiefile': './cookies.txt',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_id = info_dict.get('id', None)
            original_ext = info_dict.get('ext', 'unknown')

        # 原始文件路径
        original_file = os.path.join(output_path, f"{video_id}.{original_ext}")

        # 目标文件路径
        mp3_file = os.path.join(output_path, f"{video_id}.mp3")

        # 使用 pydub + ffmpeg 转换为 mp3
        print(f"🔄 正在将 {original_ext} 转换为 mp3...")
        audio = AudioSegment.from_file(original_file)
        audio.export(mp3_file, format="mp3")

        # 删除原始文件（可选）
        os.remove(original_file)
        print(f"✅ 下载并转换完成！文件已保存为：{mp3_file}")

        return os.path.abspath(mp3_file)

    except Exception as e:
        print(f"❌ 下载或转换失败：{e}")
        raise e

def download_youtube_subtitles(url: str, output_path: str = ".", lang: str = "a.en") -> dict:
    """
    仅下载 YouTube 自动生成字幕（默认 a.en）
    :param url: YouTube 视频链接
    :param output_path: 输出目录
    :param lang: 字幕语言代码（如 a.en 表示英文自动生成字幕）
    :return: 包含 subtitle_path 的字典
    """
    try:
        ydl_opts = {
            'proxy': f"http://{proxy_host}:{proxy_port}",
            'skip_download': True,
            'writeautomaticsub': True,
            'writesubtitles': True,
            'subtitleslangs': [lang],
            'outtmpl': os.path.join(output_path, '%(id)s.%(ext)s'),
            'noplaylist': True,
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': True,
            'cookiefile': './cookies.txt'
        }


        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info.get("id")
            subtitle_path = os.path.join(output_path, f"{video_id}.{lang}.{lang.split('.')[-1]}")

            if os.path.exists(subtitle_path):
                return {
                    "subtitle_path": os.path.abspath(subtitle_path),
                    "success": True
                }
            else:
                return {
                    "success": False,
                    "error": "字幕文件未生成，可能视频无可用字幕"
                }

    except Exception as e:
        print(f"[ERROR] 字幕下载失败: {e}")
        raise e
def download_youtube_video_with_subtitles(url: str, output_path: str = ".", lang: str = "a.en") -> dict:
    """
    同时下载 YouTube 视频和字幕
    :param url: YouTube 视频链接
    :param output_path: 输出目录
    :param lang: 字幕语言代码（如 a.en）
    :return: 包含 video_path 和 subtitle_path 的字典
    """
    try:
        ydl_opts = {
            'proxy': f"http://{proxy_host}:{proxy_port}",
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(output_path, '%(id)s.%(ext)s'),
            'writeautomaticsub': True,
            'writesubtitles': True,
            'subtitleslangs': [lang],
            'noplaylist': True,
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': True,
            'cookiefile': './cookies.txt'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info.get("id")
            video_ext = info.get("ext", "mp4")
            subtitle_ext = lang.split('.')[-1]
            video_path = os.path.join(output_path, f"{video_id}.{video_ext}")
            subtitle_path = os.path.join(output_path, f"{video_id}.{lang}.{subtitle_ext}")

            result = {
                "video_path": os.path.abspath(video_path),
                "success": True
            }

            if os.path.exists(subtitle_path):
                result["subtitle_path"] = os.path.abspath(subtitle_path)

            return result

    except Exception as e:
        print(f"[ERROR] 下载失败: {e}")
        raise e