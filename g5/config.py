import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def get_env_cleaned(var_name: str, default_value: str) -> str:
    value = os.getenv(var_name, default_value)
    if value:
        comment_start = value.find('#')
        if comment_start != -1:
            value = value[:comment_start]
        return value.strip()
    return default_value

# --- Performance Tuning ---
BATCH_SIZE = int(get_env_cleaned("BATCH_SIZE", "25"))
INITIAL_CONCURRENCY = int(get_env_cleaned("INITIAL_CONCURRENCY", "12"))
MAX_CONCURRENCY = int(get_env_cleaned("MAX_CONCURRENCY", "30"))
MIN_CONCURRENCY = int(get_env_cleaned("MIN_CONCURRENCY", "3"))
MAX_BATCH_SIZE = int(get_env_cleaned("MAX_BATCH_SIZE", "75"))
MIN_BATCH_SIZE = int(get_env_cleaned("MIN_BATCH_SIZE", "8"))

# --- Delays and Retries ---
MAX_RETRIES = int(get_env_cleaned("MAX_RETRIES", "2"))
RETRY_DELAY_MS = int(get_env_cleaned("RETRY_DELAY", "500"))
RETRY_DELAY = RETRY_DELAY_MS / 1000.0
PAUSE_INTERVAL_EMAILS = int(get_env_cleaned("PAUSE_INTERVAL_EMAILS", "0"))
PAUSE_DURATION_MS = int(get_env_cleaned("PAUSE_DURATION_MS", "0"))
PAUSE_DURATION_S = PAUSE_DURATION_MS / 1000.0

# --- Functionality & Validation ---
SMTP_TEST = get_env_cleaned("SMTP_TEST", "false").lower() == "true"
SKIP_DNS_FAILURES = get_env_cleaned("SKIP_DNS_FAILURES", "true").lower() == "true"
QUIET_MX_ERRORS = get_env_cleaned("QUIET_MX_ERRORS", "false").lower() == "true"
CHECK_MX_DURING_LOAD = get_env_cleaned("CHECK_MX_DURING_LOAD", "false").lower() == "true"
CHECK_MX_BEFORE_SEND = get_env_cleaned("CHECK_MX_BEFORE_SEND", "false").lower() == "true"
DISABLE_ALL_MX_VALIDATION = get_env_cleaned("DISABLE_ALL_MX_VALIDATION", "false").lower() == "true"
SKIP_SMTP_VERIFY = get_env_cleaned("SKIP_SMTP_VERIFY", "false").lower() == "true"
SMTP_REJECT_UNAUTHORIZED = get_env_cleaned("SMTP_REJECT_UNAUTHORIZED", "true").lower() != "false"

# --- Logging & Identification ---
LOG_LEVEL = get_env_cleaned("LOG_LEVEL", "INFO").upper()
CONSOLE_LOG_LEVEL = get_env_cleaned("CONSOLE_LOG_LEVEL", "INFO").upper()
FROM_NAME = get_env_cleaned("FROM_NAME", "Claro Br")
EMAIL_SUBJECT_TEMPLATE = get_env_cleaned("EMAIL_SUBJECT", "📩 18% OFF Pagando HOJE: Evite Bloqueio. Cod:{random:8}")

# --- File Paths ---
SMTP_CONFIG_PATH_STR = get_env_cleaned("SMTP_CONFIG_PATH", "smtp_servers.txt")
RECIPIENT_LIST_PATH_STR = get_env_cleaned("RECIPIENT_LIST_PATH", "recipients.txt")
MESSAGE_FILE_PATH_STR = get_env_cleaned("MESSAGE_FILE_PATH", "message.html")
ATTACHMENT_PATH_STR = get_env_cleaned("ATTACHMENT_PATH", "")
SUCCESS_FILE_PATH_STR = get_env_cleaned("SUCCESS_FILE_PATH", "sucesso.csv")
FAILED_FILE_PATH_STR = get_env_cleaned("FAILED_FILE_PATH", "falha.csv")

SMTP_CONFIG_PATH = Path(SMTP_CONFIG_PATH_STR)
RECIPIENT_LIST_PATH = Path(RECIPIENT_LIST_PATH_STR)
MESSAGE_FILE_PATH = Path(MESSAGE_FILE_PATH_STR)
ATTACHMENT_PATH = Path(ATTACHMENT_PATH_STR) if ATTACHMENT_PATH_STR else None
SUCCESS_FILE_PATH = Path(SUCCESS_FILE_PATH_STR)
FAILED_FILE_PATH = Path(FAILED_FILE_PATH_STR)