import os
import asyncio
import hashlib

from pathlib import Path

from autosubtitles.youtube_video_download import download_youtube,download_youtube_audio,convert_webm_to_mp3
from autosubtitles.audio_transcribe import processVideofiletoTexts,write_bilingual_srt

from autosubtitles.config import config

output_dir=config.OUTPUT_DIR
whisper_model=config.WHISPER_MODEL
async def process_youtube_video(
    url: str,
    output_dir: str = output_dir,
    download_audio: bool = True,
    original_language: str = "English",
    target_language: str = "Chinese",
    batch_size: int = 20,
    overwrite_mode: str = "overwrite"
):
    """
    统一入口函数：从 YouTube 视频链接开始，自动完成：
    1. 下载视频或音频
    2. 提取音频（如需要）
    3. 使用 Whisper 生成字幕
    4. 翻译并生成双语字幕文件（.srt）

    参数：
        url: YouTube 视频链接
        output_dir: 输出目录
        download_audio: 是否只下载音频
        original_language: 原始语言（用于 Whisper）
        target_language: 翻译目标语言
        batch_size: 翻译批次大小
        overwrite_mode: 写入模式：overwrite/skip/backup
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    print(f"🔗 正在处理视频：{url}")

    try:
        # 1. 根据URL生成唯一的文件名前缀
        safe_filename_prefix = generate_safe_filename_from_url(url)
        
        # 2. 下载视频或音频
        if download_audio:
            print("🎵 正在下载音频...")
            audio_path = await asyncio.to_thread(download_youtube_audio, url, output_path=output_dir, only_audio=True)
            audio_base_name = f"{safe_filename_prefix}.mp3"
            audio_path_final = os.path.join(output_dir, audio_base_name)
            os.rename(audio_path, audio_path_final)
            audio_path = audio_path_final
        else:
            print("🎥 正在下载视频...")
            video_path = await asyncio.to_thread(download_youtube, url, output_path=output_dir, only_audio=False)
            # 提取音频
            print("🎵 正在从视频中提取音频...")
            audio_path = os.path.join(output_dir, f"{safe_filename_prefix}.mp3")
            convert_webm_to_mp3(video_path, audio_path)

        # 3. 使用 Whisper 生成字幕
        print("🧠 正在使用 Whisper 生成字幕...")
        segments = processVideofiletoTexts("", audio_path)

        # 4. 写入双语字幕
        srt_filename = f"{safe_filename_prefix}.srt"
        print("📄 正在写入双语字幕文件...")
        await write_bilingual_srt(
            segments=segments,
            original_language=original_language,
            target_language=target_language,
            output_dir=output_dir,
            output_path=srt_filename,
            batch_size=batch_size,
            overwrite_mode=overwrite_mode
        )

        final_srt_path = os.path.join(output_dir, srt_filename)
        print(f"🎉 处理完成！字幕文件已保存至：{final_srt_path}")
        return final_srt_path

    except Exception as e:
        print(f"❌ 处理失败：{e}")
        raise

def generate_safe_filename_from_url(url: str) -> str:
    """
    根据 URL 生成安全的文件名前缀
    :param url: 视频链接
    :return: 安全的文件名前缀
    """
    # 使用 MD5 哈希算法生成固定长度的字符串，保证文件名的安全性和唯一性
    hash_object = hashlib.md5(url.encode())
    return hash_object.hexdigest()