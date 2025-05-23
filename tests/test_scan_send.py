import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
import json
import datetime
import io

# Add the parent directory to sys.path to allow importing scan_send
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scan_send

class TestScanSend(unittest.TestCase):

    def setUp(self):
        """Redirect stdout and stderr to capture print statements."""
        self.held_stdout = sys.stdout
        self.held_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        # Common mock environment variables
        self.mock_env = {
            "PHONE_ID": "test_phone_id",
            "WABA_TOKEN": "test_waba_token",
            "USER_NUMBER": "test_user_number",
            "TEMPLATE_NS": "test_template_ns",
            "TEMPLATE_NM": "test_template_name",
            "LANG_CODE": "en_US"
        }
        # Fixed datetime for consistent tests
        self.mock_datetime = datetime.datetime(2023, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)


    def tearDown(self):
        """Restore stdout and stderr."""
        sys.stdout = self.held_stdout
        sys.stderr = self.held_stderr

    # Test getenv_or_exit
    @patch('os.getenv')
    def test_getenv_or_exit_success(self, mock_getenv):
        mock_getenv.return_value = "test_value"
        self.assertEqual(scan_send.getenv_or_exit("TEST_VAR"), "test_value")
        mock_getenv.assert_called_once_with("TEST_VAR")

    @patch('os.getenv')
    @patch('sys.exit')
    def test_getenv_or_exit_failure_none(self, mock_sys_exit, mock_getenv):
        mock_getenv.return_value = None
        scan_send.getenv_or_exit("TEST_VAR_NONE")
        mock_sys_exit.assert_called_once_with(1)
        self.assertIn("ERROR: environment variable 'TEST_VAR_NONE' is not set or empty.", sys.stderr.getvalue())

    @patch('os.getenv')
    @patch('sys.exit')
    def test_getenv_or_exit_failure_empty(self, mock_sys_exit, mock_getenv):
        mock_getenv.return_value = ""
        scan_send.getenv_or_exit("TEST_VAR_EMPTY")
        mock_sys_exit.assert_called_once_with(1)
        self.assertIn("ERROR: environment variable 'TEST_VAR_EMPTY' is not set or empty.", sys.stderr.getvalue())

    # Test TEMPLATE_NS and TEMPLATE_NM handling
    @patch.dict(os.environ, {}, clear=True) # Start with a clean environment
    @patch('sys.exit') # Mock sys.exit to prevent test runner from exiting
    def test_template_vars_missing_uses_placeholders_and_warns(self, mock_sys_exit):
        # Mock only essential vars for this test, letting TEMPLATE_NS and TEMPLATE_NM be missing
        with patch.dict(os.environ, {
            "PHONE_ID": "test_phone_id",
            "WABA_TOKEN": "test_waba_token",
            "USER_NUMBER": "test_user_number",
        }):
            # We expect sys.exit to be called by getenv_or_exit for PHONE_ID etc.
            # but we are testing the warning for TEMPLATE_NS/NM before that would happen
            # if they were also using getenv_or_exit.
            # For this test, we only care about the warnings and placeholder logic.
            # The main() function will still try to run and call getenv_or_exit for required ones.
            # Let's mock requests.post to avoid actual API calls and let the script proceed further
            with patch('requests.post', return_value=MagicMock(ok=True, status_code=200, json=lambda: {"status": "success"}, text="Success")):
                scan_send.main(current_time_utc=self.mock_datetime)

        stderr_output = sys.stderr.getvalue()
        self.assertIn("WARNING: Environment variable 'TEMPLATE_NS' is not set.", stderr_output)
        self.assertIn("Using placeholder value 'your_template_namespace_here'", stderr_output)
        self.assertIn("WARNING: Environment variable 'TEMPLATE_NM' is not set.", stderr_output)
        self.assertIn("Using placeholder value 'your_template_name_here'", stderr_output)
        
        stdout_output = sys.stdout.getvalue()
        # Check if placeholders are used in the payload
        self.assertIn("your_template_namespace_here:your_template_name_here", stdout_output)


    @patch.dict(os.environ, {}, clear=True)
    @patch('requests.post')
    def test_template_vars_provided_are_used(self, mock_requests_post):
        mock_requests_post.return_value = MagicMock(ok=True, status_code=200, json=lambda: {"status": "success"}, text="Success")
        with patch.dict(os.environ, self.mock_env):
            scan_send.main(current_time_utc=self.mock_datetime)
        
        stdout_output = sys.stdout.getvalue()
        self.assertNotIn("your_template_namespace_here", stdout_output)
        self.assertNotIn("your_template_name_here", stdout_output)
        self.assertIn("test_template_ns:test_template_name", stdout_output)
        stderr_output = sys.stderr.getvalue()
        self.assertNotIn("WARNING: Environment variable 'TEMPLATE_NS' is not set.", stderr_output)
        self.assertNotIn("WARNING: Environment variable 'TEMPLATE_NM' is not set.", stderr_output)


    # Test LANG_CODE
    @patch.dict(os.environ, {}, clear=True)
    @patch('requests.post')
    def test_lang_code_defaults_to_en_us(self, mock_requests_post):
        mock_requests_post.return_value = MagicMock(ok=True, status_code=200, json=lambda: {"status": "success"}, text="Success")
        # Ensure LANG_CODE is not in the environment for this test
        env_without_lang_code = self.mock_env.copy()
        del env_without_lang_code["LANG_CODE"]
        with patch.dict(os.environ, env_without_lang_code):
            scan_send.main(current_time_utc=self.mock_datetime)
        
        stdout_output = sys.stdout.getvalue()
        payload_str = [line for line in stdout_output.split('\n') if line.startswith("▶️ PAYLOAD:")]
        self.assertTrue(payload_str)
        payload = json.loads(payload_str[0].replace("▶️ PAYLOAD: ", ""))
        self.assertEqual(payload["template"]["language"]["code"], "en_US")

    @patch.dict(os.environ, {}, clear=True)
    @patch('requests.post')
    def test_lang_code_uses_provided_value(self, mock_requests_post):
        mock_requests_post.return_value = MagicMock(ok=True, status_code=200, json=lambda: {"status": "success"}, text="Success")
        custom_lang_env = self.mock_env.copy()
        custom_lang_env["LANG_CODE"] = "fr_FR"
        with patch.dict(os.environ, custom_lang_env):
            scan_send.main(current_time_utc=self.mock_datetime)

        stdout_output = sys.stdout.getvalue()
        payload_str = [line for line in stdout_output.split('\n') if line.startswith("▶️ PAYLOAD:")]
        self.assertTrue(payload_str)
        payload = json.loads(payload_str[0].replace("▶️ PAYLOAD: ", ""))
        self.assertEqual(payload["template"]["language"]["code"], "fr_FR")

    # Test API Request Payload Construction
    @patch.dict(os.environ, {}, clear=True)
    @patch('requests.post') # Mock requests.post to prevent actual API call
    def test_payload_construction(self, mock_requests_post):
        mock_requests_post.return_value = MagicMock(ok=True, status_code=200, json=lambda: {"status": "success"}, text="Success")
        with patch.dict(os.environ, self.mock_env):
            scan_send.main(current_time_utc=self.mock_datetime)

        stdout_output = sys.stdout.getvalue()
        payload_str_lines = [line for line in stdout_output.split('\n') if line.startswith("▶️ PAYLOAD:")]
        self.assertTrue(payload_str_lines, "Payload debug print not found in stdout.")
        
        # Reconstruct the JSON string from potentially multiple lines if it was pretty-printed
        actual_payload_json_str = "".join(payload_str_lines).replace("▶️ PAYLOAD: ", "")
        actual_payload = json.loads(actual_payload_json_str)
        
        expected_footer = f"⏰ Note: Risk limited to $95 • {self.mock_datetime.strftime('%H:%M UTC')}"
        expected_payload = {
            "messaging_product": "whatsapp",
            "to": "test_user_number",
            "type": "template",
            "template": {
                "name": "test_template_ns:test_template_name",
                "language": {"code": "en_US"},
                "components": [{
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "📰 Market News: Apple beats Q2 earnings"},
                        {"type": "text", "text": "💹 Trade: AAPL – Jul 19 $175/$180 bull-call-spread"},
                        {"type": "text", "text": expected_footer}
                    ]
                }]
            }
        }
        self.assertEqual(actual_payload, expected_payload)
        
        # Also check URL and Headers
        self.assertIn(f"▶️ URL    : https://graph.facebook.com/v19.0/{self.mock_env['PHONE_ID']}/messages", stdout_output)
        headers_str_lines = [line for line in stdout_output.split('\n') if line.startswith("▶️ HEADERS:")]
        self.assertTrue(headers_str_lines, "Headers debug print not found in stdout.")
        actual_headers_json_str = "".join(headers_str_lines).replace("▶️ HEADERS: ", "")
        actual_headers = json.loads(actual_headers_json_str)
        expected_headers = {
            "Authorization": f"Bearer {self.mock_env['WABA_TOKEN']}",
            "Content-Type": "application/json"
        }
        self.assertEqual(actual_headers, expected_headers)


    # Test API Call Success
    @patch.dict(os.environ, {}, clear=True)
    @patch('requests.post')
    @patch('sys.exit')
    def test_api_call_success(self, mock_sys_exit, mock_requests_post):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.text = '{"status": "success"}'
        mock_requests_post.return_value = mock_response

        with patch.dict(os.environ, self.mock_env):
            scan_send.main(current_time_utc=self.mock_datetime)

        mock_sys_exit.assert_not_called()
        self.assertIn("✅ Message sent successfully!", sys.stdout.getvalue())
        self.assertIn('⏱ Status: 200', sys.stdout.getvalue())
        self.assertIn('{"status": "success"}', sys.stdout.getvalue())


    # Test API Call Failure
    @patch.dict(os.environ, {}, clear=True)
    @patch('requests.post')
    @patch('sys.exit')
    def test_api_call_failure_json_response(self, mock_sys_exit, mock_requests_post):
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {
                "message": "Test API error message",
                "code": 132000,
                "type": "OAuthException",
                "fbtrace_id": "test_fbtrace_id",
                "error_data": {"details": "some error data"}
            }
        }
        mock_response.text = json.dumps(mock_response.json.return_value) # ensure text matches json
        mock_requests_post.return_value = mock_response

        with patch.dict(os.environ, self.mock_env):
            scan_send.main(current_time_utc=self.mock_datetime)

        mock_sys_exit.assert_called_once_with(1)
        stderr_output = sys.stderr.getvalue()
        self.assertIn("❌ API error.message   : Test API error message", stderr_output)
        self.assertIn("❌ API error.code      : 132000", stderr_output)
        self.assertIn("❌ API error.type      : OAuthException", stderr_output)
        self.assertIn("❌ API error.fbtrace_id: test_fbtrace_id", stderr_output)
        self.assertIn("\"details\": \"some error data\"", stderr_output)
        # Check that raw response is also printed to stdout before error details to stderr
        self.assertIn('⏱ Status: 400', sys.stdout.getvalue())
        self.assertIn("Test API error message", sys.stdout.getvalue())


    @patch.dict(os.environ, {}, clear=True)
    @patch('requests.post')
    @patch('sys.exit')
    def test_api_call_failure_non_json_response(self, mock_sys_exit, mock_requests_post):
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error - Not JSON"
        # Make json() raise an error to simulate non-JSON response
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "doc", 0)
        mock_requests_post.return_value = mock_response

        with patch.dict(os.environ, self.mock_env):
            scan_send.main(current_time_utc=self.mock_datetime)

        mock_sys_exit.assert_called_once_with(1)
        stderr_output = sys.stderr.getvalue()
        self.assertIn("❌ Failed to parse error response as JSON. Raw response above.", stderr_output)
        # Check that raw response is also printed to stdout
        self.assertIn('⏱ Status: 500', sys.stdout.getvalue())
        self.assertIn("Internal Server Error - Not JSON", sys.stdout.getvalue())


    # Test API Connection Error
    @patch.dict(os.environ, {}, clear=True)
    @patch('requests.post')
    @patch('sys.exit')
    def test_api_connection_error(self, mock_sys_exit, mock_requests_post):
        mock_requests_post.side_effect = requests.exceptions.ConnectionError("Test connection error")

        with patch.dict(os.environ, self.mock_env):
            scan_send.main(current_time_utc=self.mock_datetime)

        mock_sys_exit.assert_called_once_with(1)
        self.assertIn("❌ ERROR: Connection error. Could not connect to https://graph.facebook.com/v19.0/test_phone_id/messages. Details: Test connection error", sys.stderr.getvalue())

    @patch.dict(os.environ, {}, clear=True)
    @patch('requests.post')
    @patch('sys.exit')
    def test_api_timeout_error(self, mock_sys_exit, mock_requests_post):
        mock_requests_post.side_effect = requests.exceptions.Timeout("Test timeout error")

        with patch.dict(os.environ, self.mock_env):
            scan_send.main(current_time_utc=self.mock_datetime)

        mock_sys_exit.assert_called_once_with(1)
        self.assertIn("❌ ERROR: Request timed out while trying to reach https://graph.facebook.com/v19.0/test_phone_id/messages. Details: Test timeout error", sys.stderr.getvalue())

    @patch.dict(os.environ, {}, clear=True)
    @patch('requests.post')
    @patch('sys.exit')
    def test_api_request_exception(self, mock_sys_exit, mock_requests_post):
        mock_requests_post.side_effect = requests.exceptions.RequestException("Test generic request exception")

        with patch.dict(os.environ, self.mock_env):
            scan_send.main(current_time_utc=self.mock_datetime)
        
        mock_sys_exit.assert_called_once_with(1)
        self.assertIn("❌ ERROR: An error occurred during the API request to https://graph.facebook.com/v19.0/test_phone_id/messages. Details: Test generic request exception", sys.stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
