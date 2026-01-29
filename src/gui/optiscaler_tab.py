#!/usr/bin/env python3
"""OptiScaler GUI Tab

Version: 0.3.5d (package 3.8a, stage 5/6)
"""
import sys
from pathlib import Path
from typing import Optional

try:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
        QPushButton, QLabel, QProgressBar, QComboBox,
        QSlider, QCheckBox, QLineEdit, QFileDialog,
        QMessageBox, QTextEdit
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
except ImportError:
    print("[OptiScalerTab] Warning: PyQt6 not available, using stubs")
    # Stubs for when PyQt6 not available
    class QWidget: pass
    class QVBoxLayout: pass
    class QHBoxLayout: pass
    class QGroupBox: pass
    class QPushButton: pass
    class QLabel: pass
    class QProgressBar: pass
    class QComboBox: pass
    class QSlider: pass
    class QCheckBox: pass
    class QLineEdit: pass
    class QFileDialog: pass
    class QMessageBox: pass
    class QTextEdit: pass
    class QThread: pass
    class pyqtSignal: pass
    class Qt: 
        Horizontal = 1
        AlignCenter = 0

# Import OptiScaler
try:
    from optiscaler import (
        OptiScalerManager,
        OptiScalerConfig,
        OptiScalerBackend,
        OptiScalerQuality,
        GameInfo
    )
    OPTISCALER_AVAILABLE = True
except ImportError:
    OPTISCALER_AVAILABLE = False
    print("[OptiScalerTab] Warning: optiscaler module not found")


class InstallThread(QThread):
    """Background thread for OptiScaler installation"""
    progress = pyqtSignal(str, int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, manager: 'OptiScalerManager'):
        super().__init__()
        self.manager = manager
    
    def run(self):
        """Run installation"""
        try:
            def progress_callback(status, percent):
                self.progress.emit(status, percent)
            
            success = self.manager.install(progress_callback=progress_callback)
            
            if success:
                self.finished.emit(True, "OptiScaler installed successfully!")
            else:
                self.finished.emit(False, "Installation failed")
        
        except Exception as e:
            self.finished.emit(False, f"Installation error: {e}")


