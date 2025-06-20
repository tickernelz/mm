"""
System tray management for Auto Mouse Move
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction

# Add the parent directory to sys.path for absolute imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from mm.logger import logger


class SystemTrayManager(QObject):
    """Manages system tray icon and menu"""
    
    def __init__(self, main_window, mouse_controller):
        super().__init__()
        self.main_window = main_window
        self.mouse_controller = mouse_controller
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(self.create_icon())
        self.tray_icon.setToolTip("Auto Mouse Move")
        
        # Create context menu
        self.create_menu()
        
        # Connect signals
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.mouse_controller.status_changed.connect(self.update_tooltip)
    
    def create_icon(self) -> QIcon:
        """Create a simple icon for the system tray"""
        # Create a 16x16 pixmap
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw a simple mouse cursor icon
        painter.setPen(QColor(0, 0, 0))
        painter.setBrush(QColor(100, 150, 255))
        
        # Draw mouse shape
        painter.drawEllipse(2, 2, 12, 10)
        painter.drawRect(7, 2, 2, 4)  # Mouse button separator
        
        painter.end()
        
        return QIcon(pixmap)
    
    def create_menu(self):
        """Create the context menu"""
        # Create menu without parent first
        self.menu = QMenu()
        
        # Create actions
        self.show_action = QAction("Show Window")
        self.toggle_action = QAction("Enable")
        self.force_action = QAction("Force Activity")
        self.exit_action = QAction("Exit")
        
        # Connect signals
        self.show_action.triggered.connect(self.show_window)
        self.toggle_action.triggered.connect(self.toggle_controller)
        self.force_action.triggered.connect(self.force_activity)
        self.exit_action.triggered.connect(self.exit_application)
        
        # Add actions to menu
        self.menu.addAction(self.show_action)
        self.menu.addSeparator()
        self.menu.addAction(self.toggle_action)
        self.menu.addAction(self.force_action)
        self.menu.addSeparator()
        self.menu.addAction(self.exit_action)
        
        # Set the context menu
        self.tray_icon.setContextMenu(self.menu)
        logger.debug("System tray menu created successfully")
    
    def show(self):
        """Show the system tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon.show()
            self.update_menu_state()
            logger.info("System tray icon shown")
        else:
            logger.warning("System tray is not available")
    
    def hide(self):
        """Hide the system tray icon"""
        self.tray_icon.hide()
    
    def show_notification(self, title: str, message: str):
        """Show a system notification"""
        if self.tray_icon.isVisible():
            self.tray_icon.showMessage(
                title, 
                message, 
                QSystemTrayIcon.MessageIcon.Information, 
                3000  # 3 seconds
            )
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()
        elif reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            self.toggle_controller()
    
    def show_window(self):
        """Show or hide the main window"""
        if self.main_window.isVisible():
            # Hide the window
            self.main_window.hide()
        else:
            # Show the window
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
        self.update_menu_state()
    
    def toggle_controller(self):
        """Toggle the mouse controller on/off"""
        if self.mouse_controller.is_enabled():
            self.mouse_controller.stop()
            self.main_window.enable_checkbox.setChecked(False)
        else:
            self.mouse_controller.start()
            self.main_window.enable_checkbox.setChecked(True)
        
        self.update_menu_state()
    
    def force_activity(self):
        """Force immediate activity"""
        self.mouse_controller.force_activity()
        self.show_notification("Auto Mouse Move", "Activity performed")
    
    def exit_application(self):
        """Exit the application completely"""
        self.mouse_controller.stop()
        self.tray_icon.hide()
        QApplication.quit()
    
    def update_menu_state(self):
        """Update menu items based on current state"""
        # Update show/hide action
        if self.main_window.isVisible():
            self.show_action.setText("Hide Window")
        else:
            self.show_action.setText("Show Window")
        
        # Update enable/disable action
        if self.mouse_controller.is_enabled():
            self.toggle_action.setText("Disable")
        else:
            self.toggle_action.setText("Enable")
    
    def update_tooltip(self, status: str):
        """Update the tray icon tooltip"""
        base_tooltip = "Auto Mouse Move"
        if self.mouse_controller.is_enabled():
            tooltip = f"{base_tooltip} - Running\n{status}"
        else:
            tooltip = f"{base_tooltip} - Stopped"
        
        self.tray_icon.setToolTip(tooltip)