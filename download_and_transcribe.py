#!/usr/bin/env python3
"""
python download_and_transcribe.py \
    --url https://www.youtube.com/watch?v=LPZh9BOjkQs \
    --output-dir ./tempfile \
    --download-audio \
    --original-language English \
    --target-language Chinese

"""


import argparse
import asyncio
import os

from processYoutube import process_youtube_video

def main():
    parser = argparse.ArgumentParser(description="下载 YouTube 视频并使用 Whisper 生成字幕")

    parser.add_argument("--url", required=True, help="YouTube 视频地址")
    parser.add_argument("--output-dir", default="./tempfile", help="输出目录（默认：./tempfile）")
    parser.add_argument("--download-audio", action="store_true", help="是否下载音频（否则下载视频）")
    parser.add_argument("--original-language", default="English", help="原始语言（Whisper 使用，默认 English）")
    parser.add_argument("--target-language", default="Chinese", help="目标语言（翻译目标，默认 Chinese）")

    args = parser.parse_args()

    # 创建输出目录（如果不存在）
    os.makedirs(args.output_dir, exist_ok=True)

    # 执行异步处理
    try:
        print("⬇️ 开始下载视频/音频并处理字幕...")
        asyncio.run(
            process_youtube_video(
                url=args.url,
                output_dir=args.output_dir,
                download_audio=args.download_audio,
                original_language=args.original_language,
                target_language=args.target_language
            )
        )
        print("✅ 处理完成！")
    except Exception as e:
        print(f"❌ 处理失败: {e}")


if __name__ == "__main__":
    main()