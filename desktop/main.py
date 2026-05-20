import json
import sys
from pathlib import Path

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from api_client import RivalScopeClient
from styles import APP_STYLE


def resource_path(relative_path: str) -> Path:
    """Return resource path for source run and PyInstaller bundle."""
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.client = RivalScopeClient()
        self.setWindowTitle("RivalScope Desktop")
        self.resize(1180, 760)
        self._build_ui()
        self._check_api()

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)

        header = QHBoxLayout()
        logo = QLabel()
        logo_path = resource_path("assets/logo.png")
        if not logo_path.exists():
            logo_path = Path(__file__).resolve().parent.parent / "frontend" / "assets" / "logo.png"
        if logo_path.exists():
            logo.setPixmap(QPixmap(str(logo_path)).scaledToWidth(90))
        header_text = QVBoxLayout()
        title = QLabel("RivalScope")
        title.setObjectName("Title")
        subtitle = QLabel("AI Competitive Intelligence by NeiroBridge")
        subtitle.setObjectName("Muted")
        header_text.addWidget(title)
        header_text.addWidget(subtitle)
        header.addWidget(logo)
        header.addLayout(header_text)
        header.addStretch()
        layout.addLayout(header)

        context = QHBoxLayout()
        self.niche = QComboBox()
        self.niche.addItems(
            [
                "AI-автоматизация бизнеса",
                "n8n / no-code автоматизация",
                "AI-агенты и чат-боты",
                "дизайн-студия",
                "motion / animation studio",
                "другое",
            ]
        )
        self.custom_niche = QLineEdit()
        self.custom_niche.setPlaceholderText("Своя ниша")
        self.target = QLineEdit()
        self.target.setPlaceholderText("Целевая аудитория")
        context.addWidget(self.niche)
        context.addWidget(self.custom_niche)
        context.addWidget(self.target)
        layout.addLayout(context)

        site_row = QHBoxLayout()
        self.url_input = QLineEdit("https://neirobridge.ru")
        site_btn = QPushButton("Анализ сайта")
        site_btn.clicked.connect(self.analyze_site)
        site_row.addWidget(self.url_input)
        site_row.addWidget(site_btn)
        layout.addLayout(site_row)

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Вставьте текст конкурента для анализа")
        layout.addWidget(self.text_input)

        actions = QHBoxLayout()
        text_btn = QPushButton("Анализ текста")
        text_btn.clicked.connect(self.analyze_text)
        history_btn = QPushButton("История")
        history_btn.clicked.connect(self.load_history)
        open_image_btn = QPushButton("Выбрать изображение")
        open_image_btn.clicked.connect(self.pick_image)
        actions.addWidget(text_btn)
        actions.addWidget(open_image_btn)
        actions.addWidget(history_btn)
        actions.addStretch()
        layout.addLayout(actions)

        self.result = QTextEdit()
        self.result.setReadOnly(True)
        self.result.setPlaceholderText("Результат появится здесь")
        layout.addWidget(self.result, stretch=1)

        self.setCentralWidget(root)

    def _context(self) -> dict:
        return {
            "niche": self.niche.currentText(),
            "custom_niche": self.custom_niche.text() or None,
            "own_brand": "NeiroBridge",
            "own_site": "https://neirobridge.ru",
            "target_audience": self.target.text() or None,
        }

    def _check_api(self) -> None:
        try:
            data = self.client.health()
            self.statusBar().showMessage(f"Backend: {data['status']} | {data['ai_provider']}")
        except Exception:
            self.statusBar().showMessage("Backend недоступен. Сначала запустите python run.py")

    def _show_json(self, data: dict) -> None:
        self.result.setPlainText(json.dumps(data, ensure_ascii=False, indent=2))

    def analyze_text(self) -> None:
        try:
            self._show_json(self.client.analyze_text(self.text_input.toPlainText(), self._context()))
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))

    def analyze_site(self) -> None:
        try:
            self._show_json(self.client.parse_site(self.url_input.text(), self._context()))
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))

    def load_history(self) -> None:
        try:
            self._show_json(self.client.history())
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))

    def pick_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg *.webp)")
        if path:
            QMessageBox.information(
                self,
                "Изображение",
                "В desktop MVP выбран файл. Полный анализ изображений доступен в веб-интерфейсе.",
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
