import os
import torch
import time

import asyncio
from typing import IO
from pydub import AudioSegment
import whisper.whisper as whisper
import urllib.request
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain_openai import OpenAI, ChatOpenAI
from typing import List,Dict
from urllib.parse import urlparse
from dotenv import load_dotenv
from youtube_video_download import download_youtube_audio,add_suffix_to_filename

load_dotenv(".env")

proxy_host = os.getenv("PROXY_HOST")
proxy_port = os.getenv("PROXY_PORT")
proxy_url= os.getenv("PROXY_URL")

model=os.getenv("LLM_MODEL_NAME")
api_key=os.getenv("LLM_MODEL_API_KEY")
api_base=os.getenv("LLM_MODEL_BASE_URL")
# 设置代理
proxies = {
    "http": f"http://{proxy_host}:{proxy_port}",
    "https": f"http://{proxy_host}:{proxy_port}",
}
proxy_handler = urllib.request.ProxyHandler(proxies)

def format_timestamp(seconds: float) -> str:
    milliseconds = int(seconds * 1000)
    hours = milliseconds // 3_600_000
    milliseconds %= 3_600_000
    minutes = milliseconds // 60_000
    milliseconds %= 60_000
    seconds = milliseconds // 1_000
    milliseconds %= 1_000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
def transcribe30s(model_name:str="turbo", audio_path:str="audio.mp3"):

    model = whisper.load_model(model_name)

    # load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio(audio_path)
    audio = whisper.pad_or_trim(audio)

    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio, n_mels=model.dims.n_mels).to(model.device)

    # detect the spoken language
    _, probs = model.detect_language(mel)
    print(f"Detected language: {max(probs, key=probs.get)}")

    # decode the audio
    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)

    # print the recognized text
    print(result.text)
    return result.text

def get_free_gpu():
    """自动选择一个空闲内存最多的 GPU"""
    if not torch.cuda.is_available():
        return "cpu"
    free_gpus = []
    for i in range(torch.cuda.device_count()):
        try:
            free_mem = torch.cuda.mem_get_info(i)[0]  # 尝试获取内存信息
            free_gpus.append((i, free_mem))
        except Exception as e:
            print(f"无法获取 GPU {i} 的内存信息: {e}")
    if not free_gpus:
        return "cpu"
    free_gpus.sort(key=lambda x: x[1], reverse=True)
    return free_gpus[0][0]

def transcribe(model_name:str="turbo", audio_path:str="audio.mp3"):
    device=os.environ.get("DEVICE",default=get_free_gpu())
    try:
        model = whisper.load_model(name=model_name,device=device)
        result = model.transcribe(audio_path)
        # result["segments"]
        # print(result["segments"])
        segments = merge_duplicate_segments(result["segments"])
        return segments
    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        raise str(e)

def process_YT_video_url(url: str, output_path: str = ".", model_name: str = "turbo"):
    """
    下载YouTube视频/音频，转录为文本，并删除下载的文件。
    :param url: YouTube视频URL
    :param output_path: 文件保存路径
    :param model_name: 使用的Whisper模型名称
    :return: 转录的文本
    """
    file_path = download_youtube_audio(url, output_path, only_audio=True)
    if not file_path:
        raise ValueError("Failed to download the video/audio.")

    try:

        # 调用 Whisper 转录
        text = transcribe(model_name=model_name, audio_path=file_path)

        # 删除临时文件
        os.remove(file_path)
        print(f"🗑️ 已删除文件：{file_path}")

        return text
    except Exception as e:
        print(f"❌ 转录或删除文件时出错：{e}")
        raise

def merge_duplicate_segments(segments):
    merged = []
    prev_seg = None

    for seg in segments:
        text = seg["text"].strip()

        if prev_seg is not None and text == prev_seg["text"].strip():
            # 合并时间范围
            prev_seg["end"] = seg["end"]
            prev_seg["tokens"] += seg["tokens"]
        else:
            if prev_seg is not None:
                merged.append(prev_seg)
            prev_seg = seg.copy()  # 深拷贝确保不引用原对象

    if prev_seg is not None:
        merged.append(prev_seg)

    return merged
def processVideofiletoTexts(filedir:str,filepath: str):

    
    file=os.path.join(filedir,filepath)
    
    return transcribe("turbo",file)


