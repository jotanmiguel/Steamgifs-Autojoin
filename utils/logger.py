# utils/logger.py
import logging

log = logging.getLogger("SG-Autojoin")  # instância global

class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[36m",   # Cyan
        "INFO": "\033[32m",    # Green
        "WARNING": "\033[33m", # Yellow
        "ERROR": "\033[31m",   # Red
        "CRITICAL": "\033[41m" # Red background
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        msg = super().format(record)
        return f"{color}{msg}{self.RESET}"

def setup_logger(level=logging.INFO):
    """Configura o logger global apenas uma vez"""
    if log.handlers:  # Evita duplicar handlers
        return log

    log.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    fmt = ColorFormatter("[%(asctime)s] [%(levelname)s] %(message)s", "%H:%M:%S")
    ch.setFormatter(fmt)
    log.addHandler(ch)

    return log
