import os
import logging
from pprint import pprint
from typing import List, Tuple, Optional
import datetime
import requests
import json
import base64

class TextRequest:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_url = "https://api.mistral.ai/v1/chat/completions"

    def send(self, text: str, model: str) -> dict:
        """Отправка текстового запроса"""
        return {}

class ImageRequest:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_url = "https://api.mistral.ai/v1/chat/completions"

    def encode_image(self, image_path: str) -> Optional[str]:
        """Кодирование изображения в base64"""
        return None

    def send(self, text: str, image_path: str, model: str) -> dict:
        """Отправка запроса с изображением"""
        return {}

class ChatFacade:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.text_request = TextRequest(api_key)
        self.image_request = ImageRequest(api_key)
        self.history: List[Tuple[str, dict]] = []
        self.models = {
            1: ["mistral-large-latest", "mistral-small-latest"],
            2: ["pixtral-12b-2409"]
        }

    def select_mode(self) -> int:
        """Выбор типа запроса"""
        return 1

    def select_model(self, mode: int) -> str:
        """Выбор модели"""
        return ""

    def load_image(self, image_path: str) -> str:
        """Загрузка изображения"""
        return ""

    def ask_question(self, text: str, model: str, image_path: Optional[str] = None) -> dict:
        """Отправка запроса"""
        return {}

    def get_history(self) -> List[Tuple[str, dict]]:
        """История запросов"""
        return []

    def clear_history(self) -> None:
        """Очистка истории"""
        pass

if __name__ == "__main__":
    print("Базовая структура создана")