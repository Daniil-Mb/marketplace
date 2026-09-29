from src.core.celery_app import celery_app
from src.core.email.utils import send_email


@celery_app.task(
    name="auth.send_welcome_email",
)
def send_welcome_email(
    email: str,
) -> None:
    send_email(
        recipient=email,
        subject="Welcome to Marketplace",
        body=("Здравствуйте!\n\nВы успешно зарегистрировались в Marketplace."),
    )
