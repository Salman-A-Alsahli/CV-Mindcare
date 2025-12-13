"""
Auto-updater for CV-Mindcare
----------------------------
Checks GitHub releases for newer versions.
"""

import requests
import threading
from typing import Optional, Callable
from packaging import version
import logging

logger = logging.getLogger(__name__)

# Current version
CURRENT_VERSION = "0.1.0"

# GitHub repository information
GITHUB_OWNER = "yourusername"  # TODO: Update with actual GitHub username
GITHUB_REPO = "cv-mindcare"
RELEASES_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"


class UpdateInfo:
    """Information about an available update."""

    def __init__(self, version: str, release_notes: str, download_url: str):
        self.version = version
        self.release_notes = release_notes
        self.download_url = download_url

    def __repr__(self):
        return f"UpdateInfo(version={self.version})"


class Updater:
    """Auto-updater to check for new versions."""

    def __init__(self, current_version: str = CURRENT_VERSION):
        """
        Initialize updater.

        Args:
            current_version: Current application version
        """
        self.current_version = current_version
        self.latest_version = None
        self.update_info: Optional[UpdateInfo] = None
        self._checking = False

    def check_for_updates(self, callback: Optional[Callable[[Optional[UpdateInfo]], None]] = None):
        """
        Check for updates asynchronously.

        Args:
            callback: Function to call with UpdateInfo or None if no update
        """
        if self._checking:
            logger.info("Update check already in progress")
            return

        self._checking = True
        thread = threading.Thread(target=self._check_updates_thread, args=(callback,), daemon=True)
        thread.start()

    def _check_updates_thread(self, callback: Optional[Callable]):
        """Background thread to check for updates."""
        try:
            update_info = self._fetch_latest_release()
            self.update_info = update_info

            if callback:
                callback(update_info)
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            if callback:
                callback(None)
        finally:
            self._checking = False

    def _fetch_latest_release(self) -> Optional[UpdateInfo]:
        """
        Fetch the latest release from GitHub.

        Returns:
            UpdateInfo if a newer version is available, None otherwise
        """
        try:
            # Make request to GitHub API
            response = requests.get(RELEASES_API_URL, timeout=10)

            if response.status_code == 404:
                logger.info("No releases found on GitHub")
                return None

            response.raise_for_status()
            data = response.json()

            # Extract version information
            tag_name = data.get("tag_name", "")
            # Remove 'v' prefix if present
            latest_version = tag_name.lstrip("v")

            # Compare versions
            if self._is_newer_version(latest_version):
                self.latest_version = latest_version

                # Extract release information
                release_notes = data.get("body", "No release notes available.")
                download_url = data.get("html_url", "")

                # Look for Windows installer in assets
                assets = data.get("assets", [])
                for asset in assets:
                    if asset.get("name", "").endswith((".exe", ".zip")):
                        download_url = asset.get("browser_download_url", download_url)
                        break

                logger.info(f"New version available: {latest_version}")
                return UpdateInfo(latest_version, release_notes, download_url)
            else:
                logger.info(f"Current version {self.current_version} is up to date")
                return None

        except requests.RequestException as e:
            logger.error(f"Network error while checking for updates: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing release information: {e}")
            return None

    def _is_newer_version(self, latest: str) -> bool:
        """
        Compare version strings.

        Args:
            latest: Latest version string

        Returns:
            True if latest is newer than current
        """
        try:
            return version.parse(latest) > version.parse(self.current_version)
        except Exception as e:
            logger.error(f"Error comparing versions: {e}")
            return False

    def get_download_url(self) -> Optional[str]:
        """Get the download URL for the latest version."""
        if self.update_info:
            return self.update_info.download_url
        return None

    def get_release_notes(self) -> Optional[str]:
        """Get the release notes for the latest version."""
        if self.update_info:
            return self.update_info.release_notes
        return None


def check_for_updates_async(callback: Callable[[Optional[UpdateInfo]], None]):
    """
    Convenience function to check for updates.

    Args:
        callback: Function to call with update information
    """
    updater = Updater()
    updater.check_for_updates(callback)


# Example usage for testing
if __name__ == "__main__":
    import time

    logging.basicConfig(level=logging.INFO)

    def on_update_available(update_info: Optional[UpdateInfo]):
        if update_info:
            print(f"🎉 New version available: {update_info.version}")
            print(f"Download: {update_info.download_url}")
            print(f"Release notes:\n{update_info.release_notes[:200]}...")
        else:
            print("✓ You're up to date!")

    print(f"Checking for updates (current version: {CURRENT_VERSION})...")
    check_for_updates_async(on_update_available)

    # Wait for async check to complete
    time.sleep(5)
