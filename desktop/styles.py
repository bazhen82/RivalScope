APP_STYLE = """
QWidget {
    background: #08111f;
    color: #edf7ff;
    font-family: Segoe UI, Arial;
    font-size: 14px;
}
QFrame {
    background: #101b30;
    border: 1px solid rgba(83, 241, 255, 0.25);
    border-radius: 18px;
}
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a6d8e, stop:1 #244bd9);
    color: white;
    border: 1px solid rgba(83, 241, 255, 0.55);
    border-radius: 12px;
    padding: 10px 14px;
    font-weight: 700;
}
QPushButton:hover {
    background: #2564ff;
}
QLineEdit, QTextEdit, QComboBox {
    background: #091426;
    color: #edf7ff;
    border: 1px solid rgba(83, 241, 255, 0.25);
    border-radius: 12px;
    padding: 9px;
}
QLabel#Title {
    font-size: 28px;
    font-weight: 800;
    color: #53f1ff;
}
QLabel#Muted {
    color: #8ca3bd;
}
"""
