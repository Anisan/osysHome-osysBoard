import os
from app.core.main.BasePlugin import BasePlugin
from flask import Blueprint
from flask import render_template, send_from_directory
from flask_login import (
    login_required,
)

class osysBoard(BasePlugin):

    def __init__(self,app):
        super().__init__(app,__name__)
        self.title = "osysBoard"
        self.description = """Dashboard for osysHome"""
        self.category = "App"
        self.author = "Eraser"
        self.version = "0.1"
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

    def admin(self, _):
        return render_template("osysBoard.html")
