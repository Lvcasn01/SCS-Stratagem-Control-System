import sys
import time
import threading
import random
import json
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QMessageBox, QFileDialog,
    QTabWidget, QDoubleSpinBox, QDialog, QListWidget, QListWidgetItem, QComboBox,
    QSizePolicy, QMenu, QCheckBox, QSlider
)
from PyQt6.QtGui import QIcon, QKeySequence, QPainter, QColor, QBrush, QAction
from PyQt6.QtCore import pyqtSignal, QObject, Qt, QTimer, QPoint

# --- Import necessary input libraries ---
import pyautogui
import pydirectinput
from pynput import keyboard, mouse

# --- Default Configuration ---
DEFAULT_STRATAGEM_ACTIVATION_DELAY = 0.08
DEFAULT_PYDIRECTINPUT_PAUSE = 0.05
DEFAULT_REMINDER_OPACITY = 0.5
PROFILES_DIR = "stratagem_profiles"

# Set the initial internal pause for the input library
pydirectinput.PAUSE = DEFAULT_PYDIRECTINPUT_PAUSE

# --- Helper function for PyInstaller to find resources ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Stratagem Data (Updated) ---
ALL_STRATAGEMS = {
    # Mission Stratagems
    "Reinforce": "UDRLU",
    "Resupply": "DDUR",
    "SOS Beacon": "UDLU",
    "Super Earth Flag": "DUDU",
    "Hellbomb": "DULDURDU",
    "Seismic Probe": "UULRRR",
    "SSSD Delivery": "DDDUU",
    "Prospecting Drill": "DDLRRD",
    "Upload Data": "LRUUU",
    "Dark Fluid Vessel": "DDUDLD",
    "Tectonic Drill": "DDURRD",
    "Hive Breaker Drill": "DDDLDR",
    # Orbital Cannons
    "Orbital Precision Strike": "RRU",
    "Orbital Gatling Barrage": "RDLUU",
    "Orbital Airburst Strike": "RRR",
    "Orbital 120MM HE Barrage": "RDDLDRDD",
    "Orbital 380MM HE Barrage": "RDUULDD",
    "Orbital Walking Barrage": "RDRDRD",
    "Orbital Laser": "RDULR",
    "Orbital Railcannon Strike": "RUDDR",
    "Orbital Gas Strike": "RRDR",
    "Orbital EMS Strike": "RRLD",
    "Orbital Smoke Strike": "RRDU",
    "Orbital Napalm Barrage": "RRDLUR",
    "Orbital Illumination Flare": "RRLL",
    "SEAF Artillery": "RUUD",
    # Eagle-1
    "Eagle Rearm": "UULUR",
    "Eagle Strafing Run": "URR",
    "Eagle Airstrike": "URDR",
    "Eagle Cluster Bomb": "URDDR",
    "Eagle Napalm Airstrike": "URDU",
    "Eagle Smoke Strike": "URUD",
    "Eagle 110MM Rocket Pods": "URUL",
    "Eagle 500kg Bomb": "URDDD",
    # Support Weapons
    "Machine Gun": "DLDRU",
    "Anti-Materiel Rifle": "DLRUD",
    "Stalwart": "DLDUUL",
    "Expendable Anti-Tank": "DDLUR",
    "Recoilless Rifle": "DLRRL",
    "Flamethrower": "DLURD",
    "Autocannon": "DLDUUR",
    "Heavy Machine Gun": "DLUDD",
    "Railgun": "DRDULR",
    "Spear": "DDUDD",
    "Grenade Launcher": "DLULD",
    "Laser Cannon": "DLDUL",
    "Arc Thrower": "DRDULR",
    "Quasar Cannon": "DDULR",
    "Airburst Rocket Launcher": "DLUUR",
    "MLS-4X Commando": "DDUL",
    "SM-63 W.A.S.P. Launcher": "DLURR",
    "TX-41 Sterilizer": "DLUDL",
    "GL-52 De-Escalator": "DLUDLL",
    "CDC-1 One True Flag": "DUUDU",
    # Turrets and Emplacements
    "Machine Gun Sentry": "DURRU",
    "Gatling Sentry": "DURL",
    "Mortar Sentry": "DURRD",
    "Autocannon Sentry": "DURULU",
    "Rocket Sentry": "DURRL",
    "EMS Mortar Sentry": "DURDR",
    "HMG Emplacement": "DULRRL",
    "Shield Generator Relay": "DDLRLR",
    "Tesla Tower": "DURULR",
    "E/GL-21 Grenadier Emplacement": "DULDRR",
    "E/AT-12 Anti-Tank Emplacement": "DULRUD",
    "A-FLAM-40 Flame Sentry": "DULUR",
    # Mines
    "Anti-Personnel Minefield": "DLUR",
    "Incendiary Mines": "DLLD",
    "Anti-Tank Mines": "DLUU",
    "MD-B Gas Mines": "DLRD",
    # Backpacks
    "Jump Pack": "DUUDU",
    "LIFT-660 Hover Pack": "DULUU",
    "Supply Pack": "DLDUUD",
    "Guard Dog": "DULURD",
    "Guard Dog Rover": "DULURR",
    "Ballistic Shield Backpack": "DLDDUL",
    "Shield Generator Pack": "DULRLR",
    "AX/ARC-9 \"Guard Dog\" K-9": "DULURU",
    "AD/TX-13 \"Guard Dog\" Dog Breath": "DULURDU",
    "SH-51 Directional Shield": "DLUUR",
    "B-100 Portable Hellbomb": "DLDULR",
    # Vehicles and Mechs
    "Patriot Exosuit": "LDRULDD",
    "EXO-49 Emancipator Exosuit": "LDRULDU",
    "M-102 Fast Recon Vehicle": "DRURD",
}

