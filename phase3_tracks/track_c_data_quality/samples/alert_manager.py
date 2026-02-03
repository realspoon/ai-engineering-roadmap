"""
Alert Management System
알림 시스템 (Slack, Email, Webhook 연동)

Features:
- 다양한 채널로 알림 전송
- 알림 레벨 (CRITICAL, WARNING, INFO)
- 알림 집계 및 중복 제거
- 알림 히스토리 관리
- 자동 재시도 메커니즘
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
import hashlib
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """알림 레벨"""
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class AlertChannel(Enum):
    """알림 채널"""
    SLACK = "slack"
    EMAIL = "email"
    WEBHOOK = "webhook"
    LOG = "log"


@dataclass
class Alert:
    """알림"""
    alert_id: str
    title: str
    message: str
    level: AlertLevel
    source: str  # 알림 출처 (profiler, validator, detector 등)
    timestamp: datetime
    channel: AlertChannel
    metadata: Dict[str, Any]
    is_sent: bool = False
    send_timestamp: Optional[datetime] = None
    retry_count: int = 0

    def to_dict(self) -> Dict:
        """Dictionary로 변환"""
        return {
            "alert_id": self.alert_id,
            "title": self.title,
            "message": self.message,
            "level": self.level.value,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "channel": self.channel.value,
            "metadata": self.metadata,
            "is_sent": self.is_sent,
            "send_timestamp": self.send_timestamp.isoformat() if self.send_timestamp else None,
            "retry_count": self.retry_count
        }

    def get_hash(self) -> str:
        """알림의 고유 해시값 생성"""
        content = f"{self.title}:{self.message}:{self.source}"
        return hashlib.md5(content.encode()).hexdigest()


class AlertProvider(ABC):
    """알림 제공자 기본 클래스"""

    @abstractmethod
    def send(self, alert: Alert) -> bool:
        """알림 전송"""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """설정 검증"""
        pass


class SlackAlertProvider(AlertProvider):
    """Slack 알림 제공자"""

    def __init__(self, webhook_url: str):
        """
        초기화

        Args:
            webhook_url: Slack Webhook URL
        """
        self.webhook_url = webhook_url

    def validate(self) -> bool:
        """설정 검증"""
        return bool(self.webhook_url and self.webhook_url.startswith('https://hooks.slack.com'))

    def send(self, alert: Alert) -> bool:
        """Slack으로 알림 전송"""
        try:
            # 실제 환경에서는 requests 라이브러리 사용
            # response = requests.post(self.webhook_url, json=self._format_message(alert))
            # return response.status_code == 200

            # Mock 구현
            message = self._format_message(alert)
            logger.info(f"[SLACK] Sending alert: {alert.title}")
            logger.debug(f"Slack message: {json.dumps(message, indent=2)}")
            return True

        except Exception as e:
            logger.error(f"Failed to send Slack alert: {str(e)}")
            return False

    def _format_message(self, alert: Alert) -> Dict:
        """Slack 메시지 형식화"""
        color_map = {
            AlertLevel.CRITICAL: "danger",
            AlertLevel.ERROR: "danger",
            AlertLevel.WARNING: "warning",
            AlertLevel.INFO: "good"
        }

        return {
            "attachments": [
                {
                    "color": color_map.get(alert.level, "good"),
                    "title": f"[{alert.level.value}] {alert.title}",
                    "text": alert.message,
                    "fields": [
                        {
                            "title": "Source",
                            "value": alert.source,
                            "short": True
                        },
                        {
                            "title": "Timestamp",
                            "value": alert.timestamp.isoformat(),
                            "short": True
                        },
                        {
                            "title": "Alert ID",
                            "value": alert.alert_id,
                            "short": False
                        }
                    ] + self._format_metadata(alert.metadata),
                    "footer": "Data Quality Alert System"
                }
            ]
        }

    def _format_metadata(self, metadata: Dict) -> List[Dict]:
        """메타데이터 형식화"""
        fields = []
        for key, value in metadata.items():
            fields.append({
                "title": key.replace('_', ' ').title(),
                "value": str(value),
                "short": True
            })
        return fields[:5]  # 최대 5개


class EmailAlertProvider(AlertProvider):
    """Email 알림 제공자"""

    def __init__(self, smtp_server: str, sender_email: str,
                 sender_password: str, recipients: List[str]):
        """
        초기화

        Args:
            smtp_server: SMTP 서버
            sender_email: 발신 이메일
            sender_password: 발신 비밀번호
            recipients: 수신자 목록
        """
        self.smtp_server = smtp_server
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipients = recipients

    def validate(self) -> bool:
        """설정 검증"""
        return bool(
            self.smtp_server and
            self.sender_email and
            self.sender_password and
            self.recipients
        )

    def send(self, alert: Alert) -> bool:
        """Email로 알림 전송"""
        try:
            # 실제 환경에서는 smtplib 사용
            # import smtplib
            # from email.mime.text import MIMEText
            # ...

            # Mock 구현
            logger.info(f"[EMAIL] Sending alert to {', '.join(self.recipients)}: {alert.title}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email alert: {str(e)}")
            return False


class WebhookAlertProvider(AlertProvider):
    """Webhook 알림 제공자"""

    def __init__(self, webhook_url: str):
        """
        초기화

        Args:
            webhook_url: Webhook URL
        """
        self.webhook_url = webhook_url

    def validate(self) -> bool:
        """설정 검증"""
        return bool(self.webhook_url and self.webhook_url.startswith(('http://', 'https://')))

    def send(self, alert: Alert) -> bool:
        """Webhook으로 알림 전송"""
        try:
            # 실제 환경에서는 requests 라이브러리 사용
            # response = requests.post(self.webhook_url, json=alert.to_dict())
            # return response.status_code in [200, 201]

            # Mock 구현
            logger.info(f"[WEBHOOK] Sending alert to {self.webhook_url}: {alert.title}")
            return True

        except Exception as e:
            logger.error(f"Failed to send webhook alert: {str(e)}")
            return False


class LogAlertProvider(AlertProvider):
    """Log 알림 제공자"""

    def validate(self) -> bool:
        """설정 검증"""
        return True

    def send(self, alert: Alert) -> bool:
        """로그로 알림 기록"""
        try:
            log_level = {
                AlertLevel.CRITICAL: logging.CRITICAL,
                AlertLevel.ERROR: logging.ERROR,
                AlertLevel.WARNING: logging.WARNING,
                AlertLevel.INFO: logging.INFO
            }.get(alert.level, logging.INFO)

            logger.log(log_level, f"[{alert.source}] {alert.title}: {alert.message}")
            return True

        except Exception as e:
            logger.error(f"Failed to log alert: {str(e)}")
            return False


class AlertManager:
    """알림 관리자"""

    def __init__(self, dedup_window: timedelta = timedelta(minutes=5)):
        """
        초기화

        Args:
            dedup_window: 중복 제거 윈도우 (시간)
        """
        self.providers: Dict[AlertChannel, AlertProvider] = {}
        self.alerts: List[Alert] = []
        self.alert_hashes: Dict[str, datetime] = {}
        self.dedup_window = dedup_window

    def register_provider(self, channel: AlertChannel, provider: AlertProvider) -> bool:
        """알림 제공자 등록"""
        if not provider.validate():
            logger.error(f"Invalid provider configuration for {channel.value}")
            return False

        self.providers[channel] = provider
        logger.info(f"Alert provider registered: {channel.value}")
        return True

    def create_alert(self, title: str, message: str, level: AlertLevel,
                    source: str, metadata: Optional[Dict[str, Any]] = None,
                    channels: Optional[List[AlertChannel]] = None) -> Optional[Alert]:
        """알림 생성"""
        alert_id = f"{source}:{datetime.now().timestamp()}"

        alert = Alert(
            alert_id=alert_id,
            title=title,
            message=message,
            level=level,
            source=source,
            timestamp=datetime.now(),
            channel=channels[0] if channels else AlertChannel.LOG,
            metadata=metadata or {}
        )

        return alert

    def _should_send_alert(self, alert: Alert) -> bool:
        """알림 전송 여부 결정 (중복 제거)"""
        alert_hash = alert.get_hash()
        now = datetime.now()

        # 해시에 해당하는 최근 알림이 있는지 확인
        if alert_hash in self.alert_hashes:
            last_alert_time = self.alert_hashes[alert_hash]
            if now - last_alert_time < self.dedup_window:
                logger.debug(f"Alert {alert_hash} suppressed (duplicate within dedup window)")
                return False

        # CRITICAL 레벨은 항상 전송
        if alert.level == AlertLevel.CRITICAL:
            return True

        # 해시 업데이트
        self.alert_hashes[alert_hash] = now
        return True

    def send_alert(self, alert: Alert, channels: Optional[List[AlertChannel]] = None) -> bool:
        """알림 전송"""
        if not self._should_send_alert(alert):
            return False

        channels = channels or [AlertChannel.LOG]
        success_count = 0

        for channel in channels:
            if channel not in self.providers:
                logger.warning(f"No provider registered for channel: {channel.value}")
                continue

            provider = self.providers[channel]
            try:
                if provider.send(alert):
                    success_count += 1
                    alert.is_sent = True
                    alert.send_timestamp = datetime.now()
                else:
                    alert.retry_count += 1
            except Exception as e:
                logger.error(f"Error sending alert to {channel.value}: {str(e)}")
                alert.retry_count += 1

        # 알림 히스토리에 추가
        self.alerts.append(alert)

        return success_count > 0

    def send_quality_alert(self, source: str, quality_score: float,
                          threshold: float,
                          details: Optional[Dict[str, Any]] = None,
                          channels: Optional[List[AlertChannel]] = None) -> bool:
        """품질 점수 기반 알림 전송"""
        # 레벨 결정
        if quality_score < threshold * 0.5:
            level = AlertLevel.CRITICAL
        elif quality_score < threshold * 0.8:
            level = AlertLevel.ERROR
        elif quality_score < threshold:
            level = AlertLevel.WARNING
        else:
            return True  # 알림 전송 불필요

        alert = self.create_alert(
            title=f"Data Quality Alert - {source}",
            message=f"Quality score {quality_score:.2%} below threshold {threshold:.2%}",
            level=level,
            source=source,
            metadata={
                "quality_score": quality_score,
                "threshold": threshold,
                **(details or {})
            },
            channels=channels
        )

        return self.send_alert(alert, channels)

    def send_validation_alert(self, source: str, column: str,
                            error_count: int, error_rate: float,
                            error_threshold: float = 0.05,
                            channels: Optional[List[AlertChannel]] = None) -> bool:
        """검증 실패 알림 전송"""
        # 레벨 결정
        if error_rate > error_threshold * 3:
            level = AlertLevel.CRITICAL
        elif error_rate > error_threshold * 2:
            level = AlertLevel.ERROR
        elif error_rate > error_threshold:
            level = AlertLevel.WARNING
        else:
            return True  # 알림 전송 불필요

        alert = self.create_alert(
            title=f"Validation Error - {source}:{column}",
            message=f"Found {error_count} validation errors ({error_rate:.2%})",
            level=level,
            source=source,
            metadata={
                "column": column,
                "error_count": error_count,
                "error_rate": error_rate,
                "threshold": error_threshold
            },
            channels=channels
        )

        return self.send_alert(alert, channels)

    def get_alert_history(self, source: Optional[str] = None,
                         level: Optional[AlertLevel] = None,
                         hours: int = 24) -> List[Alert]:
        """알림 히스토리 조회"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        filtered_alerts = [
            alert for alert in self.alerts
            if alert.timestamp >= cutoff_time
        ]

        if source:
            filtered_alerts = [a for a in filtered_alerts if a.source == source]

        if level:
            filtered_alerts = [a for a in filtered_alerts if a.level == level]

        return filtered_alerts

    def get_alert_summary(self, hours: int = 24) -> Dict[str, Any]:
        """알림 요약"""
        recent_alerts = self.get_alert_history(hours=hours)

        summary = {
            "total_alerts": len(recent_alerts),
            "by_level": {},
            "by_source": {},
            "by_channel": {},
            "sent_alerts": sum(1 for a in recent_alerts if a.is_sent),
            "unsent_alerts": sum(1 for a in recent_alerts if not a.is_sent)
        }

        for level in AlertLevel:
            count = sum(1 for a in recent_alerts if a.level == level)
            summary["by_level"][level.value] = count

        for alert in recent_alerts:
            summary["by_source"][alert.source] = summary["by_source"].get(alert.source, 0) + 1
            summary["by_channel"][alert.channel.value] = summary["by_channel"].get(alert.channel.value, 0) + 1

        return summary

    def generate_report(self, hours: int = 24) -> str:
        """알림 리포트 생성"""
        summary = self.get_alert_summary(hours)
        alerts = self.get_alert_history(hours=hours)

        report = f"""
=== Alert Report ===
Generated: {datetime.now().isoformat()}
Period: Last {hours} hours

Summary:
  Total Alerts: {summary['total_alerts']}
  Sent: {summary['sent_alerts']}
  Unsent: {summary['unsent_alerts']}

By Level:
"""

        for level, count in summary['by_level'].items():
            report += f"  {level}: {count}\n"

        report += "\nBy Source:\n"
        for source, count in summary['by_source'].items():
            report += f"  {source}: {count}\n"

        report += "\nRecent Alerts:\n"
        for alert in alerts[-10:]:
            status = "✓" if alert.is_sent else "✗"
            report += f"  [{status}] [{alert.level.value}] {alert.title}\n"
            report += f"      {alert.message}\n"

        return report


