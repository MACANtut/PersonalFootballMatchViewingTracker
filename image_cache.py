from PySide6.QtGui import QPixmap
from PySide6.QtCore import QTimer
import requests
from io import BytesIO
import os
import hashlib

class ImageCache:
    """Кэш для изображений с отложенной загрузкой"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.cache = {}
        self.pending_loads = {}
        self.cache_dir = "image_cache"
        
        # Создаем директорию для кэша если её нет
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_cache_path(self, url):
        """Возвращает путь к файлу кэша для URL"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        ext = url.split('.')[-1].lower()
        if ext not in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            ext = 'png'
        return os.path.join(self.cache_dir, f"{url_hash}.{ext}")
    
    def load_from_cache(self, url):
        """Загружает изображение из файлового кэша"""
        cache_path = self._get_cache_path(url)
        if os.path.exists(cache_path):
            pixmap = QPixmap(cache_path)
            if not pixmap.isNull():
                return pixmap
        return None
    
    def save_to_cache(self, url, pixmap):
        """Сохраняет изображение в файловый кэш"""
        if pixmap and not pixmap.isNull():
            cache_path = self._get_cache_path(url)
            pixmap.save(cache_path)
    
    def _load_image_sync(self, url):
        """Синхронная загрузка изображения"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                image_data = BytesIO(response.content)
                pixmap = QPixmap()
                pixmap.loadFromData(image_data.getvalue())
                if not pixmap.isNull():
                    return pixmap
            return None
        except Exception as e:
            print(f"Ошибка загрузки {url}: {e}")
            return None
    
    def get_image(self, url, callback, force_reload=False):
        """
        Асинхронно получает изображение (через QTimer для неблокировки UI)
        callback: функция, которая будет вызвана с pixmap
        """
        if not url:
            callback(None)
            return
        
        # Проверяем память
        if url in self.cache and not force_reload:
            callback(self.cache[url])
            return
        
        # Проверяем файловый кэш
        cached = self.load_from_cache(url)
        if cached and not force_reload:
            self.cache[url] = cached
            callback(cached)
            return
        
        # Загружаем синхронно, но через QTimer чтобы не блокировать UI
        def do_load():
            pixmap = self._load_image_sync(url)
            if pixmap:
                self.cache[url] = pixmap
                self.save_to_cache(url, pixmap)
            callback(pixmap)
        
        QTimer.singleShot(10, do_load)


# Глобальный экземпляр кэша
image_cache = ImageCache()