CATEGORIZED_STRATAGEMS = {
    "Mission Stratagems": [
        "Reinforce", "Resupply", "SOS Beacon", "Super Earth Flag", "Hellbomb",
        "Seismic Probe", "SSSD Delivery", "Prospecting Drill", "Upload Data",
        "Dark Fluid Vessel", "Tectonic Drill", "Hive Breaker Drill", "SEAF Artillery"
    ],
    "Orbital Cannons": [
        "Orbital Precision Strike", "Orbital Gatling Barrage", "Orbital Airburst Strike",
        "Orbital 120MM HE Barrage", "Orbital 380MM HE Barrage", "Orbital Walking Barrage",
        "Orbital Laser", "Orbital Railcannon Strike", "Orbital Gas Strike",
        "Orbital EMS Strike", "Orbital Smoke Strike", "Orbital Napalm Barrage",
        "Orbital Illumination Flare"
    ],
    "Eagle-1": [
        "Eagle Rearm", "Eagle Strafing Run", "Eagle Airstrike", "Eagle Cluster Bomb",
        "Eagle Napalm Airstrike", "Eagle Smoke Strike", "Eagle 110MM Rocket Pods", "Eagle 500kg Bomb"
    ],
    "Support Weapons": [
        "Machine Gun", "Anti-Materiel Rifle", "Stalwart", "Expendable Anti-Tank",
        "Recoilless Rifle", "Flamethrower", "Autocannon", "Heavy Machine Gun", "Railgun",
        "Spear", "Grenade Launcher", "Laser Cannon", "Arc Thrower", "Quasar Cannon",
        "Airburst Rocket Launcher", "MLS-4X Commando", "SM-63 W.A.S.P. Launcher",
        "TX-41 Sterilizer", "GL-52 De-Escalator", "CDC-1 One True Flag"
    ],
    "Turrets and Emplacements": [
        "Machine Gun Sentry", "Gatling Sentry", "Mortar Sentry", "Autocannon Sentry",
        "Rocket Sentry", "EMS Mortar Sentry", "HMG Emplacement", "Shield Generator Relay",
        "Tesla Tower", "E/GL-21 Grenadier Emplacement", "E/AT-12 Anti-Tank Emplacement",
        "A-FLAM-40 Flame Sentry"
    ],
    "Mines": [
        "Anti-Personnel Minefield", "Incendiary Mines", "Anti-Tank Mines", "MD-B Gas Mines"
    ],
    "Backpacks": [
        "Jump Pack", "LIFT-660 Hover Pack", "Supply Pack", "Guard Dog", "Guard Dog Rover",
        "Ballistic Shield Backpack", "Shield Generator Pack", "AX/ARC-9 \"Guard Dog\" K-9",
        "AD/TX-13 \"Guard Dog\" Dog Breath", "SH-51 Directional Shield", "B-100 Portable Hellbomb"
    ],
    "Vehicles and Mechs": [
        "Patriot Exosuit", "EXO-49 Emancipator Exosuit", "M-102 Fast Recon Vehicle"
    ]
}

# --- UI Classes ---

class ReminderWindow(QWidget):
    """A small, always-on-top window to display the current hotkey bindings."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.label = QLabel("No hotkeys set.")
        self.label.setStyleSheet("color: white; font-size: 9pt;")
        self.layout.addWidget(self.label)
        self._drag_pos = None

    def update_reminders(self, hotkeys_dict):
        reminder_text = ""
        if not hotkeys_dict:
            reminder_text = "No hotkeys set."
        else:
            for hotkey, (stratagem_name, _) in hotkeys_dict.items():
                reminder_text += f"<b>{hotkey.upper()}:</b> {stratagem_name}<br>"
        self.label.setText(reminder_text)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(34, 35, 35, 200)) # Semi-transparent dark background
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()

class StatusIndicator(QWidget):
    """A small, borderless, 'always on top' widget that shows a colored circle."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(10, 10)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.is_on = False
        self._drag_pos = None

    def set_status(self, is_on):
        self.is_on = is_on
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(StratagemMacroApp.HELLDIVER_GREEN) if self.is_on else QColor(StratagemMacroApp.HELLDIVER_RED)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(self.rect())
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()

