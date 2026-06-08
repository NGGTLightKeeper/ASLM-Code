# Copyright NGGT.LightKeeper. All Rights Reserved.

import logging
import threading

from django.apps import AppConfig

logger = logging.getLogger(__name__)


# Warm up ASLM-Chat in the background when ASLM-Code starts inside the host.
def _warmup_aslm_chat() -> None:
    try:
        from Services import aslm_chat_resolver

        base_url = aslm_chat_resolver.ensure_chat_running()
        logger.info("ASLM-Chat warmup succeeded: %s", base_url)
    except Exception as exc:
        logger.warning("ASLM-Chat warmup skipped: %s", exc)


# Configure the UI application.
class UiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Apps.UI"

    def ready(self) -> None:
        thread = threading.Thread(
            target=_warmup_aslm_chat,
            name="aslm-code-chat-warmup",
            daemon=True,
        )
        thread.start()
