# AI-Powered Customer Service Chatbot

A sophisticated customer service chatbot that combines speech recognition, natural language processing, and text-to-speech capabilities using Gemini AI, ElevenLabs, and MySQL integration.

## Features

- 🎙️ **Voice Interface**: Speech-to-text and text-to-speech capabilities
- 🤖 **Gemini AI Integration**: Smart conversation handling with context awareness
- 🗣️ **ElevenLabs Voice**: High-quality text-to-speech conversion
- 📅 **Appointment Management**: Handles meeting scheduling
- 💾 **Database Integration**: Stores conversations and sentiment analysis
- 📊 **Sentiment Analysis**: Analyzes customer interactions
- 🔄 **MCP (Model Context Protocol)**: Tool integration for enhanced functionality

## Prerequisites

- Python 3.11+
- MySQL Server
- Required API Keys:
  - Google Gemini API Key
  - ElevenLabs API Key

## Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
cd mcp101
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with:
```env
GOOGLE_API_KEY=your_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

4. Set up MySQL Database:
```sql
CREATE DATABASE customer_service;
USE customer_service;

CREATE TABLE customer (
    customer_id INT PRIMARY KEY,
    first_name VARCHAR(100),
    topic VARCHAR(200),
    meeting_date DATE
);

CREATE TABLE sentiment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    text TEXT NOT NULL,
    t_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Usage

1. Start the MCP server:
```bash
python database_funcs.py
```

2. Run the chatbot:
```bash
python main.py
```

3. Speak to the bot and wait for its response. The bot will:
   - Convert your speech to text
   - Process your request using Gemini AI
   - Generate and play an audio response
   - Store the conversation in the database

## Project Structure

- `main.py`: Main application file with CustomerServiceBot class
- `database_funcs.py`: Database operations and MCP tools
- `speech2text.py`: Speech recognition functionality
- `prompts.py`: System prompts and templates
- `logger_config.py`: Logging configuration
- `requirements.txt`: Project dependencies

## Configuration

- Adjust voice settings in `text_to_speech_file()` method
- Modify system prompts in `prompts.py`
- Configure logging levels in `logger_config.py`

## Key Components

1. **CustomerServiceBot Class**
   - Handles main bot functionality
   - Manages API clients and chat sessions
   - Processes voice input/output

2. **Database Functions**
   - Customer management
   - Meeting scheduling
   - Conversation storage
   - Sentiment analysis

3. **Speech Processing**
   - Speech recognition with error handling
   - Text-to-speech conversion
   - Audio playback management

## Error Handling

The application includes comprehensive error handling for:
- API connection issues
- Speech recognition failures
- Database operations
- Audio processing errors

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

[Choose your license]

## Acknowledgments

- Google Gemini AI for natural language processing
- ElevenLabs for text-to-speech capabilities
- FastMCP for tool integration