class SettingsDialog(QDialog):
    """A dialog for configuring global settings."""
    def __init__(self, main_app, parent=None):
        super().__init__(parent)
        self.main_app = main_app
        self.setWindowTitle("Settings")
        self.setModal(True)
        
        layout = QGridLayout(self)
        layout.setSpacing(15)

        # Stratagem Menu Key
        menu_key_label = QLabel("<b>Stratagem Menu Key:</b>")
        menu_key_label.setToolTip("The key you hold to open the stratagem menu in-game.")
        layout.addWidget(menu_key_label, 0, 0)
        self.menu_key_input = HotkeyLineEdit(allow_modifiers=True)
        self.menu_key_input.setToolTip(menu_key_label.toolTip())
        self.menu_key_input.setText(self.main_app.stratagem_menu_key)
        layout.addWidget(self.menu_key_input, 0, 1)

        # Global Toggle Hotkey
        toggle_label = QLabel("<b>Global Toggle Hotkey:</b>")
        toggle_label.setToolTip("Set a single key to start/stop the macro from anywhere.")
        layout.addWidget(toggle_label, 1, 0)
        self.global_toggle_hotkey_input = HotkeyLineEdit()
        self.global_toggle_hotkey_input.setToolTip(toggle_label.toolTip())
        self.global_toggle_hotkey_input.setText(self.main_app.global_toggle_hotkey)
        layout.addWidget(self.global_toggle_hotkey_input, 1, 1)
        
        # Activation Delay
        activation_label = QLabel("<b>Activation Delay (sec):</b>")
        activation_label.setToolTip("Pause after holding the stratagem key before input begins.")
        layout.addWidget(activation_label, 2, 0)
        self.delay_spinbox = QDoubleSpinBox()
        self.delay_spinbox.setToolTip(activation_label.toolTip())
        self.delay_spinbox.setRange(0.0, 5.0)
        self.delay_spinbox.setSingleStep(0.01)
        self.delay_spinbox.setValue(self.main_app.stratagem_activation_delay)
        layout.addWidget(self.delay_spinbox, 2, 1)
        
        # Internal Delay
        internal_delay_label = QLabel("<b>Internal Key Press Delay (sec):</b>")
        internal_delay_label.setToolTip("Delay between each arrow/WASD key press. Lower is faster.")
        layout.addWidget(internal_delay_label, 3, 0)
        self.pydirectinput_pause_spinbox = QDoubleSpinBox()
        self.pydirectinput_pause_spinbox.setToolTip(internal_delay_label.toolTip())
        self.pydirectinput_pause_spinbox.setRange(0.0, 2.0)
        self.pydirectinput_pause_spinbox.setSingleStep(0.005)
        self.pydirectinput_pause_spinbox.setValue(pydirectinput.PAUSE)
        layout.addWidget(self.pydirectinput_pause_spinbox, 3, 1)

        # WASD Toggle
        self.wasd_checkbox = QCheckBox("Use WASD for Stratagem Input")
        self.wasd_checkbox.setToolTip("If checked, macros will use WASD instead of arrow keys.")
        self.wasd_checkbox.setChecked(self.main_app.use_wasd_input)
        layout.addWidget(self.wasd_checkbox, 4, 0, 1, 2)

        # Reminder Opacity
        opacity_label = QLabel("<b>Reminder Opacity:</b>")
        layout.addWidget(opacity_label, 5, 0)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(20, 100)
        self.opacity_slider.setValue(int(self.main_app.reminder_opacity * 100))
        self.opacity_slider.valueChanged.connect(self.update_opacity)
        layout.addWidget(self.opacity_slider, 5, 1)

        # OK Button
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout, 6, 0, 1, 2)
        
        self.accepted.connect(self.apply_settings)

    def update_opacity(self, value):
        self.main_app.set_reminder_opacity(value / 100.0)

    def apply_settings(self):
        """Apply the chosen settings back to the main application."""
        self.main_app.stratagem_menu_key = self.menu_key_input.text() or 'ctrl'
        self.main_app.global_toggle_hotkey = self.global_toggle_hotkey_input.text()
        self.main_app.stratagem_activation_delay = self.delay_spinbox.value()
        self.main_app.use_wasd_input = self.wasd_checkbox.isChecked()
        pydirectinput.PAUSE = self.pydirectinput_pause_spinbox.value()

