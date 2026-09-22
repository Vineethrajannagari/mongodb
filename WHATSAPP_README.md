# WhatsApp Message Sender

An enhanced FastAPI application for sending WhatsApp messages through the official WhatsApp Business Cloud API with retry logic, message tracking, and MongoDB integration.

## Features

- **Send Text Messages**: Send free-form text messages to recipients
- **Send Template Messages**: Send pre-approved template messages (required for new conversations)
- **Message Status Tracking**: Check delivery status of sent messages
- **Message History**: Log all messages to MongoDB for tracking and analytics
- **Retry Logic**: Automatic retry with exponential backoff for transient failures
- **Health Check**: Monitor service status and configuration
- **Statistics**: Get messaging statistics from MongoDB

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your WhatsApp Business API credentials:

```env
# MongoDB Connection (optional - leave empty to disable logging)
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=whatsapp_sender

# WhatsApp Business API Configuration
WHATSAPP_ACCESS_TOKEN=your_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
GRAPH_API_VERSION=v21.0

# Retry Configuration
MAX_RETRIES=3
RETRY_DELAY=2
```

### 3. Get WhatsApp API Credentials

1. Go to [developers.facebook.com](https://developers.facebook.com/)
2. Create an app or select an existing one
3. Add WhatsApp product to your app
4. Go to WhatsApp > API Setup
5. Copy your **Access Token** and **Phone Number ID**
6. Add recipient phone numbers to the test recipient list (required in test mode)

### 4. Run the Server

```bash
python whatsapp_sender.py
```

The API will be available at `http://127.0.0.1:8000`

Interactive API documentation: `http://127.0.0.1:8000/docs`

## API Endpoints

### Health Check

```bash
GET /health
```

Returns service status and configuration.

### Send Text Message

```bash
POST /send-message
Content-Type: application/json

{
  "phone": "919876543210",
  "message": "Hey bro, how are you?"
}
```

**Note**: Free-form text messages only work if the recipient has messaged your number in the last 24 hours.

### Send Template Message

```bash
POST /send-template
Content-Type: application/json

{
  "phone": "919876543210",
  "template_name": "hello_world",
  "language_code": "en_US"
}
```

Template messages can start new conversations. Meta's test number includes a template called "hello_world".

### Get Message Status

```bash
GET /message-status?message_id=your_message_id
```

Check the delivery status of a previously sent message.

### Get Message History

```bash
GET /messages?limit=50&phone=919876543210&status=accepted
```

Retrieve message history from MongoDB (requires MongoDB configuration).

- `limit`: Number of messages to return (1-200, default: 50)
- `phone`: Filter by phone number (optional)
- `status`: Filter by status (optional)

### Get Statistics

```bash
GET /stats
```

Get messaging statistics from MongoDB (requires MongoDB configuration).

## Usage Examples

### Using cURL

Send a template message:
```bash
curl -X POST http://127.0.0.1:8000/send-template \
     -H "Content-Type: application/json" \
     -d '{"phone": "919876543210"}'
```

Send a text message:
```bash
curl -X POST http://127.0.0.1:8000/send-message \
     -H "Content-Type: application/json" \
     -d '{"phone": "919876543210", "message": "Hey bro, how are you?"}'
```

Check message status:
```bash
curl http://127.0.0.1:8000/message-status?message_id=your_message_id
```

### Using Python

```python
import requests

# Send template message
response = requests.post(
    "http://127.0.0.1:8000/send-template",
    json={"phone": "919876543210"}
)
print(response.json())

# Send text message
response = requests.post(
    "http://127.0.0.1:8000/send-message",
    json={
        "phone": "919876543210",
        "message": "Hey bro, how are you?"
    }
)
print(response.json())
```

## Important Notes

- **Message Status**: "accepted" means WhatsApp queued the message, not that it was delivered
- **Token Expiry**: Temporary tokens from the dashboard expire after about 24 hours
- **Test Mode**: In test mode, you can only message numbers added to your recipient list
- **24-Hour Window**: Free-form text messages require the recipient to have messaged you in the last 24 hours
- **Compliance**: Only message people who agreed to hear from you. This uses the official API only.

## Error Handling

The application includes automatic retry logic for:
- Network failures
- Rate limiting (HTTP 429)
- Server errors (HTTP 5xx)

Retries use exponential backoff with configurable settings.

## MongoDB Integration

When MongoDB is configured, the application logs:
- All message send attempts
- Message status (accepted/failed)
- WhatsApp message IDs
- Error details
- Timestamps

This enables tracking, analytics, and debugging.

## Configuration Options

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `WHATSAPP_ACCESS_TOKEN` | WhatsApp API access token | Required |
| `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp phone number ID | Required |
| `GRAPH_API_VERSION` | Facebook Graph API version | `v21.0` |
| `MONGODB_URI` | MongoDB connection string | Optional |
| `MONGODB_DB` | MongoDB database name | `whatsapp_sender` |
| `MAX_RETRIES` | Maximum retry attempts | `3` |
| `RETRY_DELAY` | Initial retry delay in seconds | `2` |

## Troubleshooting

### Server Configuration Error
If you see "Server is missing WHATSAPP_ACCESS_TOKEN or WHATSAPP_PHONE_NUMBER_ID", ensure your `.env` file is properly configured.

### MongoDB Connection Error
MongoDB errors are logged as warnings but won't prevent message sending. The application will function without MongoDB.

### Message Not Delivered
- Check that the recipient is in your test recipient list (test mode)
- For text messages, ensure the recipient messaged you in the last 24 hours
- Use template messages to start new conversations
- Verify your access token hasn't expired

## License

This project uses the official WhatsApp Business Cloud API. Ensure you comply with WhatsApp's terms of service and messaging policies.
