"""
Main GUI window for Auto Mouse Move
"""

import time
import datetime
import sys
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QSpinBox, QCheckBox, QPushButton, QGroupBox,
                            QComboBox, QTextEdit, QTabWidget, QFormLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# Add the parent directory to sys.path for absolute imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from mm.config import ConfigManager
from mm.mouse_controller import MouseController


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, config_manager: ConfigManager, mouse_controller: MouseController):
        super().__init__()
        self.config_manager = config_manager
        self.mouse_controller = mouse_controller
        
        # Connect signals
        self.mouse_controller.status_changed.connect(self.update_status)
        self.mouse_controller.activity_performed.connect(self.log_activity)
        
        self.init_ui()
        self.load_settings()
        
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_display)
        self.status_timer.start(1000)  # Update every second
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Auto Mouse Move")
        self.setFixedSize(500, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Create tabs
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Main tab
        main_tab = self.create_main_tab()
        tab_widget.addTab(main_tab, "Main")
        
        # Settings tab
        settings_tab = self.create_settings_tab()
        tab_widget.addTab(settings_tab, "Settings")
        
        # Log tab
        log_tab = self.create_log_tab()
        tab_widget.addTab(log_tab, "Activity Log")
        
        # Status bar
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
    
    def create_main_tab(self) -> QWidget:
        """Create the main control tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Control group
        control_group = QGroupBox("Control")
        control_layout = QVBoxLayout(control_group)
        
        # Enable/Disable
        self.enable_checkbox = QCheckBox("Enable Auto Mouse Move")
        self.enable_checkbox.stateChanged.connect(self.toggle_enabled)
        control_layout.addWidget(self.enable_checkbox)
        
        # Force activity button
        self.force_button = QPushButton("Force Activity Now")
        self.force_button.clicked.connect(self.force_activity)
        control_layout.addWidget(self.force_button)
        
        layout.addWidget(control_group)
        
        # Status group
        status_group = QGroupBox("Status")
        status_layout = QFormLayout(status_group)
        
        self.idle_time_label = QLabel("0 seconds")
        status_layout.addRow("Current Idle Time:", self.idle_time_label)
        
        self.next_action_label = QLabel("N/A")
        status_layout.addRow("Next Action In:", self.next_action_label)
        
        self.controller_status_label = QLabel("Stopped")
        status_layout.addRow("Controller Status:", self.controller_status_label)
        
        layout.addWidget(status_group)
        
        # Quick settings group
        quick_group = QGroupBox("Quick Settings")
        quick_layout = QFormLayout(quick_group)
        
        # Idle threshold
        self.idle_threshold_spin = QSpinBox()
        self.idle_threshold_spin.setRange(3, 18000)  # 3 seconds to 5 hours
        self.idle_threshold_spin.setSuffix(" seconds")
        self.idle_threshold_spin.valueChanged.connect(self.save_settings)
        quick_layout.addRow("Idle Threshold:", self.idle_threshold_spin)
        
        # Move interval
        self.move_interval_spin = QSpinBox()
        self.move_interval_spin.setRange(5, 300)  # 5 seconds to 5 minutes
        self.move_interval_spin.setSuffix(" seconds")
        self.move_interval_spin.valueChanged.connect(self.save_settings)
        quick_layout.addRow("Move Interval:", self.move_interval_spin)
        
        layout.addWidget(quick_group)
        
        layout.addStretch()
        return widget
    
    def create_settings_tab(self) -> QWidget:
        """Create the settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Mouse settings group
        mouse_group = QGroupBox("Mouse Settings")
        mouse_layout = QFormLayout(mouse_group)
        
        # Mouse movement enabled
        self.mouse_enabled_checkbox = QCheckBox()
        self.mouse_enabled_checkbox.stateChanged.connect(self.save_settings)
        mouse_layout.addRow("Enable Mouse Movement:", self.mouse_enabled_checkbox)
        
        # Movement distance
        self.move_distance_spin = QSpinBox()
        self.move_distance_spin.setRange(1, 50)
        self.move_distance_spin.setSuffix(" pixels")
        self.move_distance_spin.valueChanged.connect(self.save_settings)
        mouse_layout.addRow("Movement Distance:", self.move_distance_spin)
        
        # Movement pattern
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems(["random", "circular", "linear"])
        self.pattern_combo.currentTextChanged.connect(self.save_settings)
        mouse_layout.addRow("Movement Pattern:", self.pattern_combo)
        
        layout.addWidget(mouse_group)
        
        # Scroll settings group
        scroll_group = QGroupBox("Scroll Settings")
        scroll_layout = QFormLayout(scroll_group)
        
        # Scroll enabled
        self.scroll_enabled_checkbox = QCheckBox()
        self.scroll_enabled_checkbox.stateChanged.connect(self.save_settings)
        scroll_layout.addRow("Enable Scrolling:", self.scroll_enabled_checkbox)
        
        # Scroll amount
        self.scroll_amount_spin = QSpinBox()
        self.scroll_amount_spin.setRange(1, 10)
        self.scroll_amount_spin.setSuffix(" clicks")
        self.scroll_amount_spin.valueChanged.connect(self.save_settings)
        scroll_layout.addRow("Scroll Amount:", self.scroll_amount_spin)
        
        layout.addWidget(scroll_group)
        
        # Application settings group
        app_group = QGroupBox("Application Settings")
        app_layout = QFormLayout(app_group)
        
        # Check interval
        self.check_interval_spin = QSpinBox()
        self.check_interval_spin.setRange(1, 60)
        self.check_interval_spin.setSuffix(" seconds")
        self.check_interval_spin.valueChanged.connect(self.save_settings)
        app_layout.addRow("Check Interval:", self.check_interval_spin)
        
        # Minimize to tray
        self.minimize_tray_checkbox = QCheckBox()
        self.minimize_tray_checkbox.stateChanged.connect(self.save_settings)
        app_layout.addRow("Minimize to Tray:", self.minimize_tray_checkbox)
        
        layout.addWidget(app_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.manual_save_settings)
        button_layout.addWidget(save_button)
        
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self.reset_settings)
        button_layout.addWidget(reset_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        layout.addStretch()
        return widget
    
    def create_log_tab(self) -> QWidget:
        """Create the activity log tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier", 10))
        layout.addWidget(self.log_text)
        
        # Clear button
        clear_button = QPushButton("Clear Log")
        clear_button.clicked.connect(self.clear_log)
        layout.addWidget(clear_button)
        
        return widget
    
    def load_settings(self):
        """Load settings from config manager"""
        config = self.config_manager.get_all()
        
        # Main tab
        self.enable_checkbox.setChecked(config.get("enabled", False))
        self.idle_threshold_spin.setValue(config.get("idle_threshold", 300))
        self.move_interval_spin.setValue(config.get("move_interval", 30))
        
        # Settings tab
        self.mouse_enabled_checkbox.setChecked(config.get("mouse_move_enabled", True))
        self.move_distance_spin.setValue(config.get("move_distance", 5))
        self.pattern_combo.setCurrentText(config.get("movement_pattern", "random"))
        self.scroll_enabled_checkbox.setChecked(config.get("scroll_enabled", True))
        self.scroll_amount_spin.setValue(config.get("scroll_amount", 3))
        self.check_interval_spin.setValue(config.get("check_interval", 5))
        self.minimize_tray_checkbox.setChecked(config.get("minimize_to_tray", True))
    
    def save_settings(self):
        """Save current settings to config manager (automatic save)"""
        # Main tab
        self.config_manager.set("enabled", self.enable_checkbox.isChecked())
        self.config_manager.set("idle_threshold", self.idle_threshold_spin.value())
        self.config_manager.set("move_interval", self.move_interval_spin.value())
        
        # Settings tab
        self.config_manager.set("mouse_move_enabled", self.mouse_enabled_checkbox.isChecked())
        self.config_manager.set("move_distance", self.move_distance_spin.value())
        self.config_manager.set("movement_pattern", self.pattern_combo.currentText())
        self.config_manager.set("scroll_enabled", self.scroll_enabled_checkbox.isChecked())
        self.config_manager.set("scroll_amount", self.scroll_amount_spin.value())
        self.config_manager.set("check_interval", self.check_interval_spin.value())
        self.config_manager.set("minimize_to_tray", self.minimize_tray_checkbox.isChecked())
    
    def manual_save_settings(self):
        """Manually save settings with user feedback"""
        self.save_settings()
        self.log_activity("Settings saved manually")
        
        # Show temporary feedback on the button text only
        save_button = self.sender()
        original_text = save_button.text()
        
        save_button.setText("Saved!")
        
        # Reset button text after 2 seconds
        QTimer.singleShot(2000, lambda: save_button.setText(original_text))
    
    def reset_settings(self):
        """Reset settings to defaults"""
        self.config_manager.reset_to_defaults()
        self.load_settings()
    
    def toggle_enabled(self, state):
        """Toggle the mouse controller"""
        enabled = state == Qt.CheckState.Checked.value
        self.config_manager.set("enabled", enabled)
        
        if enabled:
            self.mouse_controller.start()
        else:
            self.mouse_controller.stop()
    
    def force_activity(self):
        """Force immediate activity"""
        self.mouse_controller.force_activity()
        self.log_activity("Manual activity triggered")
    
    def update_status(self, status: str):
        """Update status display"""
        self.status_label.setText(status)
    
    def update_display(self):
        """Update the display with current information"""
        # Update controller status
        if self.mouse_controller.is_enabled():
            self.controller_status_label.setText("Running")
            self.controller_status_label.setStyleSheet("color: green;")
        else:
            self.controller_status_label.setText("Stopped")
            self.controller_status_label.setStyleSheet("color: red;")
        
        # Update idle time and next action
        try:
            idle_time = self.mouse_controller.idle_detector.get_idle_time()
            self.idle_time_label.setText(f"{idle_time:.1f} seconds")
            
            # Calculate next action time
            if self.mouse_controller.is_enabled():
                idle_threshold = self.config_manager.get("idle_threshold", 300)
                move_interval = self.config_manager.get("move_interval", 30)
                
                if idle_time >= idle_threshold:
                    # System is idle, calculate time until next move based on last move time
                    current_time = time.time()
                    time_since_last_move = current_time - self.mouse_controller._last_move_time
                    next_move_in = max(0, move_interval - time_since_last_move)
                    
                    if next_move_in <= 0:
                        self.next_action_label.setText("Now")
                    else:
                        self.next_action_label.setText(f"{next_move_in:.1f} seconds")
                else:
                    # System not idle yet, show time until idle threshold
                    time_until_idle = idle_threshold - idle_time
                    self.next_action_label.setText(f"{time_until_idle:.1f} seconds (until idle)")
            else:
                self.next_action_label.setText("Disabled")
                
        except Exception as e:
            self.idle_time_label.setText("Unknown")
            self.next_action_label.setText("Error")
    
    def log_activity(self, message: str):
        """Log activity to the log tab"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_text.append(log_entry)
        
        # Keep log size manageable
        if self.log_text.document().blockCount() > 1000:
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.KeepAnchor, 100)
            cursor.removeSelectedText()
    
    def clear_log(self):
        """Clear the activity log"""
        self.log_text.clear()
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.config_manager.get("minimize_to_tray", True):
            event.ignore()
            self.hide()
        else:
            event.accept()