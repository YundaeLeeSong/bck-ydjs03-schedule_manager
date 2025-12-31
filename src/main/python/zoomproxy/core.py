# zoomproxy/core.py
import os
import requests
import json
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import sys

# Load .env
SRC_DIR = Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path("").resolve() # absolute path
ENV_PATH = SRC_DIR / Path(".env")                                                     # absolute path to the .env file 
from dotenv import load_dotenv                                       # dotenv is used to load the environment variables from the .env file
load_dotenv(dotenv_path=ENV_PATH)

class IZoomService(ABC):
    """Interface for Zoom Service."""
    @abstractmethod
    def create_meeting(self, topic: str, start_time_str: str, duration_min: int) -> Dict[str, Any]:
        """
        Create a meeting.

        Args:
            topic (str): The meeting topic.
            start_time_str (str): The start time in "YYYY-MM-DD HH:MM" format.
            duration_min (int): Duration in minutes.

        Returns:
            Dict[str, Any]: The result dictionary from the API or an error dict.
        """
        pass

class RealZoomService(IZoomService):
    """Actual implementation using Zoom API."""
    def __init__(self):
        self.account_id: Optional[str] = os.getenv("ZOOM_ACCOUNT_ID")
        self.client_id: Optional[str] = os.getenv("ZOOM_CLIENT_ID")
        self.client_secret: Optional[str] = os.getenv("ZOOM_CLIENT_SECRET")
        self.token: Optional[str] = None
    
    def _get_token(self) -> Optional[str]:
        """
        Authenticate with Zoom to get an access token.

        Returns:
            Optional[str]: The access token if successful, None otherwise.
        """
        url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={self.account_id}"
        auth = (self.client_id, self.client_secret)
        try:
            response = requests.post(url, auth=auth)
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                return self.token
            else:
                print(f"Zoom Auth Error: {response.text}")
                return None
        except Exception as e:
            print(f"Connection Error: {e}")
            return None

    def create_meeting(self, topic: str, start_time_str: str, duration_min: int) -> Dict[str, Any]:
        """
        Create a scheduled meeting on Zoom.

        Args:
            topic (str): The meeting topic.
            start_time_str (str): The start time in "YYYY-MM-DD HH:MM" format (assumed local).
            duration_min (int): Duration in minutes.

        Returns:
            Dict[str, Any]: API response JSON or error dictionary.
        """
        if not self.token:
            if not self._get_token():
                return {"error": "Authentication failed"}

        url = "https://api.zoom.us/v2/users/me/meetings"
        
        # Parse time string "YYYY-MM-DD HH:MM" (Local Time) -> UTC ISO Format
        try:
            # 1. Parse naive string (assumed local)
            dt_naive = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
            # 2. Make it aware (Local) using astimezone() without arguments
            dt_local = dt_naive.astimezone() 
            # 3. Convert to UTC
            dt_utc = dt_local.astimezone(timezone.utc)
            # 4. Format as ISO 8601 with Z
            iso_start = dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError as e:
            return {"error": f"Date error: {e}"}

        payload = {
            "topic": topic,
            "type": 2,  # Scheduled
            "start_time": iso_start,
            "duration": duration_min,
            "timezone": "UTC", 
            "agenda": "Tutoring Session"
        }
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 201:
                return response.json()
            elif response.status_code == 401:
                # Token might be expired, retry once
                if self._get_token():
                    headers["Authorization"] = f"Bearer {self.token}"
                    response = requests.post(url, json=payload, headers=headers)
                    if response.status_code == 201:
                        return response.json()
            return {"error": f"API Error {response.status_code}: {response.text}"}
        except Exception as e:
            return {"error": f"Request Error: {e}"}

class ZoomProxy(IZoomService):
    """
    Proxy to control access to RealZoomService.
    Adds checking for credentials and logging.
    """
    def __init__(self):
        self._real_service: Optional[RealZoomService] = None
    
    def _get_service(self) -> RealZoomService:
        """Lazy load the real service."""
        if self._real_service is None:
            self._real_service = RealZoomService()
        return self._real_service

    def create_meeting(self, topic: str, start_time_str: str, duration_min: int) -> Dict[str, Any]:
        """
        Delegates meeting creation to the RealZoomService if credentials exist.

        Args:
            topic (str): The meeting topic.
            start_time_str (str): The start time in "YYYY-MM-DD HH:MM" format.
            duration_min (int): Duration in minutes.

        Returns:
            Dict[str, Any]: Result from RealZoomService or error if credentials missing.
        """
        # Pre-check: Environment variables
        if not all([os.getenv("ZOOM_ACCOUNT_ID"), os.getenv("ZOOM_CLIENT_ID"), os.getenv("ZOOM_CLIENT_SECRET")]):
            return {"error": "Missing ZOOM credentials in .env file."}
        
        print(f"[Proxy] Delegating meeting creation for '{topic}'...")
        result = self._get_service().create_meeting(topic, start_time_str, duration_min)
        
        if "join_url" in result:
            print(f"[Proxy] Success: {result['join_url']}")
        else:
            print(f"[Proxy] Failed: {result.get('error')}")
            
        return result
