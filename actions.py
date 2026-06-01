import os
import shutil
import subprocess
import pyautogui
import psutil
import glob
from pathlib import Path

class JarvisActions:
    """
    The 'Hands' of JARVIS.
    This class provides high-level methods for interacting with the Windows OS.
    """

    def __init__(self):
        # Safety setting for PyAutoGUI
        pyautogui.FAILSAFE = True

    # --- File Management ---
    def find_file(self, filename, search_path="C:\\"):
        """Search for a file by name starting from search_path."""
        print(f"[Action] Searching for {filename} in {search_path}...")
        # Using glob for recursive search
        pattern = os.path.join(search_path, "**", f"*{filename}*")
        files = glob.glob(pattern, recursive=True)
        return files

    def create_folder(self, path):
        """Creates a directory at the specified path."""
        try:
            os.makedirs(path, exist_ok=True)
            return f"Successfully created folder at {path}"
        except Exception as e:
            return f"Error creating folder: {e}"

    def move_file(self, src, dst):
        """Moves a file or folder from src to dst."""
        try:
            shutil.move(src, dst)
            return f"Moved {src} to {dst}"
        except Exception as e:
            return f"Error moving file: {e}"

    def delete_file(self, path):
        """Deletes a file or folder."""
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return f"Deleted {path}"
        except Exception as e:
            return f"Error deleting: {e}"

    # --- Application Control ---
    def launch_app(self, app_name):
        """
        Attempts to launch an application.
        app_name can be a system command (like 'notepad') or a path to an exe.
        """
        try:
            subprocess.Popen(app_name, shell=True)
            return f"Launched {app_name}"
        except Exception as e:
            return f"Error launching {app_name}: {e}"

    def close_app(self, app_name):
        """Closes an application by its name in the process list."""
        found = False
        for proc in psutil.process_iter(['name']):
            if app_name.lower() in proc.info['name'].lower():
                proc.kill()
                found = True
        return f"Closed {app_name}" if found else f"Could not find process {app_name}"

    # --- Desktop Automation ---
    def type_text(self, text):
        """Types the provided text using the keyboard."""
        pyautogui.write(text, interval=0.05)
        return f"Typed: {text}"

    def press_key(self, key):
        """Presses a specific key (e.g., 'enter', 'esc', 'win')."""
        pyautogui.press(key)
        return f"Pressed key: {key}"

    def screenshot(self, filename="screenshot.png"):
        """Takes a screenshot and saves it to the specified filename."""
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            return f"Screenshot saved as {filename}"
        except Exception as e:
            return f"Error taking screenshot: {e}"

    def set_window_focus(self, app_name):
        """
        This is a simplified version. Real window management
        usually requires pygetwindow or pywin32.
        """
        return "Window focus management requires additional libraries (pygetwindow)."

# Global instance for easy import in <PYTHON> blocks
actions = JarvisActions()
