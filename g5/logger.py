import logging
from rich.logging import RichHandler
from rich.console import Console
from .config import *
from .logger import logger, console

console = Console()
logger = logging.getLogger("bulk_sender")

class MxErrorFilter(logging.Filter):
    def filter(self, record):
        is_mx_error = 'MX Record Error' in record.getMessage() or 'MX Check Failed' in record.getMessage()
        # Você pode importar QUIET_MX_ERRORS do config se quiser
        return not (getattr(record, 'QUIET_MX_ERRORS', False) and record.levelno == logging.WARNING and is_mx_error)

rich_handler = RichHandler(
    console=console,
    show_time=True,
    show_level=True,
    show_path=False,
    markup=True,
    log_time_format="[%Y-%m-%d %H:%M:%S]",
)
rich_handler.addFilter(MxErrorFilter())
logger.addHandler(rich_handler)