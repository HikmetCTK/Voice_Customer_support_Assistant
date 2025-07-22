from logger_config import logger
import pymysql
from datetime import datetime
from sentiment_analysis import analyze_sentiment, categorize_sentiment
import uuid


def connect():
    """Veritabanı bağlantısı oluşturur"""
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password="password",
            database='customer_service'
        )
        logger.info("Veritabanı bağlantısı başarılı")
        return connection
    except pymysql.Error as e:
        logger.error(f"Veritabanı bağlantı hatası: {e}", exc_info=True)
        raise  # Hatayı yukarı iletmek için 


def update_meeting_date(date: str) -> str:  # mcp fonksiyon
    """
    Belirli bir müşteri ID'sine  ait toplantı tarihini günceller
    Args:
        datetime (str): Toplantı tarihi. Format: 'YYYY-MM-DD hh:mm:ss' şeklinde olmalıdır.


    Returns:
        Randevunun başarıyla ayarlandığına veya ayarlanamadığına dair mesaj gönderir
    """
    try:
        # Format kontrolü 
        datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

    except ValueError:
        logger.info(
            "Geçersiz tarih formatı! Lütfen 'YYYY-MM-DD HH:MM:SS' şeklinde girin.")
        return "Geçersiz tarih formatı! Lütfen 'YYYY-MM-DD HH:MM:SS' şeklinde girin"
    if date < datetime.now().strftime('%Y-%m-%d'):
        logger.info("Geçersiz tarih! Lütfen gelecekteki bir tarih girin.")
        return "Geçersiz tarih! Lütfen gelecekteki bir tarih girin"

    connection = connect()

    if connection is not None:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE customer SET meeting_date=%s WHERE customer_id=%s", (date, get_customer_id()))  # saat ve tarih ayarlama
                logger.info(f"Randevu güncellendi: {date}")
                cursor.execute(
                    "update meeting_dates set is_available = 1 , taken_by=%s where valid_date = %s", (get_customer_id(), date))

                connection.commit()  # Değişiklikleri kaydet
                logger.info(f"Randevu başarıyla {date} tarihine ayarlandı.")
        except Exception as e:
            logger.info(f"Randevu ayarlanamadı: {e}")

        finally:
            connection.close()
            logger.info("Veritabanı bağlantısı kapatıldı.")
        return f"Randevu başarıyla {date} tarihine ayarlandı "
    else:
        logger.info("Veritabanı bağlantısı kurulamadı, güncelleme yapılamadı.")
        return f"Randevu başarıyla {date} tarihine ayarlanamadı"


def get_customer_id():
    return 53  # Örnek olarak sabit bir müşteri ID'si döndürüyoruz arayan numaradan id çekme işlemi yapılabilir


# Varsayılan değer olarak get_customer_id() kullanılıyor
def customer_name(id: int = get_customer_id()):
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT first_name FROM customer WHERE customer_id =%s", (id,))
            result = cursor.fetchone()
            return result[0] if result else "Unknown Customer"
    finally:
        if connection is not None:
            connection.close()
            logger.info("Veritabanı bağlantısı kapatıldı.")


def topic_name(id: int = get_customer_id()):

    connection = connect()
    try:
        if connection is None:
            logger.info("Veritabanı bağlantısı kurulamadı.")
            return "Veritabanı bağlantısı kurulamadı"

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT topic FROM customer WHERE customer_id =%s", (id,))
            result = cursor.fetchone()
            return result[0] if result else "bir konu yok"

    finally:

        if connection is not None:
            connection.close()
            logger.info("Veritabanı bağlantısı kapatıldı.")


def get_available_slots():
    """
    Veritabanından uygun randevu tarihlerini alır.
    """
    connection = connect()
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "SELECT valid_date from meeting_dates where is_available = 0")
            result = cursor.fetchall()
            if not result:
                logger.info("Uygun tarih bulunamadı.")
                return ["Uygun tarih bulunamadı"]
            formatted_dates = [row[0].strftime(
                '%Y-%m-%d %H:%M:%S') if isinstance(row[0], datetime) else str(row[0]) for row in result]
            return formatted_dates
        except Exception as e:
            logger.error(
                f"Uygun tarihleri alırken hata oluştu: {e}", exc_info=True)
            return [" Uygun saatlere bakarken Hata oluştu, lütfen tekrar deneyin"]
        finally:
            if connection is not None:
                connection.close()
                logger.info("Veritabanı bağlantısı kapatıldı.")


def save_messages(messages: str, customer_id: int = get_customer_id())-> str:
    """Mesajları veritabanına kaydeder.
    Random konusma_id döndürür
    """
    connection = connect()
    konusma_id = str(uuid.uuid4())
    if connection is None:
        logger.error("Veritabanı bağlantısı kurulamadı.")
        return ""

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO customer_mssgs (c_id, chat,konusma_id) VALUES (%s, %s,%s)",
                (customer_id, messages, konusma_id)
            )
        connection.commit()
        logger.info("Mesajlar başarıyla kaydedildi.")
        
    except Exception as e:
        logger.error(f"Mesaj kaydı sırasında hata oluştu: {e}", exc_info=True)
        return ""
    finally:
        connection.close()
        logger.info("Veritabanı bağlantısı kapatıldı.")
        return konusma_id


def sentiment_insert(t_id: str, text: str, id: int = get_customer_id()):
    """
    Kullanıcı ile yapılan sohbetin duygu analizi veri tabanına kaydedilir
    """
    connection = connect()
    sentiment = categorize_sentiment(text=text)
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "update customer_mssgs set sentiment=%s where konusma_id=%s ", (sentiment, t_id))
            connection.commit()
            logger.info(f"Başarıyla duygu analizi veritabanına eklendi")

        except Exception as e:
            logger.info(f"Duygu veri tabanına işlenirken hata oluştu {e}")

        finally:
            connection.close()
            logger.info("Veritabanı bağlantısı kapatıldı.")
