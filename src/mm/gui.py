"""
Main GUI window for Auto Mouse Move
"""

import time
import datetime
import sys
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QSpinBox, QCheckBox, QPushButton, QGroupBox,
                            QComboBox, QTextEdit, QTabWidget, QFormLayout, QListWidget,
                            QListWidgetItem, QLineEdit, QDoubleSpinBox, QDialog,
                            QDialogButtonBox, QMessageBox, QSplitter)
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
        
        # Keyboard Macros tab
        macros_tab = self.create_macros_tab()
        tab_widget.addTab(macros_tab, "Keyboard Macros")
        
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
        self.scroll_amount_spin.setRange(1, 200)
        self.scroll_amount_spin.setSuffix(" clicks")
        self.scroll_amount_spin.valueChanged.connect(self.save_settings)
        scroll_layout.addRow("Scroll Amount:", self.scroll_amount_spin)
        
        # Scroll pattern
        self.scroll_pattern_combo = QComboBox()
        self.scroll_pattern_combo.addItems(["random", "up", "down", "left", "right"])
        self.scroll_pattern_combo.currentTextChanged.connect(self.save_settings)
        scroll_layout.addRow("Scroll Pattern:", self.scroll_pattern_combo)
        
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
    
    def create_macros_tab(self) -> QWidget:
        """Create the keyboard macros tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Keyboard macros control group
        control_group = QGroupBox("Keyboard Macros Control")
        control_layout = QFormLayout(control_group)
        
        # Enable keyboard macros
        self.macros_enabled_checkbox = QCheckBox()
        self.macros_enabled_checkbox.stateChanged.connect(self.toggle_macros_enabled)
        control_layout.addRow("Enable Keyboard Macros:", self.macros_enabled_checkbox)
        
        layout.addWidget(control_group)
        
        # Macros management group
        macros_group = QGroupBox("Manage Macros")
        macros_layout = QVBoxLayout(macros_group)
        
        # Buttons row
        buttons_layout = QHBoxLayout()
        
        add_button = QPushButton("Add Macro")
        add_button.clicked.connect(self.add_macro)
        buttons_layout.addWidget(add_button)
        
        edit_button = QPushButton("Edit Macro")
        edit_button.clicked.connect(self.edit_macro)
        buttons_layout.addWidget(edit_button)
        
        delete_button = QPushButton("Delete Macro")
        delete_button.clicked.connect(self.delete_macro)
        buttons_layout.addWidget(delete_button)
        
        test_button = QPushButton("Test Macro")
        test_button.clicked.connect(self.test_macro)
        buttons_layout.addWidget(test_button)
        
        buttons_layout.addStretch()
        macros_layout.addLayout(buttons_layout)
        
        # Macros list
        self.macros_list = QListWidget()
        self.macros_list.itemDoubleClicked.connect(self.edit_macro)
        macros_layout.addWidget(self.macros_list)
        
        layout.addWidget(macros_group)
        
        # Load macros
        self.refresh_macros_list()
        
        # Connect macro manager signals
        self.mouse_controller.keyboard_macro_manager.macros_changed.connect(self.refresh_macros_list)
        
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
        self.scroll_pattern_combo.setCurrentText(config.get("scroll_pattern", "random"))
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
        self.config_manager.set("scroll_pattern", self.scroll_pattern_combo.currentText())
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
        # Safety check to ensure log_text exists
        if not hasattr(self, 'log_text') or self.log_text is None:
            return
            
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
    
    # Keyboard Macro Management Methods
    
    def toggle_macros_enabled(self, state):
        """Toggle keyboard macros enabled/disabled"""
        enabled = state == Qt.CheckState.Checked.value
        self.mouse_controller.keyboard_macro_manager.set_enabled(enabled)
        self.log_activity(f"Keyboard macros {'enabled' if enabled else 'disabled'}")
    
    def refresh_macros_list(self):
        """Refresh the macros list display"""
        self.macros_list.clear()
        
        # Load current macro enabled state
        if hasattr(self, 'macros_enabled_checkbox'):
            self.macros_enabled_checkbox.setChecked(
                self.mouse_controller.keyboard_macro_manager.is_enabled()
            )
        
        # Get the current palette to determine theme colors
        palette = self.macros_list.palette()
        text_color = palette.color(palette.ColorRole.Text)
        disabled_color = palette.color(palette.ColorRole.PlaceholderText)
        
        # If disabled color is too similar to text color, create a more distinct disabled color
        if disabled_color == text_color or disabled_color.lightnessF() == text_color.lightnessF():
            # Create a grayed-out version of the text color
            disabled_color = text_color.darker(150)  # Make it 50% darker
            if text_color.lightnessF() < 0.5:  # If we're in dark mode
                disabled_color = text_color.lighter(150)  # Make it 50% lighter instead
        
        # Add macros to list
        macros = self.mouse_controller.keyboard_macro_manager.get_all_macros()
        for macro in macros:
            item = QListWidgetItem()
            
            # Create display text
            keys_text = ", ".join(macro.keys) if macro.keys else "No keys"
            status = "✓" if macro.enabled else "✗"
            display_text = f"{status} {macro.name} - {keys_text}"
            if macro.description:
                display_text += f" ({macro.description})"
            
            item.setText(display_text)
            item.setData(Qt.ItemDataRole.UserRole, macro.name)  # Store macro name
            
            # Dynamic color coding based on current theme
            if macro.enabled:
                # Use the default text color for enabled macros
                item.setForeground(text_color)
            else:
                # Use a muted color for disabled macros
                item.setForeground(disabled_color)
            
            self.macros_list.addItem(item)
    
    def add_macro(self):
        """Add a new keyboard macro"""
        dialog = MacroEditDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            macro = dialog.get_macro()
            if macro:
                self.mouse_controller.keyboard_macro_manager.add_macro(macro)
                self.log_activity(f"Added macro: {macro.name}")
    
    def edit_macro(self):
        """Edit the selected macro"""
        current_item = self.macros_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a macro to edit.")
            return
        
        macro_name = current_item.data(Qt.ItemDataRole.UserRole)
        macro = self.mouse_controller.keyboard_macro_manager.get_macro(macro_name)
        
        if macro:
            dialog = MacroEditDialog(self, macro)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_macro = dialog.get_macro()
                if updated_macro:
                    self.mouse_controller.keyboard_macro_manager.update_macro(macro_name, updated_macro)
                    self.log_activity(f"Updated macro: {updated_macro.name}")
    
    def delete_macro(self):
        """Delete the selected macro"""
        current_item = self.macros_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a macro to delete.")
            return
        
        macro_name = current_item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            f"Are you sure you want to delete the macro '{macro_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.mouse_controller.keyboard_macro_manager.remove_macro(macro_name):
                self.log_activity(f"Deleted macro: {macro_name}")
            else:
                QMessageBox.warning(self, "Error", f"Failed to delete macro '{macro_name}'.")
    
    def test_macro(self):
        """Test the selected macro"""
        current_item = self.macros_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a macro to test.")
            return
        
        macro_name = current_item.data(Qt.ItemDataRole.UserRole)
        macro = self.mouse_controller.keyboard_macro_manager.get_macro(macro_name)
        
        if macro:
            # Show warning dialog
            reply = QMessageBox.question(
                self, "Test Macro", 
                f"This will execute the macro '{macro_name}' immediately.\n\n"
                f"Keys: {', '.join(macro.keys)}\n"
                f"Description: {macro.description}\n\n"
                "Are you sure you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                success = self.mouse_controller.keyboard_macro_manager.test_macro(macro)
                if success:
                    self.log_activity(f"Tested macro: {macro_name}")
                else:
                    QMessageBox.warning(self, "Test Failed", f"Failed to test macro '{macro_name}'.")


class MacroEditDialog(QDialog):
    """Dialog for editing keyboard macros"""
    
    def __init__(self, parent=None, macro=None):
        super().__init__(parent)
        self.macro = macro
        self.init_ui()
        
        if macro:
            self.load_macro(macro)
    
    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("Edit Keyboard Macro" if self.macro else "Add Keyboard Macro")
        self.setFixedSize(550, 450)  # Increased size for better layout
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)  # Add more spacing between sections
        
        # Main form group
        form_group = QGroupBox("Macro Settings")
        form_layout = QFormLayout(form_group)
        form_layout.setVerticalSpacing(10)  # Add spacing between form rows
        
        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter macro name")
        self.name_edit.setMinimumHeight(30)  # Set minimum height for better visibility
        form_layout.addRow("Name:", self.name_edit)
        
        # Description
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Enter description (optional)")
        self.description_edit.setMinimumHeight(30)
        form_layout.addRow("Description:", self.description_edit)
        
        # Keys
        self.keys_edit = QLineEdit()
        self.keys_edit.setPlaceholderText("e.g., f5 or ctrl+s or shift+cmd+ctrl+right")
        self.keys_edit.setMinimumHeight(30)
        form_layout.addRow("Keys:", self.keys_edit)
        
        # Delay
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0.0, 5.0)
        self.delay_spin.setSingleStep(0.1)
        self.delay_spin.setValue(0.1)
        self.delay_spin.setSuffix(" seconds")
        self.delay_spin.setMinimumHeight(30)
        form_layout.addRow("Delay:", self.delay_spin)
        
        # Enabled
        self.enabled_checkbox = QCheckBox()
        self.enabled_checkbox.setChecked(True)
        form_layout.addRow("Enabled:", self.enabled_checkbox)
        
        layout.addWidget(form_group)
        
        # Help section
        help_group = QGroupBox("Key Examples & Help")
        help_layout = QVBoxLayout(help_group)
        
        help_text = QLabel(
            "Key Examples:\n"
            "• Single keys: f5, space, enter, escape\n"
            "• Simple combinations: ctrl+s, alt+tab, shift+f10\n"
            "• Complex combinations: shift+cmd+ctrl+right\n"
            "• Multiple keys: up,down,left,right (random selection)\n"
            "• macOS: Use 'cmd' for Command key\n"
            "• Windows: Use 'win' for Windows key\n"
            "• Arrow keys: up, down, left, right\n"
            "• Function keys: f1, f2, f3, etc."
        )
        help_text.setStyleSheet("color: gray; font-size: 11px; padding: 5px;")
        help_text.setWordWrap(True)
        help_text.setAlignment(Qt.AlignmentFlag.AlignTop)
        help_layout.addWidget(help_text)
        
        layout.addWidget(help_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_macro(self, macro):
        """Load macro data into the form"""
        self.name_edit.setText(macro.name)
        self.description_edit.setText(macro.description)
        self.keys_edit.setText(", ".join(macro.keys))
        self.delay_spin.setValue(macro.delay)
        self.enabled_checkbox.setChecked(macro.enabled)
    
    def get_macro(self):
        """Get macro from form data"""
        from mm.keyboard_macro import KeyboardMacro
        
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Input", "Please enter a macro name.")
            return None
        
        keys_text = self.keys_edit.text().strip()
        if not keys_text:
            QMessageBox.warning(self, "Invalid Input", "Please enter at least one key.")
            return None
        
        # Parse keys
        keys = [key.strip() for key in keys_text.replace(",", " ").split() if key.strip()]
        if not keys:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid keys.")
            return None
        
        # Validate keys
        macro_manager = self.parent().mouse_controller.keyboard_macro_manager
        for key in keys:
            if not macro_manager.validate_key_combination(key):
                QMessageBox.warning(
                    self, "Invalid Key", 
                    f"The key combination '{key}' is not valid.\n\n"
                    "Please use valid key names like:\n"
                    "• Single keys: f5, space, enter, escape\n"
                    "• Combinations: ctrl+s, alt+tab\n"
                    "• Arrow keys: up, down, left, right"
                )
                return None
        
        description = self.description_edit.text().strip()
        delay = self.delay_spin.value()
        enabled = self.enabled_checkbox.isChecked()
        
        macro = KeyboardMacro(name, keys, delay, description)
        macro.enabled = enabled
        
        return macro