class HotkeyLineEdit(QLineEdit):
    """A custom QLineEdit that captures keyboard and mouse hotkeys."""
    MOUSE_QT_MAP = {
        Qt.MouseButton.LeftButton: "left",
        Qt.MouseButton.RightButton: "right",
        Qt.MouseButton.MiddleButton: "middle",
        Qt.MouseButton.XButton1: "xbutton1",
        Qt.MouseButton.XButton2: "xbutton2",
    }

    def __init__(self, allow_modifiers=False, parent=None):
        super().__init__(parent)
        self.is_capturing = False
        self.allow_modifiers = allow_modifiers
        self.setPlaceholderText("Not Set")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def mousePressEvent(self, event):
        if self.is_capturing:
            button = event.button()
            if button in self.MOUSE_QT_MAP:
                self.setText(f"mouse_{self.MOUSE_QT_MAP[button]}")
                self.is_capturing = False
                self.clearFocus()
        else:
            self.is_capturing = True
            self.setText("Press key...")
            self.selectAll()
            self.setFocus()

    def focusOutEvent(self, event):
        self.is_capturing = False
        if "Press key" in self.text():
            self.clear()
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        if self.is_capturing:
            key = event.key()
            if not self.allow_modifiers and key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
                return
            
            if self.allow_modifiers and key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
                key_text_map = {Qt.Key.Key_Control: 'ctrl', Qt.Key.Key_Shift: 'shift', Qt.Key.Key_Alt: 'alt'}
                self.setText(key_text_map.get(key, ''))
                self.is_capturing = False
                self.clearFocus()
                return

            if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
                 self.setText(f"num_{event.text()}")
            else:
                key_sequence = QKeySequence(key)
                text = key_sequence.toString(QKeySequence.SequenceFormat.NativeText).lower()
                if text:
                    self.setText(text)

            self.is_capturing = False
            self.clearFocus()
        else:
            super().keyPressEvent(event)

class HotkeySlot(QWidget):
    """A self-contained widget for a single hotkey slot."""
    stratagem_changed = pyqtSignal()
    hotkey_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.stratagem_button = QPushButton("--- EMPTY ---")
        self.stratagem_button.clicked.connect(self.open_stratagem_menu)
        layout.addWidget(self.stratagem_button)

        self.hotkey_input = HotkeyLineEdit()
        self.hotkey_input.textChanged.connect(self.hotkey_changed.emit)
        layout.addWidget(self.hotkey_input)

    def open_stratagem_menu(self):
        menu = self.create_stratagem_menu()
        menu.exec(self.stratagem_button.mapToGlobal(QPoint(0, self.stratagem_button.height())))

    def create_stratagem_menu(self):
        menu = QMenu(self)
        for category, stratagems in CATEGORIZED_STRATAGEMS.items():
            category_menu = menu.addMenu(category)
            for name in sorted(stratagems):
                action = QAction(name, self)
                action.triggered.connect(lambda _, n=name: self.set_stratagem(n))
                category_menu.addAction(action)
        return menu

    def set_stratagem(self, name):
        self.stratagem_button.setText(name)
        self.stratagem_changed.emit()
    
    def get_stratagem(self):
        text = self.stratagem_button.text()
        return text if text != "--- EMPTY ---" else ""

    def get_hotkey(self):
        return self.hotkey_input.text()
    
    def set_hotkey(self, text):
        self.hotkey_input.setText(text)

    def clear_slot(self):
        self.stratagem_button.setText("--- EMPTY ---")
        self.hotkey_input.clear()
    
    def set_duplicate_style(self, is_duplicate):
        self.hotkey_input.setObjectName("duplicate" if is_duplicate else "")
        self.hotkey_input.style().polish(self.hotkey_input)

class WorkerSignals(QObject):
    """Defines signals available from a running worker thread."""
    update_status = pyqtSignal(str, str)
    update_reminders = pyqtSignal(dict)

