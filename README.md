# AI-Powered Voice Customer Support Assistant
![Workflow](https://github.com/user-attachments/assets/fc160859-fa83-4bbc-9daf-5a4a73f7d608)


## Demo Video



https://github.com/user-attachments/assets/244d3985-0c7c-4972-9ca8-a428ca53029a

## Overview🔎

This project aims that combining voice user interaction with artificial intelligence . It converts user voice to text in realtime , Google gemini analyze it and give answer then finally send response in natural voice with elevenlabs.
This system plans meetings, give informations and makes sentiment analyzes.

## Features⚙️

- 🎙️ **Voice **: Speech-to-text and text-to-speech capabilities
- 🤖 **Gemini AI Integration**: Smart conversation handling with context awareness
- 🗣️ **ElevenLabs Voice**: High-quality text-to-speech conversion
- 📅 **Appointment Management**: Handles meeting scheduling
- 📊 **Sentiment Analysis**: Analyzes customer interactions and labels as positive neutral or negative thanks to saribasmetehan/bert-base-turkish-sentiment-analysis
- 💾 **Database Integration**: Stores appointment dates, conversations and  sentiment analysis.

## Sentiment analysis🎭
![sentiment analysis](https://github.com/user-attachments/assets/fc06e833-5590-4fb4-b64c-db208d983505)


## 🧰 Tools & Technologies

🐍 Python  
🤖 Gemini AI (`gemini-2.5-flash`)  
🔊 ElevenLabs (Text-to-Speech)  
🎙️ OpenAI Whisper (Speech-to-Text)  
🎧 SpeechRecognition  
🗣️ PyAudio  
📢 playsound3   
🗃️ python-dotenv  
🛢️ PyMySQL  
🔥 Torch (PyTorch)  
🧠 Transformers

## Usage 🕹️``

* Clone repository
``
git clone https://github.com/HikmetCTK/Voice_Customer_support_Assistant.git
cd Voice_Customer_support_Assistant``

* Windows:Write in terminal
``
uv add
``
to  activate it 

* install requirements.txt
  ``uv add -r requirements.txt``

* Create .env file
``GOOGLE_API_KEY=your_google_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key``

*  Write this in terminal to run it
  ``python main.py``

## Future Plans

* Adding More Tools for special usecases e.g. 
selling promotional tariffs,After-sales support
* integrating with livekit
