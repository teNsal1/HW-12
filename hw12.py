import os
import logging
from pprint import pprint
from typing import List, Tuple, Optional
import datetime
import requests
import json
import base64

class TextRequest:
    
    def send(self, text: str, model: str) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": text
                }
            ]
        }
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending text request: {e}")
            return {"error": str(e)}

class ImageRequest:
    
    def encode_image(self, image_path: str) -> Optional[str]:
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            logging.error(f"Error: The file {image_path} was not found.")
            return None
        except Exception as e:
            logging.error(f"Error: {e}")
            return None

    def send(self, text: str, image_path: str, model: str) -> dict:
        base64_image = self.encode_image(image_path)
        if base64_image is None:
            return {"error": "Failed to encode image"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": text
                        },
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    ]
                }
            ]
        }
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending image request: {e}")
            return {"error": str(e)}

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
    api_key = "test_key"
    text_req = TextRequest(api_key)
    img_req = ImageRequest(api_key)
    
    print("Тест текстового запроса:", text_req.send("Привет", "test-model"))
    print("Тест запроса с изображением:", img_req.send("Описание", "test.jpg", "test-model"))