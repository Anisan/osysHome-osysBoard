import os
import requests
import shutil
import zipfile
from settings import Config
from app.core.main.BasePlugin import BasePlugin
from flask import Blueprint
from flask import render_template, send_from_directory, redirect
from app.api import api
from flask_login import (
    login_required,
)
from app.core.lib.object import getProperty, setProperty

class osysBoard(BasePlugin):

    def __init__(self,app):
        super().__init__(app,__name__)
        self.title = "osysBoard"
        self.description = """Dashboard for osysHome"""
        self.category = "App"
        self.author = "Eraser"
        self.version = "0.1"
        self.actions = ['widget']
        self.path = os.path.dirname(__file__)

        # Создаем Blueprint
        self.client_bp = Blueprint('osysBoard_app', __name__, static_folder=os.path.join(self.path,'dist'))

        @self.client_bp.route('/osysBoard/', methods=['GET'])
        @login_required
        def osysBoard_root():
            # Обработка корневого пути osysBoard
            return send_from_directory(self.client_bp.static_folder, 'index.html')

        @self.client_bp.route('/osysBoard/<path:subpath>')
        @login_required
        def osysBoard_app(subpath):
            # Определяем путь к файлам в папке dist
            file_path = os.path.join(self.client_bp.static_folder, subpath)

            # Если файл существует, возвращаем его
            if os.path.exists(file_path):
                return send_from_directory(self.client_bp.static_folder, subpath)
            else:
                # Если файла нет, возвращаем index.html
                return send_from_directory(self.client_bp.static_folder, 'index.html')

        app.register_blueprint(self.client_bp)

    def initialization(self):
        pass

    def download_and_extract_github_release(self, url):
        local_filename = f"release_osysboard.zip"
        target_folder = os.path.join(Config.PLUGINS_FOLDER, self.name, "dist")
        
        # Скачивание архива
        self.logger.info("Downloading %s...",url)
        response = requests.get(url)
        
        if response.status_code == 200:
            with open(local_filename, 'wb') as f:
                f.write(response.content)
            self.logger.info(f"Downloaded {local_filename}")
        else:
            raise Exception(f"Failed to download the file: {response.status_code}")

        # Удаление предыдущей версии
        shutil.rmtree(target_folder)

        # Создание целевой папки
        os.makedirs(target_folder, exist_ok=True)
        
        # Распаковка архива во временную папку
        
        self.logger.info(f"Extracting {local_filename} to {target_folder}...")
        with zipfile.ZipFile(local_filename, 'r') as zip_ref:
            zip_ref.extractall(target_folder)
        self.logger.info(f"Extracted to {target_folder}")
        
        # Удаление загруженного архива
        os.remove(local_filename)
        self.logger.info(f"Removed {local_filename}")

    def admin(self,request):
        upgrade = request.args.get('upgrade',None)

        if upgrade:
            try:
                url = "http://api.github.com/repos/anisan/osyshome-osysBoard/releases"
                response = requests.get(url)
            
                if response.status_code == 200:
                    versions = response.json()
                    for version in versions:
                        if version['name'] == upgrade:
                            self.download_and_extract_github_release(version['assets'][0]['browser_download_url'])
                            setProperty("SystemVar.osysBoard_version", version['name'])
                            break
            except Exception as ex:
                self.logger.error(f"Error: {ex}")
            return redirect(self.name)

        return render_template("osysBoard.html")
    
    def widget(self):
        try:
            content = {}
            installed = getProperty("SystemVar.osysBoard_version")
            url = "http://api.github.com/repos/anisan/osyshome-osysBoard/releases"
            response = requests.get(url)
        
            if response.status_code == 200:
                versions = response.json()
                latest_version = versions[0]['name']
                if installed != latest_version:
                    content['version'] = latest_version
                    return render_template("widget_osysboard.html", **content)
            else:
                self.logger.debug(response.content)
        except Exception as ex:
            self.logger.error(ex)
        return None