class StratagemMacroApp(QMainWindow):
    """Main application window for the Stratagem Macro."""
    # --- Themed Color Constants ---
    HELLDIVER_YELLOW = "#ffb400"
    HELLDIVER_YELLOW_HOVER = "#ba8000"
    HELLDIVER_DARK_BG = "#222323"
    HELLDIVER_LIGHT_BG = "#3c3d3d"
    HELLDIVER_TEXT_LIGHT = "#f0f0f0"
    HELLDIVER_RED = "#e74c3c"
    HELLDIVER_RED_HOVER = "#c0392b"
    HELLDIVER_GREEN = "#2ecc71"
    BLUE_STATUS = "#3498db"

    def __init__(self):
        super().__init__()
        # Application State & Settings
        self.is_running = False
        self.stratagems_to_execute = {}
        self.stratagem_menu_key = 'ctrl'
        self.global_toggle_hotkey = ""
        self.use_wasd_input = False
        self.stratagem_activation_delay = DEFAULT_STRATAGEM_ACTIVATION_DELAY
        self.reminder_opacity = DEFAULT_REMINDER_OPACITY
        
        # System & UI Components
        self.keyboard_listener = None
        self.mouse_listener = None
        self.signals = WorkerSignals()
        self.status_indicator_window = None
        self.reminder_window = None
        self.hotkey_slots = []
        
        self.initUI()
        self.start_global_listeners()
        self.populate_profiles_dropdown()
        self.validate_hotkeys() 

    def initUI(self):
        """Initialize the 'Tool Panel' user interface."""
        self.setWindowTitle('Helldivers 2 Stratagem Macro')
        self.setMinimumWidth(800)
        self.setWindowIcon(QIcon(resource_path("icon.ico")))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 5, 10, 10)
        
        self.setup_styles(central_widget)
        
        self.init_toolbar(main_layout)
        main_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine))
        self.init_hotkey_grid(main_layout)
        main_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine))
        self.init_control_area(main_layout)
        
        self.signals.update_status.connect(self.update_status_label)
        self.signals.update_reminders.connect(self.update_reminder_data)
        self.show()

    def init_toolbar(self, parent_layout):
        """Initialize the top toolbar for controls."""
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(10)

        self.profiles_combo = QComboBox()
        self.profiles_combo.setMinimumWidth(150)
        self.profiles_combo.setToolTip("Select a profile to load.")
        self.profiles_combo.currentIndexChanged.connect(self.load_selected_profile)
        toolbar_layout.addWidget(self.profiles_combo)

        self.save_profile_button = QPushButton("Save Profile")
        self.save_profile_button.clicked.connect(self.save_current_profile)
        toolbar_layout.addWidget(self.save_profile_button)

        self.delete_profile_button = QPushButton("Delete Profile")
        self.delete_profile_button.clicked.connect(self.delete_selected_profile)
        toolbar_layout.addWidget(self.delete_profile_button)
        
        self.clear_all_button = QPushButton("Clear All")
        self.clear_all_button.setToolTip("Clears all currently configured stratagem slots.")
        self.clear_all_button.clicked.connect(self.clear_all_slots)
        toolbar_layout.addWidget(self.clear_all_button)

        toolbar_layout.addStretch()

        self.reminder_button = QPushButton("📋 Reminder")
        self.reminder_button.setToolTip("Shows/hides the hotkey reminder list.")
        self.reminder_button.clicked.connect(self.toggle_reminder_window)
        toolbar_layout.addWidget(self.reminder_button)

        self.indicator_button = QPushButton("● Status")
        self.indicator_button.setToolTip("Shows/hides a small, always-on-top status window.")
        self.indicator_button.clicked.connect(self.toggle_status_indicator)
        toolbar_layout.addWidget(self.indicator_button)

        self.help_button = QPushButton("? Help")
        self.help_button.setToolTip("Show usage instructions.")
        self.help_button.clicked.connect(self.show_help_dialog)
        toolbar_layout.addWidget(self.help_button)

        self.settings_button = QPushButton("⚙️ Settings")
        self.settings_button.setToolTip("Open the settings dialog.")
        self.settings_button.clicked.connect(self.open_settings_dialog)
        toolbar_layout.addWidget(self.settings_button)

        self.toggle_button = QPushButton('Start Macro')
        self.toggle_button.clicked.connect(self.toggle_macro)
        toolbar_layout.addWidget(self.toggle_button)
        
        parent_layout.addLayout(toolbar_layout)

    def init_hotkey_grid(self, parent_layout):
        """Initialize the grid of hotkey slots."""
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)

        num_slots = 12
        num_cols = 6
        for i in range(num_slots):
            slot = HotkeySlot()
            slot.hotkey_changed.connect(self.validate_and_update)
            slot.stratagem_changed.connect(self.validate_and_update)
            self.hotkey_slots.append(slot)
            row, col = divmod(i, num_cols)
            grid_layout.addWidget(slot, row, col)
            
        parent_layout.addLayout(grid_layout)

    def init_control_area(self, parent_layout):
        """Initialize the bottom status bar."""
        self.status_label = QLabel('Status: Stopped')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"color: {self.HELLDIVER_RED}; font-weight: bold; font-size: 12pt;")
        parent_layout.addWidget(self.status_label)

    def setup_styles(self, parent_widget):
        """Apply a global stylesheet to the application."""
        parent_widget.setStyleSheet(f"""
            QWidget {{ 
                background-color: {self.HELLDIVER_DARK_BG}; 
                color: {self.HELLDIVER_TEXT_LIGHT}; 
            }}
            QLabel {{ font-size: 10pt; }}
            QPushButton {{
                background-color: {self.HELLDIVER_LIGHT_BG}; 
                color: {self.HELLDIVER_TEXT_LIGHT}; 
                padding: 8px;
                border: 1px solid #555;
                border-radius: 5px; 
                font-size: 10pt;
            }}
            QPushButton:hover {{ background-color: #4f5050; }}
            #toggle_button_running {{ 
                background-color: {self.HELLDIVER_GREEN}; 
                color: {self.HELLDIVER_DARK_BG};
                border-color: #27ae60;
                font-weight: bold;
            }}
            #toggle_button_running:hover {{ background-color: #27ae60; }}
            QLineEdit, QDoubleSpinBox, QComboBox, QCheckBox {{
                padding: 5px; 
                border: 1px solid #555; 
                border-radius: 4px;
                background-color: {self.HELLDIVER_DARK_BG}; 
                color: {self.HELLDIVER_TEXT_LIGHT};
            }}
            QLineEdit#duplicate {{
                border: 2px solid {self.HELLDIVER_RED};
            }}
            QFrame {{ background-color: #555; }}
            QDialog {{ background-color: {self.HELLDIVER_DARK_BG}; }}
            QMenu {{
                background-color: {self.HELLDIVER_LIGHT_BG};
                border: 1px solid #555;
            }}
        """)

    # --- Listener and Execution Logic ---
    
    def start_global_listeners(self):
        threading.Thread(target=self._run_keyboard_listener, daemon=True).start()
        threading.Thread(target=self._run_mouse_listener, daemon=True).start()

    def _run_keyboard_listener(self):
        with keyboard.Listener(on_press=self.on_global_press) as listener:
            self.keyboard_listener = listener
            listener.join()
    
    def _run_mouse_listener(self):
        with mouse.Listener(on_click=self.on_global_click) as listener:
            self.mouse_listener = listener
            listener.join()

    def on_global_press(self, key):
        try:
            hotkey_pressed = self.get_key_str_from_pynput(key)
            if not hotkey_pressed: return
            self.handle_hotkey(hotkey_pressed)
        except Exception as e:
            print(f"Error in on_global_press: {e}")

    def on_global_click(self, x, y, button, pressed):
        if not pressed: return
        try:
            hotkey_name = ""
            if button == mouse.Button.left: hotkey_name = "mouse_left"
            elif button == mouse.Button.right: hotkey_name = "mouse_right"
            elif button == mouse.Button.middle: hotkey_name = "mouse_middle"
            elif button == mouse.Button.x1: hotkey_name = "mouse_xbutton1"
            elif button == mouse.Button.x2: hotkey_name = "mouse_xbutton2"
            
            if hotkey_name:
                self.handle_hotkey(hotkey_name)
        except Exception as e:
            print(f"Error in on_global_click: {e}")

    def handle_hotkey(self, hotkey):
        if self.global_toggle_hotkey and hotkey == self.global_toggle_hotkey:
            QTimer.singleShot(0, self.toggle_macro)
            return

        if self.is_running and hotkey in self.stratagems_to_execute:
            name, sequence = self.stratagems_to_execute[hotkey]
            threading.Thread(target=self.execute_stratagem, args=(name, sequence), daemon=True).start()

    def execute_stratagem(self, name, sequence):
        key_map = {'U': 'w', 'D': 's', 'L': 'a', 'R': 'd'} if self.use_wasd_input else {'U': 'up', 'D': 'down', 'L': 'left', 'R': 'right'}
        try:
            self.signals.update_status.emit(f"Executing: {name}", self.BLUE_STATUS)
            pyautogui.keyDown(self.stratagem_menu_key)
            time.sleep(self.stratagem_activation_delay)
            
            for char in sequence:
                if char in key_map: pydirectinput.press(key_map[char])
            
            pyautogui.keyUp(self.stratagem_menu_key)
            QTimer.singleShot(1500, lambda: self.update_ui_for_state() if self.is_running else None)
        except Exception as e:
            print(f"An error during stratagem execution: {e}")
            self.signals.update_status.emit("Execution Error!", self.HELLDIVER_RED)

    # --- Macro State Control ---

    def toggle_macro(self):
        if self.is_running: self.stop_macro()
        else: self.start_macro()

    def start_macro(self):
        self.stratagems_to_execute.clear()
        if self.validate_hotkeys():
             QMessageBox.warning(self, "Duplicate Hotkeys", "Resolve duplicates before starting.")
             return

        for slot in self.hotkey_slots:
            hotkey = slot.get_hotkey().strip().lower()
            stratagem_name = slot.get_stratagem()
            if hotkey and stratagem_name:
                sequence = ALL_STRATAGEMS.get(stratagem_name)
                if sequence:
                    self.stratagems_to_execute[hotkey] = (stratagem_name, sequence)

        if not self.stratagems_to_execute:
            QMessageBox.warning(self, "No Hotkeys Configured", "Configure at least one hotkey.")
            return

        self.is_running = True
        self.update_ui_for_state()

    def stop_macro(self):
        self.is_running = False
        self.update_ui_for_state()
    
    def update_ui_for_state(self):
        """Updates the UI elements based on the current running state."""
        profile_text = self.profiles_combo.currentText()
        if self.is_running:
            self.toggle_button.setText('Stop Macro')
            self.toggle_button.setObjectName('toggle_button_running')
            self.signals.update_status.emit(f"Running | {profile_text}", self.HELLDIVER_GREEN)
            self.set_controls_enabled(False)
        else:
            self.toggle_button.setText('Start Macro')
            self.toggle_button.setObjectName('')
            self.signals.update_status.emit(f"Stopped | {profile_text}", self.HELLDIVER_RED)
            self.set_controls_enabled(True)
        self.toggle_button.style().polish(self.toggle_button)
        
        if self.status_indicator_window:
            self.status_indicator_window.set_status(self.is_running)


    def update_status_label(self, text, color):
        self.status_label.setText(f"Status: {text}")
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12pt;")

    def set_controls_enabled(self, enabled):
        """Enable/disable UI controls to prevent changes while the macro is running."""
        self.profiles_combo.setEnabled(enabled)
        self.save_profile_button.setEnabled(enabled)
        self.delete_profile_button.setEnabled(enabled)
        self.settings_button.setEnabled(enabled)
        self.clear_all_button.setEnabled(enabled)
        self.help_button.setEnabled(enabled)
        self.reminder_button.setEnabled(enabled)
        self.indicator_button.setEnabled(enabled)
        for slot in self.hotkey_slots:
            slot.setEnabled(enabled)

    # --- UI Callbacks & Profile Management ---
    
    def open_settings_dialog(self):
        dialog = SettingsDialog(self)
        dialog.exec()
        
    def toggle_status_indicator(self):
        if not self.status_indicator_window:
            self.status_indicator_window = StatusIndicator()
            self.status_indicator_window.set_status(self.is_running)
            self.status_indicator_window.show()
        else:
            if self.status_indicator_window.isVisible():
                self.status_indicator_window.hide()
            else:
                self.status_indicator_window.show()

    def toggle_reminder_window(self):
        if not self.reminder_window:
            self.reminder_window = ReminderWindow()
            self.signals.update_reminders.connect(self.reminder_window.update_reminders)
            self.update_reminder_data(self.get_active_hotkeys())
            self.set_reminder_opacity(self.reminder_opacity)
        
        if self.reminder_window.isVisible():
            self.reminder_window.hide()
        else:
            self.reminder_window.show()
    
    def set_reminder_opacity(self, opacity):
        self.reminder_opacity = opacity
        if self.reminder_window:
            self.reminder_window.setWindowOpacity(self.reminder_opacity)
    
    def update_reminder_data(self, data):
        if self.reminder_window:
            self.reminder_window.update_reminders(data)

    def get_active_hotkeys(self):
        active = {}
        for slot in self.hotkey_slots:
            hotkey = slot.get_hotkey().strip().lower()
            stratagem = slot.get_stratagem()
            if hotkey and stratagem:
                active[hotkey] = (stratagem, None) # Sequence is not needed for display
        return active
        

    def show_help_dialog(self):
        """Displays a message box with usage instructions."""
        instructions = """
        <h2>How to Use</h2>
        <p><b>Important Game Settings:</b> For best results, go to your in-game keybinds and change the 'Stratagem Menu' key from 'Hold' to 'Press'. It is also suggested to map the four stratagem direction keys to the arrow keys on your keyboard, so you can still move while calling in a stratagem.</p>
        <hr>
        <p><b>1. Setup Your Loadout:</b></p>
        <ul>
            <li>Click an "--- EMPTY ---" button to open the categorized stratagem menu.</li>
            <li>Click the "Not Set" field below it and press any key or mouse button to assign it.</li>
        </ul>
        <p><b>2. Manage Profiles:</b></p>
        <ul>
            <li>Use the dropdown menu to switch between saved profiles.</li>
            <li>To save, select an existing profile to overwrite, or type a new name and click "Save Profile".</li>
        </ul>
        <p><b>3. Configure Settings:</b></p>
        <ul>
            <li>Click the "⚙️ Settings" button to open the settings dialog.</li>
            <li>Here you can set a <b>Global Toggle Hotkey</b>, change the Stratagem Menu key (default: Ctrl), and switch to WASD input.</li>
        </ul>
        <p><b>4. Start the Macro:</b></p>
        <ul>
            <li>Click "Start Macro" or use your global hotkey. The status bar will turn green.</li>
        </ul>
        <hr>
        <p>If you find this tool helpful and would like to show your appreciation, please consider supporting my work. Thank you, Helldiver!</p>
        <p><a href='https://ko-fi.com/lucas_n' style='color: #ffb400;'>ko-fi.com/lucas_n</a></p>
        """
        QMessageBox.information(self, "Help", instructions)

    def validate_and_update(self):
        """Validates hotkeys and updates the reminder window."""
        self.validate_hotkeys()
        self.signals.update_reminders.emit(self.get_active_hotkeys())

    def validate_hotkeys(self):
        hotkey_counts = {}
        for slot in self.hotkey_slots:
            hotkey = slot.get_hotkey().strip().lower()
            if hotkey:
                hotkey_counts[hotkey] = hotkey_counts.get(hotkey, 0) + 1
        
        has_duplicates = False
        for slot in self.hotkey_slots:
            hotkey = slot.get_hotkey().strip().lower()
            if hotkey and hotkey_counts.get(hotkey, 0) > 1:
                slot.set_duplicate_style(True)
                has_duplicates = True
            else:
                slot.set_duplicate_style(False)
        return has_duplicates
    
    def clear_all_slots(self):
        """Clears all configured hotkey rows after confirmation."""
        reply = QMessageBox.question(self, 'Confirm Clear All',
                                     "Are you sure you want to clear all stratagem slots?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for slot in self.hotkey_slots:
                slot.clear_slot()
    
    def populate_profiles_dropdown(self):
        if not os.path.exists(PROFILES_DIR): os.makedirs(PROFILES_DIR)
        self.profiles_combo.blockSignals(True)
        self.profiles_combo.clear()
        self.profiles_combo.addItem("--- New Profile ---")
        profiles = [f for f in os.listdir(PROFILES_DIR) if f.endswith('.json')]
        for profile in sorted(profiles):
            self.profiles_combo.addItem(profile.replace('.json', ''))
        self.profiles_combo.blockSignals(False)

    def save_current_profile(self):
        profile_name = self.profiles_combo.currentText()
        if profile_name == "--- New Profile ---":
            text, ok = QFileDialog.getSaveFileName(self, "Save New Profile", PROFILES_DIR, "JSON Files (*.json)")
            if ok and text: profile_name = os.path.basename(text).replace('.json', '')
            else: return
        
        config = {
            "settings": {
                "stratagem_menu_key": self.stratagem_menu_key,
                "global_toggle_hotkey": self.global_toggle_hotkey,
                "use_wasd_input": self.use_wasd_input,
                "activation_delay": self.stratagem_activation_delay,
                "pydirectinput_pause": pydirectinput.PAUSE,
                "reminder_opacity": self.reminder_opacity,
            },
            "hotkeys": []
        }
        for slot in self.hotkey_slots:
            config["hotkeys"].append({
                "stratagem": slot.get_stratagem(), 
                "hotkey": slot.get_hotkey()
            })
        
        filepath = os.path.join(PROFILES_DIR, f"{profile_name}.json")
        try:
            with open(filepath, 'w') as f: json.dump(config, f, indent=4)
            QMessageBox.information(self, "Success", f"Profile '{profile_name}' saved.")
            current_selection = self.profiles_combo.currentText()
            self.populate_profiles_dropdown()
            if current_selection == "--- New Profile ---":
                 self.profiles_combo.setCurrentText(profile_name)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save profile: {e}")

    def load_selected_profile(self, index):
        profile_name = self.profiles_combo.itemText(index)
        if profile_name == "--- New Profile ---":
            for slot in self.hotkey_slots: slot.clear_slot()
            self.stratagem_menu_key = 'ctrl'
            self.global_toggle_hotkey = ""
            self.use_wasd_input = False
            self.stratagem_activation_delay = DEFAULT_STRATAGEM_ACTIVATION_DELAY
            pydirectinput.PAUSE = DEFAULT_PYDIRECTINPUT_PAUSE
            self.set_reminder_opacity(DEFAULT_REMINDER_OPACITY)
            self.update_ui_for_state()
            return
        
        filepath = os.path.join(PROFILES_DIR, f"{profile_name}.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f: config = json.load(f)
                
                settings = config.get("settings", {})
                self.stratagem_menu_key = settings.get("stratagem_menu_key", "ctrl")
                self.global_toggle_hotkey = settings.get("global_toggle_hotkey", "")
                self.use_wasd_input = settings.get("use_wasd_input", False)
                self.stratagem_activation_delay = settings.get("activation_delay", DEFAULT_STRATAGEM_ACTIVATION_DELAY)
                pydirectinput.PAUSE = settings.get("pydirectinput_pause", DEFAULT_PYDIRECTINPUT_PAUSE)
                self.set_reminder_opacity(settings.get("reminder_opacity", DEFAULT_REMINDER_OPACITY))


                hotkeys = config.get("hotkeys", [])
                for i, slot in enumerate(self.hotkey_slots):
                    if i < len(hotkeys):
                        item = hotkeys[i]
                        slot.set_stratagem(item.get("stratagem", ""))
                        slot.set_hotkey(item.get("hotkey", ""))
                    else: slot.clear_slot()
                
                self.validate_and_update()
                self.update_ui_for_state()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load profile: {e}")

    def delete_selected_profile(self):
        profile_name = self.profiles_combo.currentText()
        if profile_name == "--- New Profile ---": return
        
        reply = QMessageBox.question(self, 'Confirm Delete', f"Delete profile '{profile_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            filepath = os.path.join(PROFILES_DIR, f"{profile_name}.json")
            try:
                if os.path.exists(filepath): os.remove(filepath)
                self.populate_profiles_dropdown()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete profile: {e}")

    # --- Utilities ---
    def get_key_str_from_pynput(self, key):
        """Converts a pynput key object to a standardized string, handling numpad keys."""
        if hasattr(key, 'vk') and 96 <= key.vk <= 105: # Numpad keys 0-9 have vk 96-105
            return f'num_{key.vk - 96}'
        if isinstance(key, keyboard.KeyCode) and key.char: return key.char.lower()
        if isinstance(key, keyboard.Key):
            if keyboard.Key.f1 <= key <= keyboard.Key.f12: return f"f{key.value.vk - 111}"
            if key == keyboard.Key.x1: return "mouse_xbutton1"
            if key == keyboard.Key.x2: return "mouse_xbutton2"
            return key.name.lower()
        return None

    def closeEvent(self, event):
        if self.status_indicator_window: self.status_indicator_window.close()
        if self.reminder_window: self.reminder_window.close()
        if self.keyboard_listener: self.keyboard_listener.stop()
        if self.mouse_listener: self.mouse_listener.stop()
        event.accept()

def main():
    """Main function to run the application."""
    try:
        import pyautogui, pydirectinput, pynput
    except ImportError as e:
        app = QApplication(sys.argv)
        QMessageBox.critical(None, "Dependency Error", f"Missing library: {e.name}. Please run: pip install PyQt6 pyautogui pynput pydirectinput")
        sys.exit(1)
        
    app = QApplication(sys.argv)
    ex = StratagemMacroApp()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
