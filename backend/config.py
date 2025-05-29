from pydantic import BaseModel, validator
from typing import Optional
import os
import yaml
from pathlib import Path

class Config(BaseModel):
    apikey: str  # 与yaml文件中的字段名保持一致

    @validator('apikey')
    def api_key_not_empty(cls, v):
        if not v:
            raise ValueError('API key cannot be empty')
        return v

def load_config(path: str) -> Config:
    """从YAML文件加载配置，支持环境变量覆盖"""
    config_data = {}
    
    # 从YAML文件加载
    if path:
        abs_path = Path(path).absolute()
        with open(abs_path, 'r') as f:
            config_data = yaml.safe_load(f) or {}
    
    # 应用环境变量覆盖
    if 'DEEPSEEK_API_KEY' in os.environ:
        config_data['apikey'] = os.environ['DEEPSEEK_API_KEY']
    
    # 验证并返回配置
    return Config(**config_data)

def save_sample_config(path: str) -> None:
    """生成示例配置文件"""
    sample = {'api_key': 'your-api-key-here'}
    with open(path, 'w') as f:
        yaml.dump(sample, f)

__all__ = ['Config', 'load_config', 'save_sample_config']
