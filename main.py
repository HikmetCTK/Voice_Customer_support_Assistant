import time

from datetime import datetime
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import uuid
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from playsound3 import playsound
from database_funcs import customer_name, topic_name,update_meeting_date,get_available_slots,save_messages,sentiment_insert
from prompts import  CUSTOMER_SUPPORT2, CS3
from speech2text import get_user_transcript
from logger_config import logger
from fastmcp import Client


load_dotenv()  # ortam değişkenleri (elevenlabs, gemini)


class CustomerServiceBot:
    def __init__(self):
        self.llm_model = "gemini-2.5-flash"
        self.gemini_client = None
        self.elevenlabs_client = None
        self.chat = None
        # CUSTOMER_SUPPORT2 veya CS3 kullanabilirsiniz
        self.customer_name = customer_name()
        self.load_models()

    def load_models(self):
        try:
            gemini_api_key = os.getenv("GOOGLE_API_KEY")
            if not gemini_api_key:
                logger.error("API_KEY ortam değişkeni bulunamadı.")
            else:
                self.gemini_client = genai.Client(api_key=gemini_api_key)
                print(self.gemini_client)
                logger.info("Gemini istemcisi hazır.")
        except Exception as e:
            logger.error(f"Gemini istemcisi başlatılamadı: {e}", exc_info=True)

        try:
            elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
            if not elevenlabs_api_key:
                logger.error("ELEVENLABS_API_KEY ortam değişkeni bulunamadı.")
            else:
                self.elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)
                logger.info("ElevenLabs istemcisi hazır.")
        except Exception as e:
            logger.error(
                f"ElevenLabs istemcisi başlatılamadı: {e}", exc_info=True)

        try:
            if not self.gemini_client:
                logger.error(
                    "Gemini istemcisi yüklenemedi, sohbet başlatılamıyor.")
            else:


                self.chat = self.gemini_client.chats.create(
                    model=self.llm_model,
                    config=types.GenerateContentConfig(
                        system_instruction=CS3.format(
                            customer_name=self.customer_name,
                            topic_name=topic_name,
                            #meeting_slots=get_available_slots(),
                            current_date=datetime.now().strftime("%Y-%m-%d")
                        ),
                        #thinking_config=types.ThinkingConfig(thinking_budget=0),
                        tools=[update_meeting_date, get_available_slots],
                        temperature=0),
                    history=[])

        except Exception as e:
            logger.error(f"Sohbet başlatılamadı: {e}", exc_info=True)

    def generate_filename(self, prefix="konusma", extension=".wav"):
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}{extension}"

    def get_llm_response(self, input_text):
        if not self.gemini_client:
            logger.error(
                "Gemini istemcisi mevcut değil, LLM yanıtı alınamıyor.")
            return "Üzgünüm, şu anda bağlanamıyorum. Lütfen daha sonra tekrar deneyin gemini client."

        if not self.chat:
            logger.error("Sohbet başlatılmadı, LLM yanıtı alınamıyor.")
            return "Üzgünüm, şu anda bağlanamıyorum. Lütfen daha sonra tekrar deneyin gemini chat."
        if not input_text or input_text.strip() == "":
            logger.warning(
                "Boş veya sadece boşluk karakterlerinden oluşan giriş alındı.")
            return "Lütfen geçerli bir metin girin."
        logger.info(f"LLM'e gönderilen metin: '{input_text}'")
        try:
            
            response = self.chat.send_message(input_text)
            llm_response_text = response.text
            logger.info(f"LLM'den alınan yanıt: '{llm_response_text}'")
            return llm_response_text

        except Exception as e:
            logger.error(
                f"LLM yanıtı alınırken hata oluştu: {e}", exc_info=True)
            return "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin."

    def text_to_speech_file(self, text: str) -> str:
        if not self.elevenlabs_client:
            logger.error("ElevenLabs istemcisi mevcut değil.")
            return "ElevenLabs istemcisi mevcut değil."

        if not text or text.strip() == "":
            logger.warning("Boş metin için ses üretilemez.")
            return "Boş metin için ses üretilemez."

        # İlk 50 karakteri logla
        logger.info(f"Metinden sese dönüştürülüyor: '{text[:50]}...'")
        try:
            response = self.elevenlabs_client.text_to_speech.convert(
                voice_id="xyqF3vGMQlPk3e7yA4DI",
                output_format="mp3_22050_32",
                text=text,
                model_id="eleven_turbo_v2_5",
                voice_settings=VoiceSettings(
                    stability=0,
                    similarity_boost=1.0,
                    style=0.7,
                    use_speaker_boost=True,
                    speed=1.1,
                ),
            )
            save_file_path = f"{uuid.uuid4()}.mp3"
            with open(save_file_path, "wb") as f:
                for chunk in response:
                    if chunk:
                        f.write(chunk)
            logger.info(f"Ses dosyası başarıyla kaydedildi: {save_file_path}")
            return save_file_path
        except Exception as e:
            logger.error(
                f"Ses üretimi sırasında hata oluştu: {e}", exc_info=True)
            return "Ses üretimi sırasında hata oluştu"

    def play_audio(self, file_path: str):
        if file_path and os.path.exists(file_path):
            try:
                logger.info(f"Ses çalınıyor: {file_path}")
                # playsound bloklu olduğu için, bu satır ses çalma bitene kadar bekler.
                playsound(file_path, block=True)

                try:
                    os.remove(file_path)  # Çalma sonrası dosyayı sil
                    logger.debug(f"Çalınan ses dosyası silindi: {file_path}")
                except OSError as e:
                    logger.warning(
                        f"Çalınan ses dosyası silinemedi: {file_path} - {e}")

                logger.info("Ses çalma tamamlandı.")
            except Exception as e:
                logger.error(f"Ses çalarken hata oluştu: {e}", exc_info=True)
        else:
            logger.warning(
                "Geçersiz dosya yolu veya dosya mevcut değil: %s", file_path)

    def start_chat(self):
        logger.info("Müşteri Hizmetleri Botu sohbeti başlatılıyor.")
        logger.info("Sohbeti sonlandırmak için 'Çıkış' diyebilirsiniz.")

        while True:
            user_input_text = get_user_transcript()

            if user_input_text is None:  # get_user_transcript hata verirse
                logger.error(
                    "get_user_transcript fonksiyonundan None döndü. Ses işleme başarısız.")

                # Kullanıcıya bir şans daha vermek için kısa bir bekleme
                time.sleep(2)
                continue

            if not user_input_text.strip():  # Boş giriş veya sessizlik
                logger.info(
                    "Kullanıcıdan sessiz giriş alındı veya boşluk karakterleri girildi.")
                continue

            if user_input_text.lower() == "görüşürüz":  # Deneme  amacıyla çıkış komutu kullanıldı
                logger.info(
                    "Kullanıcı 'Görüşürüz' komutunu girdi. Sohbet sonlandırılıyor.")
                print("Görüşmek üzere! Hoşça kalın.")
                break

            logger.info(f"Kullanıcı Girişi: '{user_input_text}'")

            llm_response = self.get_llm_response(user_input_text)

            if llm_response is None or "hata oluştu" in llm_response.lower():
                logger.error(
                    f"LLM'den geçersiz yanıt alındı: '{llm_response}'")
                llm_response = "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin."
                continue
            logger.info(f"Kullanıcıdan alınan metin: '{user_input_text}'")
            logger.info(f"LLM Yanıtı: '{llm_response}'")

            audio_path = self.text_to_speech_file(llm_response)
            if audio_path:  # Ses dosyasını çal
                self.play_audio(audio_path)
            else:
                logger.warning("Ses dosyası üretilemedi, seslendirme atlandı.")

        logger.info("Sohbet döngüsü tamamlandı.")
        chat_history = []
        if self.chat is not None:  # Eğer chat oturumu varsa
            for message in self.chat.get_history():
                part = message.parts[0] if message.parts and message.parts[0] is not None else None
                # None olan mesajları atla
                if not part or not hasattr(part, "text") or part.text is None:
                    logger.debug(f"Geçersiz mesaj atlandı - role: {message.role}")
                    continue
                text = part.text if part and hasattr(part, "text") else ""
                chat_history.append({
                    "role": message.role,
                    "text": text if text else "No text provided"
                })

                logger.info(f'role - {message.role}: {text}')
            # Sohbet geçmişini veritabanına kaydet

            valid_text=[msg["text"] for msg in chat_history]
            if valid_text:
                text=" \n ".join(valid_text)
                konusma_id=save_messages(text)
                print(f"Chat history text: {text}")
                sentiment_insert(text=text,t_id=konusma_id) # duyguyu veri tabanına kaydet
            else:
                logger.warning("Sohbet geçmişi boş, mesaj kaydedilemedi.")


        else:
            logger.warning("Sohbet oturumu mevcut değil, geçmiş alınamadı.")


if __name__ == "__main__":
    bot = CustomerServiceBot()
    bot.start_chat()
