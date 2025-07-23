import speech_recognition as sr
import logging
import audioop,wave
import pyaudio
from logger_config import logger


def get_user_transcript():   
    """
    Mikrofondan sesli giriş alınır ve metne dönüştürülür.
    """
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 1.0  # Dinleme sırasında sessizlik süresi
    with sr.Microphone() as source:
        #recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Ortam gürültüsünü algıla

        logger.info("Dinleniyor...")
        audio = recognizer.listen(source,timeout=5,phrase_time_limit=30)  # Sessizlik 5  saniye  olursa otomatik durur kullanıcıdan ses aldıktan sonra maks 30 saniye dinler.

        logger.info("Tanımlanıyor...")
        try:
            text = recognizer.recognize_google(audio, language="tr-TR")
            logger.info(f"Müşteri: {text}")
            return text 
        except sr.WaitTimeoutError:
            logger.info("Maksimum Bekleme süresi doldu, lütfen tekrar deneyin.")
            return "Maksimum Bekleme süresi doldu, lütfen tekrar deneyin."
        except sr.UnknownValueError:
            logger.info("Ne söylediğinizi anlayamadım.")
            return "Ne söylediğinizi anlayamadım."
        except sr.RequestError as e:
            logger.info(f"Request hatası: {e}")
            return f"Request hatası: {e}"
        


def get_user_transcript_and_save(self,   # hem transkripti alıyor hem videoya kaydediyor.
                            threshold=100,
                            silence_limit=1,
                            rate=16000,
                            chunk=1024,
                            channels=1):
        
        
        """Mikrofondan sesli giriş alınır ve metne dönüştürülür ve Wav olarak kaydedilir."""


        if not self.whisper_model:
            logger.error("Hata: Whisper modeli mevcut değil.")
            return None

        logger.info("Dinleniyor... Konuşun ve sonra susun.")
        frames = []
        silent_chunks = 0
        is_speaking = False
        filename = self.generate_filename()

        p = pyaudio.PyAudio()
        stream = None # stream'i finally bloğunda kontrol edebilmek için none
        try:
            stream = p.open(format=pyaudio.paInt16,
                            channels=channels,
                            rate=rate,
                            input=True,
                            frames_per_buffer=chunk)

            while True:
                data = stream.read(chunk, exception_on_overflow=False)
                rms = audioop.rms(data, 2)

                if rms > threshold:
                    frames.append(data)
                    silent_chunks = 0
                    is_speaking = True
                else:
                    if is_speaking:
                        silent_chunks += 1
                        frames.append(data)
                        # Burada oluşan silent_chunks sayısını loglayıp incelenebilir daha iyi parametre ayarları için.
                        # logger.debug(f"Silent chunks: {silent_chunks}, Threshold chunks: {rate / chunk * silence_limit}")
                        if silent_chunks > (rate / chunk * silence_limit):
                            logger.info("Konuşma bitti, işleniyor...")
                            break
        except Exception as e:
            logger.error(f"Ses kaydı sırasında hata oluştu: {e}", exc_info=True)
            return None 
        finally: # stream'i her durumda kapatmak için finally kullanıldı.
            if stream:
                stream.stop_stream()
                stream.close()
            p.terminate()

        if not frames: # Eğer hiç konuşma kaydedilmediyse
            logger.warning("Kayıt sırasında hiç ses verisi alınamadı.")
            return ""

        try:
            wf = wave.open(filename, 'wb')
            wf.setnchannels(channels)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
            wf.setframerate(rate)
            wf.writeframes(b''.join(frames))
            wf.close()
        except Exception as e:
            logger.error(f"Ses dosyası yazılırken hata oluştu: {e}", exc_info=True)
            return None

        logger.info("Whisper ile yazıya dökülüyor...")
        try:
            result = self.whisper_model.transcribe(filename, language="tr")
            # os.remove(filename) # Kaydedilen geçici dosyayı sil
            try:
                #os.remove(filename)
                logger.debug(f"Geçici ses dosyası silindi: {filename}")
            except OSError as e:
                logger.warning(f"Geçici ses dosyası silinemedi: {filename} - {e}")
            
            if result and "text" in result:
                logger.info(f"Transkripsiyon sonucu: {result['text']}")
                return result["text"]
            else:
                logger.warning("Transkripsiyon başarılı ancak metin alınamadı.")
                return ""
        except Exception as e:
            logger.error(f"Whisper transkripsiyonu sırasında hata oluştu: {e}", exc_info=True)
            return None
