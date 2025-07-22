import logging

logging.basicConfig(
    level=logging.INFO,  # INFO seviyesinden itibaren her şeyi göster
    format="'%(asctime)s - %(name)s - %(levelname)s -  [%(filename)s:%(lineno)d] -%(message)s'",
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),  # Log dosyasına yaz
        logging.StreamHandler()                            # Konsola da yaz
    ]
)



logger = logging.getLogger(__name__)