class OptiScalerTab(QWidget):
    """OptiScaler Control Panel GUI
    
    Provides interface for:
    - Installing/uninstalling OptiScaler
    - Configuring upscaler settings
    - Injecting into games
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        if not OPTISCALER_AVAILABLE:
            self._create_error_ui()
            return
        
        # Initialize manager
        self.manager = OptiScalerManager()
        self.current_game: Optional[GameInfo] = None
        self.install_thread: Optional[InstallThread] = None
        
        # Create UI
        self._create_ui()
        
        # Check installation status
        self._check_installation()
    
    def _create_error_ui(self):
        """Create error UI when OptiScaler not available"""
        layout = QVBoxLayout()
        
        error_label = QLabel(
            "❌ OptiScaler module not available\n\n"
            "Please ensure the optiscaler package is installed."
        )
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setStyleSheet("color: red; font-size: 14px;")
        
        layout.addWidget(error_label)
        self.setLayout(layout)
    
    def _create_ui(self):
        """Create main UI"""
        main_layout = QVBoxLayout()
        
        # Installation section
        install_group = self._create_installation_section()
        main_layout.addWidget(install_group)
        
        # Configuration section
        config_group = self._create_configuration_section()
        main_layout.addWidget(config_group)
        
        # Game injection section
        game_group = self._create_game_injection_section()
        main_layout.addWidget(game_group)
        
        # Status log
        log_group = self._create_log_section()
        main_layout.addWidget(log_group)
        
        main_layout.addStretch()
        self.setLayout(main_layout)
    
    def _create_installation_section(self) -> QGroupBox:
        """Create installation section"""
        group = QGroupBox("OptiScaler Installation")
        layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel("Status: Checking...")
        layout.addWidget(self.status_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.install_btn = QPushButton("Install OptiScaler")
        self.install_btn.clicked.connect(self._install_optiscaler)
        btn_layout.addWidget(self.install_btn)
        
        self.uninstall_btn = QPushButton("Uninstall")
        self.uninstall_btn.clicked.connect(self._uninstall_optiscaler)
        self.uninstall_btn.setEnabled(False)
        btn_layout.addWidget(self.uninstall_btn)
        
        layout.addLayout(btn_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)
        
        group.setLayout(layout)
        return group
    
    def _create_configuration_section(self) -> QGroupBox:
        """Create configuration section"""
        group = QGroupBox("Configuration")
        layout = QVBoxLayout()
        
        # Backend selector
        backend_layout = QHBoxLayout()
        backend_layout.addWidget(QLabel("Backend:"))
        self.backend_combo = QComboBox()
        self.backend_combo.addItems(["Auto", "FSR 3.1", "XeSS 2.1", "DLSS"])
        backend_layout.addWidget(self.backend_combo)
        layout.addLayout(backend_layout)
        
        # Quality selector
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems([
            "Performance (2.0x)",
            "Balanced (1.7x)",
            "Quality (1.5x)",
            "Ultra Quality (1.3x)"
        ])
        self.quality_combo.setCurrentIndex(2)  # Quality default
        quality_layout.addWidget(self.quality_combo)
        layout.addLayout(quality_layout)
        
        # Sharpness slider
        sharpness_layout = QVBoxLayout()
        sharpness_layout.addWidget(QLabel("Sharpness:"))
        self.sharpness_slider = QSlider(Qt.Horizontal)
        self.sharpness_slider.setMinimum(0)
        self.sharpness_slider.setMaximum(100)
        self.sharpness_slider.setValue(50)
        self.sharpness_slider.valueChanged.connect(self._update_sharpness_label)
        sharpness_layout.addWidget(self.sharpness_slider)
        
        self.sharpness_value_label = QLabel("0.5")
        sharpness_layout.addWidget(self.sharpness_value_label)
        layout.addLayout(sharpness_layout)
        
        # Checkboxes
        self.frame_gen_check = QCheckBox("Enable Frame Generation")
        layout.addWidget(self.frame_gen_check)
        
        self.hud_fix_check = QCheckBox("Enable HUD Fix")
        self.hud_fix_check.setChecked(True)
        layout.addWidget(self.hud_fix_check)
        
        # Apply button
        self.apply_config_btn = QPushButton("Apply Configuration")
        self.apply_config_btn.clicked.connect(self._apply_configuration)
        self.apply_config_btn.setEnabled(False)
        layout.addWidget(self.apply_config_btn)
        
        group.setLayout(layout)
        return group
    
    def _create_game_injection_section(self) -> QGroupBox:
        """Create game injection section"""
        group = QGroupBox("Game Injection")
        layout = QVBoxLayout()
        
        # Game directory
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Game Directory:"))
        self.game_dir_edit = QLineEdit()
        dir_layout.addWidget(self.game_dir_edit)
        
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self._browse_game_dir)
        dir_layout.addWidget(self.browse_btn)
        layout.addLayout(dir_layout)
        
        # Detect game button
        self.detect_game_btn = QPushButton("Detect Game")
        self.detect_game_btn.clicked.connect(self._detect_game)
        layout.addWidget(self.detect_game_btn)
        
        # Game info
        self.game_info_label = QLabel("No game detected")
        self.game_info_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(self.game_info_label)
        
        # Inject/Remove buttons
        inject_layout = QHBoxLayout()
        self.inject_btn = QPushButton("Inject OptiScaler")
        self.inject_btn.clicked.connect(self._inject_optiscaler)
        self.inject_btn.setEnabled(False)
        inject_layout.addWidget(self.inject_btn)
        
        self.remove_btn = QPushButton("Remove OptiScaler")
        self.remove_btn.clicked.connect(self._remove_optiscaler)
        self.remove_btn.setEnabled(False)
        inject_layout.addWidget(self.remove_btn)
        layout.addLayout(inject_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_log_section(self) -> QGroupBox:
        """Create log section"""
        group = QGroupBox("Status Log")
        layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)
        
        group.setLayout(layout)
        return group
    
    def _check_installation(self):
        """Check OptiScaler installation status"""
        self.manager.initialize()
        
        if self.manager.is_installed():
            info = self.manager.get_info()
            self.status_label.setText(f"✅ Status: Installed (v{info.version})")
            self.status_label.setStyleSheet("color: green;")
            self.install_btn.setEnabled(False)
            self.uninstall_btn.setEnabled(True)
            self.apply_config_btn.setEnabled(True)
            self._log(f"OptiScaler {info.version} detected")
        else:
            self.status_label.setText("❌ Status: Not Installed")
            self.status_label.setStyleSheet("color: red;")
            self.install_btn.setEnabled(True)
            self.uninstall_btn.setEnabled(False)
            self.apply_config_btn.setEnabled(False)
            self._log("OptiScaler not installed")
    
    def _install_optiscaler(self):
        """Install OptiScaler"""
        self._log("Starting OptiScaler installation...")
        
        # Disable buttons
        self.install_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Start installation thread
        self.install_thread = InstallThread(self.manager)
        self.install_thread.progress.connect(self._on_install_progress)
        self.install_thread.finished.connect(self._on_install_finished)
        self.install_thread.start()
    
    def _on_install_progress(self, status: str, percent: int):
        """Handle installation progress"""
        self.progress_label.setText(status)
        self.progress_bar.setValue(percent)
        self._log(f"{status}: {percent}%")
    
    def _on_install_finished(self, success: bool, message: str):
        """Handle installation completion"""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        if success:
            QMessageBox.information(self, "Success", message)
            self._log("✅ " + message)
            self._check_installation()
        else:
            QMessageBox.critical(self, "Error", message)
            self._log("❌ " + message)
            self.install_btn.setEnabled(True)
    
    def _uninstall_optiscaler(self):
        """Uninstall OptiScaler"""
        reply = QMessageBox.question(
            self,
            "Confirm Uninstall",
            "Are you sure you want to uninstall OptiScaler?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._log("Uninstalling OptiScaler...")
            
            if self.manager.uninstall():
                QMessageBox.information(self, "Success", "OptiScaler uninstalled")
                self._log("✅ OptiScaler uninstalled")
                self._check_installation()
            else:
                QMessageBox.critical(self, "Error", "Uninstall failed")
                self._log("❌ Uninstall failed")
    
    def _apply_configuration(self):
        """Apply OptiScaler configuration"""
        # Map selections
        backend_map = {
            "Auto": OptiScalerBackend.AUTO,
            "FSR 3.1": OptiScalerBackend.FSR3,
            "XeSS 2.1": OptiScalerBackend.XESS,
            "DLSS": OptiScalerBackend.DLSS
        }
        
        quality_map = [
            OptiScalerQuality.PERFORMANCE,
            OptiScalerQuality.BALANCED,
            OptiScalerQuality.QUALITY,
            OptiScalerQuality.ULTRA_QUALITY
        ]
        
        # Create config
        config = OptiScalerConfig(
            backend=backend_map[self.backend_combo.currentText()],
            quality=quality_map[self.quality_combo.currentIndex()],
            sharpness=self.sharpness_slider.value() / 100.0,
            enable_frame_gen=self.frame_gen_check.isChecked(),
            enable_hud_fix=self.hud_fix_check.isChecked()
        )
        
        # Apply
        if self.manager.configure(config):
            QMessageBox.information(self, "Success", "Configuration applied")
            self._log("✅ Configuration applied")
        else:
            QMessageBox.critical(self, "Error", "Failed to apply configuration")
            self._log("❌ Configuration failed")
    
    def _update_sharpness_label(self, value: int):
        """Update sharpness value label"""
        self.sharpness_value_label.setText(f"{value / 100.0:.2f}")
    
    def _browse_game_dir(self):
        """Browse for game directory"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Game Directory",
            ""
        )
        
        if dir_path:
            self.game_dir_edit.setText(dir_path)
            self._log(f"Selected: {dir_path}")
    
    def _detect_game(self):
        """Detect game in selected directory"""
        game_dir = self.game_dir_edit.text()
        
        if not game_dir:
            QMessageBox.warning(self, "Warning", "Please select a game directory")
            return
        
        self._log(f"Detecting game in: {game_dir}")
        
        game = self.manager.detect_game(Path(game_dir))
        
        if game:
            self.current_game = game
            
            # Show game info
            upscalers = []
            if game.has_dlss: upscalers.append("DLSS")
            if game.has_fsr: upscalers.append("FSR2")
            if game.has_xess: upscalers.append("XeSS")
            
            info_text = f"✅ Game: {game.name}\nSupports: {', '.join(upscalers) if upscalers else 'None detected'}"
            self.game_info_label.setText(info_text)
            self.game_info_label.setStyleSheet("color: green;")
            
            self.inject_btn.setEnabled(True)
            self.remove_btn.setEnabled(True)
            
            self._log(f"✅ Detected: {game.name}")
        else:
            self.game_info_label.setText("❌ No game detected in this directory")
            self.game_info_label.setStyleSheet("color: red;")
            self.inject_btn.setEnabled(False)
            self.remove_btn.setEnabled(False)
            self._log("❌ Game detection failed")
    
    def _inject_optiscaler(self):
        """Inject OptiScaler into game"""
        if not self.current_game:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Injection",
            f"Inject OptiScaler into {self.current_game.name}?\n\n"
            f"This will:\n"
            f"- Backup original DLLs\n"
            f"- Copy OptiScaler files\n"
            f"- Apply configuration",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._log(f"Injecting into {self.current_game.name}...")
            
            try:
                if self.manager.inject_into_game(self.current_game):
                    QMessageBox.information(
                        self,
                        "Success",
                        f"OptiScaler injected into {self.current_game.name}!\n\n"
                        f"Game now uses FSR 3.1!"
                    )
                    self._log(f"✅ Injection successful!")
                else:
                    QMessageBox.critical(self, "Error", "Injection failed")
                    self._log("❌ Injection failed")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Injection error: {e}")
                self._log(f"❌ Error: {e}")
    
    def _remove_optiscaler(self):
        """Remove OptiScaler from game"""
        if not self.current_game:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Remove OptiScaler from {self.current_game.name}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._log(f"Removing from {self.current_game.name}...")
            
            if self.manager.remove_from_game(self.current_game):
                QMessageBox.information(self, "Success", "OptiScaler removed")
                self._log("✅ Removal successful")
            else:
                QMessageBox.critical(self, "Error", "Removal failed")
                self._log("❌ Removal failed")
    
    def _log(self, message: str):
        """Add message to log"""
        self.log_text.append(message)
