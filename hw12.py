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
        """Инициализация класса с API-ключом."""
        self.api_key = api_key
        self.base_url = "https://api.mistral.ai/v1/chat/completions"  # Предполагаемый URL API

    def send(self, text: str, model: str) -> dict:
        """
        Отправка текстового запроса к API Mistral.

        Args:
            text (str): Текст запроса.
            model (str): Название модели.

        Returns:
            dict: Ответ от API.
        """
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
            response.raise_for_status()  # Проверка на ошибки HTTP
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending text request: {e}")
            return {"error": str(e)}

class ImageRequest:
    def __init__(self, api_key: str) -> None:
        """Инициализация класса с API-ключом."""
        self.api_key = api_key
        self.base_url = "https://api.mistral.ai/v1/chat/completions"  # Предполагаемый URL API

    def encode_image(self, image_path: str) -> Optional[str]:
        """
        Переводит изображение в формат base64.

        Args:
            image_path (str): Путь к изображению.

        Returns:
            Optional[str]: Изображение в формате base64 или None в случае ошибки.
        """
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
        """
        Отправка запроса с изображением.

        Args:
            text (str): Текст запроса.
            image_path (str): Путь к изображению.
            model (str): Название модели.

        Returns:
            dict: Ответ от API.
        """
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
        """Инициализация фасада с API-ключом."""
        self.api_key = api_key
        self.text_request = TextRequest(api_key)
        self.image_request = ImageRequest(api_key)
        self.history: List[Tuple[str, dict]] = []
        self.models = {
            1: ["mistral-large-latest", "mistral-small-latest"],  # Текстовые модели
            2: ["pixtral-12b-2409"]  # Модели для изображений
        }

    def select_mode(self) -> int:
        """
        Предоставляет пользователю выбор типа запроса.

        Returns:
            int: Выбранный режим (1 или 2).
        """
        print("Выберите тип запроса:")
        print("1. Текстовый запрос")
        print("2. Запрос с изображением")
        while True:
            try:
                mode = int(input("Введите номер режима (1 или 2): "))
                if mode in [1, 2]:
                    return mode
                else:
                    print("Пожалуйста, введите 1 или 2.")
            except ValueError:
                print("Пожалуйста, введите число.")

    def select_model(self, mode: int) -> str:
        """
        Позволяет выбрать модель из списка, соответствующую выбранному режиму.

        Args:
            mode (int): Выбранный режим (1 или 2).

        Returns:
            str: Название выбранной модели.
        """
        available_models = self.models.get(mode, [])
        if not available_models:
            print("Нет доступных моделей для выбранного режима.")
            return ""

        print(f"Доступные модели для режима {mode}:")
        for i, model in enumerate(available_models, 1):
            print(f"{i}. {model}")

        while True:
            try:
                choice = int(input("Введите номер модели: "))
                if 1 <= choice <= len(available_models):
                    return available_models[choice - 1]
                else:
                    print(f"Пожалуйста, введите число от 1 до {len(available_models)}.")
            except ValueError:
                print("Пожалуйста, введите число.")

    def load_image(self, image_path: str) -> str:
        """
        Метод для загрузки изображения (если выбран режим с изображением).

        Args:
            image_path (str): Путь к изображению.

        Returns:
            str: Путь к изображению.

        Raises:
            FileNotFoundError: Если файл не найден.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Файл {image_path} не найден.")
        return image_path

    def ask_question(self, text: str, model: str, image_path: Optional[str] = None) -> dict:
        """
        Основной метод для отправки запроса.

        Args:
            text (str): Текст запроса.
            model (str): Название модели.
            image_path (Optional[str]): Путь к изображению (опционально).

        Returns:
            dict: Ответ от API.
        """
        if not text.strip():
            raise ValueError("Текст запроса не может быть пустым.")

        if image_path:
            response = self.image_request.send(text, image_path, model)
        else:
            response = self.text_request.send(text, model)

        self.history.append((text, response))
        return response

    def get_history(self) -> List[Tuple[str, dict]]:
        """
        Возвращает историю запросов и ответов.

        Returns:
            List[Tuple[str, dict]]: История запросов и ответов.
        """
        return self.history

    def clear_history(self) -> None:
        """Очищает историю сообщений."""
        self.history.clear()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    api_key = os.getenv("MISTRAL_API_KEY", "")
    chat = ChatFacade(api_key)

    mode = chat.select_mode()
    model = chat.select_model(mode)
    image_path = None

    if mode == 2:
        image_path = input("Введите путь к изображению: ")
        try:
            image_path = chat.load_image(image_path)
        except FileNotFoundError as e:
            logging.error(e)
            exit(1)

    text_question = input("Введите ваш вопрос: ")
    try:
        response = chat.ask_question(text_question, model, image_path)
        
        # Извлекаем и выводим только текст ответа
        if "choices" in response:
            answer = response["choices"][0]["message"]["content"]
            print("\nОтвет от API:")
            print(answer)
        else:
            print("Ошибка в структуре ответа:")
            pprint(response)

        # Проверка временной метки
        created_timestamp = response.get('created', 0)
        current_time = datetime.datetime.now().timestamp()
        if created_timestamp > current_time:
            print("Предупреждение: временная метка ответа указывает на будущее.")

        # Улучшенный вывод истории
        print("\nИстория запросов:")
        for i, (question, resp) in enumerate(chat.get_history(), 1):
            print(f"{i}. Вопрос: {question}")
            if "choices" in resp:
                answer = resp["choices"][0]["message"]["content"]
                print(f"   Ответ: {answer}")
            else:
                print(f"   Ошибка: {resp.get('error', 'Неизвестная ошибка')}")
            print()

    except ValueError as e:
        logging.error(e)