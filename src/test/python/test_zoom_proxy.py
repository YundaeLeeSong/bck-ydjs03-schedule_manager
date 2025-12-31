#!/usr/bin/env python3
"""
test_zoom_proxy.py — Unit tests for zoomproxy.core

Run with:
    python runner.py test
"""

import unittest
import os
from unittest.mock import patch, MagicMock
from zoomproxy import RealZoomService, ZoomProxy

class TestRealZoomService(unittest.TestCase):
    def setUp(self):
        self.env_patcher = patch.dict(os.environ, {
            "ZOOM_ACCOUNT_ID": "acc_id",
            "ZOOM_CLIENT_ID": "client_id",
            "ZOOM_CLIENT_SECRET": "client_secret"
        })
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    @patch("requests.post")
    def test_get_token_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "fake_token"}
        mock_post.return_value = mock_response

        service = RealZoomService()
        token = service._get_token()
        
        self.assertEqual(token, "fake_token")
        self.assertIn("https://zoom.us/oauth/token", mock_post.call_args[0][0])

    @patch("requests.post")
    def test_get_token_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        service = RealZoomService()
        token = service._get_token()
        
        self.assertIsNone(token)

    @patch("requests.post")
    def test_create_meeting_success(self, mock_post):
        # Setup mocks
        # First call: Auth (success)
        # Second call: Create Meeting (success)
        
        mock_auth_resp = MagicMock()
        mock_auth_resp.status_code = 200
        mock_auth_resp.json.return_value = {"access_token": "fake_token"}
        
        mock_meet_resp = MagicMock()
        mock_meet_resp.status_code = 201
        mock_meet_resp.json.return_value = {"join_url": "https://zoom.us/j/123"}
        
        mock_post.side_effect = [mock_auth_resp, mock_meet_resp]

        service = RealZoomService()
        result = service.create_meeting("Test Topic", "2025-01-01 10:00", 60)
        
        self.assertEqual(result.get("join_url"), "https://zoom.us/j/123")

    @patch("requests.post")
    def test_create_meeting_auth_fail(self, mock_post):
        # Auth fails
        mock_auth_resp = MagicMock()
        mock_auth_resp.status_code = 400
        mock_post.return_value = mock_auth_resp

        service = RealZoomService()
        result = service.create_meeting("Test Topic", "2025-01-01 10:00", 60)
        
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Authentication failed")

class TestZoomProxy(unittest.TestCase):
    @patch.dict(os.environ, {
        "ZOOM_ACCOUNT_ID": "acc_id",
        "ZOOM_CLIENT_ID": "client_id",
        "ZOOM_CLIENT_SECRET": "client_secret"
    })
    @patch("zoomproxy.core.RealZoomService")
    def test_proxy_delegates_success(self, MockRealService):
        # Setup Mock Service
        mock_instance = MockRealService.return_value
        mock_instance.create_meeting.return_value = {"join_url": "https://zoom.us/j/123"}
        
        proxy = ZoomProxy()
        result = proxy.create_meeting("Topic", "2025-01-01 10:00", 60)
        
        self.assertEqual(result["join_url"], "https://zoom.us/j/123")
        mock_instance.create_meeting.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    def test_proxy_missing_credentials(self):
        # Ensure env is clear of zoom creds
        proxy = ZoomProxy()
        result = proxy.create_meeting("Topic", "2025-01-01 10:00", 60)
        
        self.assertIn("error", result)
        self.assertIn("Missing ZOOM credentials", result["error"])

if __name__ == "__main__":
    unittest.main()
