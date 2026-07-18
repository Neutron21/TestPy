import logging
from unittest import TestCase
from unittest.mock import patch

from app.routers.tareas import syncAllDashboard
from app.utils import logger_config


class LoggerAlertsTests(TestCase):
    def test_critical_log_triggers_alert_email(self):
        handler = logger_config.BrevoAlertHandler()

        with patch("app.utils.email.enviar_correo_alerta") as mock_send:
            record = logging.LogRecord(
                name="konnect_api.test",
                level=logging.CRITICAL,
                pathname=__file__,
                lineno=1,
                msg="fallo crítico de prueba",
                args=(),
                exc_info=None,
            )
            handler.emit(record)

        mock_send.assert_called_once()

    def test_sync_dashboard_logs_critical_on_failure(self):
        with patch("app.routers.tareas.sync_brokers", side_effect=RuntimeError("boom")), patch(
            "app.routers.tareas.logger.critical"
        ) as mock_critical:
            with self.assertRaises(RuntimeError):
                syncAllDashboard(None)

        mock_critical.assert_called_once()