async def translation(text: str,original_language:str,target_language:str)-> str:
    with open("./prompt/translation.md", "r", encoding="utf-8") as file:
        template = file.read()
    llm= ChatOpenAI(
        model_name= model,
        api_key= api_key,
        base_url=api_base,
        )
    agent = create_react_agent(llm,[])
    prompt = template.format(original_language=original_language,target_language=target_language,text=text)
    result = await agent.ainvoke({"messages": [HumanMessage(content=prompt)]})
    return result["messages"][-1].content

async def batch_translate(
    texts: List[str],
    original_language: str,
    target_language: str,
) -> List[str]:
    with open("./prompt/translation.md", "r", encoding="utf-8") as file:
        template = file.read()

    # 构建输入文本
    translation_list = "\n".join([f"{i + 1}. {text}" for i, text in enumerate(texts)])
    final_prompt = template.format(original_language=original_language,target_language=target_language,text=translation_list)

    llm = ChatOpenAI(model_name=model, api_key=api_key, base_url=api_base)
    agent = create_react_agent(llm,[])
    result = await agent.ainvoke({"messages": [HumanMessage(content=final_prompt)]})

    # 拆分结果
    translated_texts = result["messages"][-1].content.strip().split("\n")
    return translated_texts

async def process_batch(
    segments: List[Dict],
    original_language: str,
    target_language: str,
    global_start_idx: int
):
    texts = [seg["text"].strip() for seg in segments]

    try:
        translated_texts = await batch_translate(texts, original_language, target_language)
    except Exception as e:
        print(f"⚠️ 批量翻译失败，改用逐条翻译：{e}")
        translated_texts = []
        for text in texts:
            try:
                translated = await translation(text, original_language, target_language)
                translated_texts.append(translated)
            except Exception as e:
                print(f"❌ 翻译失败：{e}")
                translated_texts.append("[ERROR]")

    results = []
    for idx, segment in enumerate(segments):
        start = format_timestamp(segment["start"])
        end = format_timestamp(segment["end"])
        original_text = segment["text"].strip()
        translated_text = translated_texts[idx] if idx < len(translated_texts) else "[ERROR]"

        # 构造一个包含编号的字幕条目
        global_idx = global_start_idx + idx
        results.append({
            "index": global_idx,
            "start": start,
            "end": end,
            "original": original_text,
            "translated": translated_text
        })

    await asyncio.sleep(1.5)  # 控制速率
    return results  



async def process_segment(segment: Dict, idx: int, original_language: str, target_language: str, file: IO):
    start = format_timestamp(segment["start"])
    end = format_timestamp(segment["end"])
    original_text = segment["text"].strip()

    translated_text = await translation(original_text, original_language, target_language)

    file.write(f"{idx + 1}\n")
    file.write(f"{start} --> {end}\n")
    file.write(f"{original_text}\n")
    file.write(f"{translated_text}\n\n")

async def write_bilingual_srt(
    segments: List[Dict],
    original_language: str,
    target_language: str,
    output_dir: str,
    output_path: str,
    batch_size: int = 5,
    overwrite_mode: str = "overwrite"
):
    file_path = os.path.join(output_dir, output_path)

    os.makedirs(output_dir, exist_ok=True)

    # 处理已存在文件
    if os.path.exists(file_path):
        if overwrite_mode == "skip":
            print(f"⚠️ 文件已存在且设置为跳过：{file_path}")
            return
        elif overwrite_mode == "backup":
            base, ext = os.path.splitext(file_path)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_path = f"{base}_backup_{timestamp}{ext}"
            os.rename(file_path, backup_path)
            print(f"📦 已有文件重命名为备份：{backup_path}")

    # 并发翻译
    all_results = []
    global_index = 1
    tasks = []
    for i in range(0, len(segments), batch_size):
        batch = segments[i:i + batch_size]
        tasks.append(process_batch(batch, original_language, target_language, global_index))
        global_index += len(batch)

    # 并发执行所有翻译任务
    batch_results = await asyncio.gather(*tasks)

    # 合并并排序所有结果
    for result_list in batch_results:
        all_results.extend(result_list)

    # 按 index 排序
    all_results.sort(key=lambda x: x["index"])

    # 写入文件
    with open(file_path, "w", encoding="utf-8") as f:
        for item in all_results:
            f.write(f"{item['index']}\n")
            f.write(f"{item['start']} --> {item['end']}\n")
            f.write(f"{item['original']}\n")
            f.write(f"{item['translated']}\n\n")

    print(f"✅ 双语字幕已保存至：{file_path}")