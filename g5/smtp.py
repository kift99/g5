from typing import List, Dict, Any
from pathlib import Path
import time
import random
import sys
import math

import aiofiles
from email_validator import validate_email, EmailNotValidError

from .logger import logger

SmtpConfig = Dict[str, Any]
failed_smtp_servers: Dict[str, Dict[str, Any]] = {}

async def load_smtp_servers(file_path: Path) -> List[SmtpConfig]:
    """
    Loads SMTP server configurations from a file (host|email|password).
    Defaults to port 587 and STARTTLS.
    """
    logger.info(f"Loading SMTP configurations from: {file_path} (Format: host|email|password)")
    configs: List[SmtpConfig] = []
    try:
        async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
            line_num = 0
            async for line in f:
                line_num += 1
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = [p.strip() for p in line.split('|')]
                if len(parts) != 3:
                    logger.warning(f"Skipping invalid SMTP line {line_num}: Expected 3 parts, found {len(parts)}. Line: '{line}'")
                    continue
                host, email, password = parts[0], parts[1], parts[2]
                if not host or not email or not password:
                    logger.warning(f"Skipping invalid SMTP line {line_num}: Host, email, or password missing.")
                    continue
                try:
                    validate_email(email, check_deliverability=False)
                except EmailNotValidError as val_err:
                    logger.warning(f"Skipping invalid SMTP line {line_num}: Invalid email format '{email}': {val_err}")
                    continue
                configs.append({
                    "host": host, "port": 587, "email": email, "password": password,
                    "use_tls": False, "start_tls": True
                })
        logger.info(f"Loaded {len(configs)} valid SMTP configurations.")
        if not configs:
            logger.critical('No valid SMTP configurations found. Cannot proceed.')
            sys.exit(1)
        return configs
    except FileNotFoundError:
        logger.critical(f"SMTP configuration file not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Failed to load SMTP configurations: {e}", exc_info=True)
        sys.exit(1)

def get_next_smtp_config(smtp_servers: List[SmtpConfig]) -> SmtpConfig:
    """Selects the next available SMTP server randomly, respecting temporary failures."""
    now = time.monotonic()
    available_servers = []
    unavailable_details = {}

    for config in smtp_servers:
        email = config['email']
        if email in failed_smtp_servers:
            failure_info = failed_smtp_servers[email]
            if now < failure_info['retry_time']:
                unavailable_details[email] = failure_info['reason']
                continue
            else:
                logger.info(f"SMTP {email} is now available for retry (was failing due to: {failure_info['reason']}).")
                del failed_smtp_servers[email]
                available_servers.append(config)
        else:
            available_servers.append(config)

    unavailable_count = len(unavailable_details)
    if unavailable_count > 0 and (unavailable_count == len(smtp_servers) or random.random() < 0.1):
        logger.debug(f"{unavailable_count}/{len(smtp_servers)} SMTP server(s) are currently marked as unavailable.")

    if not available_servers:
        logger.error('All SMTP servers are currently marked as unavailable.')
        if not smtp_servers:
            raise RuntimeError('No SMTP servers loaded.')
        else:
            next_retry_time = min((info['retry_time'] for info in failed_smtp_servers.values()), default=float('inf'))
            wait_seconds = max(0, next_retry_time - now) if next_retry_time != float('inf') else float('inf')
            wait_minutes_str = f"{math.ceil(wait_seconds / 60)}" if wait_seconds != float('inf') else 'Indefinitely'
            raise RuntimeError(f"All {len(smtp_servers)} SMTP servers are currently unavailable. Next potential retry in ~{wait_minutes_str} minutes.")

    return random.choice(available_servers)