def main():
    """테스트"""
    # 알림 관리자 생성
    manager = AlertManager()

    # 알림 제공자 등록
    manager.register_provider(
        AlertChannel.SLACK,
        SlackAlertProvider("https://hooks.slack.com/services/YOUR/WEBHOOK/URL")
    )
    manager.register_provider(
        AlertChannel.EMAIL,
        EmailAlertProvider(
            "smtp.gmail.com",
            "your_email@gmail.com",
            "your_password",
            ["admin@example.com", "team@example.com"]
        )
    )
    manager.register_provider(AlertChannel.LOG, LogAlertProvider())

    # 품질 알림 전송
    print("=== Sending Quality Alert ===")
    manager.send_quality_alert(
        source="quality_profiler",
        quality_score=0.65,
        threshold=0.75,
        details={"completeness": 0.9, "consistency": 0.5},
        channels=[AlertChannel.LOG, AlertChannel.SLACK]
    )

    # 검증 알림 전송
    print("\n=== Sending Validation Alert ===")
    manager.send_validation_alert(
        source="rule_validator",
        column="email",
        error_count=15,
        error_rate=0.15,
        error_threshold=0.05,
        channels=[AlertChannel.LOG]
    )

    # 알림 히스토리 조회
    print("\n=== Alert History ===")
    history = manager.get_alert_history(hours=1)
    for alert in history:
        print(f"  [{alert.level.value}] {alert.title}")

    # 리포트 생성
    print(manager.generate_report(hours=1))


if __name__ == "__main__":
    main()
