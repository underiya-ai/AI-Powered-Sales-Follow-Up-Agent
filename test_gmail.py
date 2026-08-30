from backend.service.gmail_service import send_email


result = send_email(
    to_email="aniketunderiya20@gmail.com",
    subject="FollowAI Gmail Test",
    body="Hello! This is a test email sent automatically by FollowAI."
)

print("Email sent successfully!")
print(result)