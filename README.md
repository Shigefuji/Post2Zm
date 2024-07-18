readme_content = """
# ZmChat - Zoom Chat API Integration

ZmChat is a Python program for integrating with the Zoom Chat API to schedule meetings, create chat channels, send messages, and update user presence status.

## Prerequisites

Before using ZmChat, ensure you have the following:

- Python 3.x installed on your system.
- Zoom account with API access credentials (account ID, client ID, client secret).
- `.env.local` file containing your Zoom API credentials and channel name in JSON format. Example:
  ```json
  {
    "ZOOM_ACCOUNT_ID": "your_account_id",
    "ZOOM_CLIENT_ID": "your_client_id",
    "ZOOM_CLIENT_SECRET": "your_client_secret",
    "ZOOM_CHANNEL_NAME": "your_channel_name"
  }

## Installation
Clone the repository or download the zm_chat.py file.
Install the required Python packages using pip:
pip install requests

## Usage
Ensure your .env.local file is correctly configured with your Zoom API credentials.
Run the zm_chat.py script:
python zm_chat.py
The program will send a greeting message to your specified Zoom chat channel based on the current time.

## Functionality
schedule_meeting(topic=None, start_time=None, duration=60): Schedule a Zoom meeting and return the join URL.
create_chat_channel(channel_name): Create a Zoom chat channel and return the join URL.
send_message(channel_name, message): Send a message to a specified Zoom chat channel.
update_presence_status(status): Update the user's presence status on Zoom.

## Example
python
from zm_chat import ZmChat

# Initialize ZmChat instance
zm_chat = ZmChat('.env.local')

# Schedule a meeting
join_url = zm_chat.schedule_meeting(topic="Team Meeting", start_time="2024-06-20T10:00:00", duration=60)
print(f"Scheduled meeting URL: {join_url}")

# Create a chat channel
channel_url = zm_chat.create_chat_channel("Team Chat")
print(f"Created channel URL: {channel_url}")

# Send a message
zm_chat.send_message("Team Chat", "Hello everyone!")

# Update presence status
zm_chat.update_presence_status("Busy")

## License
This project is licensed under the MIT License - see the LICENSE file for details.