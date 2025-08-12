from dotenv import load_dotenv
from typing import Optional
import os

# 加载 .env 文件（从项目根目录开始）
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))

class Config:
    PROXY_TYPE: Optional[str] = os.getenv("PROXY_TYPE").lower()  # http 
    PROXY_HOST: Optional[str] = os.getenv("PROXY_HOST")
    PROXY_PORT: Optional[int] = int(os.getenv("PROXY_PORT", "0")) if os.getenv("PROXY_PORT") else None
    PROXY_URL: Optional[str] = os.getenv("PROXY_URl")
    
    HTTP_PROXY: Optional[str] = os.getenv("HTTP_PROXY")
    HTTPS_PROXY: Optional[str] = os.getenv("HTTPS_PROXY")
    
    LLM_MODEL_NAME=os.getenv("LLM_MODEL_NAME")
    LLM_MODEL_API_KEY=os.getenv("LLM_MODEL_API_KEY")
    LLM_MODEL_BASE_URL=os.getenv("LLM_MODEL_BASE_URL")
        
    WHISPER_MODEL=os.getenv("WHISPER_MODEL","tiny")
    WHISPER_CACHE=os.getenv("WHISPER_CACHE","")
    DEVICE=os.getenv("DEVICE","auto")
    OUTPUT_DIR=os.getenv("OUTPUT_DIR","./tempfile")
    
    @classmethod
    def get_proxy_dict(cls) -> dict:
        """
        返回标准的 proxy 字典，可用于 requests 或 httpx
        """
        if cls.HTTP_PROXY and cls.HTTPS_PROXY:
            return {
                "http://": cls.HTTP_PROXY,
                "https://": cls.HTTPS_PROXY,
            }
        elif cls.PROXY_TYPE and cls.PROXY_HOST and cls.PROXY_PORT:
            scheme = f"{cls.PROXY_TYPE}://{cls.PROXY_HOST}:{cls.PROXY_PORT}"
            return {
                "http://": scheme,
                "https://": scheme,
            }
        return {}

    @classmethod
    def validate(cls):
        """
        验证必要配置是否已设置
        """
        missing = []
        if not cls.PROXY_URL:
            missing.append("PROXY_URL")
        if not cls.LLM_MODEL_NAME:
            missing.append("LLM_MODEL_NAME")


        if missing:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

config = Config()