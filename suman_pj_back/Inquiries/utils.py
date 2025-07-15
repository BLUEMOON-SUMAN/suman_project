# inquiries/utils.py (이 파일이 없으면 생성하고, 있다면 내용 확인)
from django.core.mail import send_mail
from django.conf import settings

def send_Inquiry_notification_email(Inquiry): # <--- 이 함수 이름 스펠링 확인!
    subject = f"[문의 접수] 새로운 문의가 도착했습니다: {Inquiry.name}"
    plain_message = (
        f"새로운 문의가 접수되었습니다.\n\n"
        f"이름: {Inquiry.name}\n"
        f"소속: {Inquiry.affiliation if Inquiry.affiliation else '없음'}\n"
        f"연락처: {Inquiry.phone if Inquiry.phone else '없음'}\n"
        f"이메일: {Inquiry.email}\n"
        f"문의 내용:\n{Inquiry.content}\n\n"
        f"관리자 페이지에서 확인해주세요: http://localhost:8000/admin/Inquiries/Inquiry/{Inquiry.id}/change/"
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [settings.ADMIN_EMAIL]

    try:
        send_mail(
            subject,
            plain_message,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        print(f"문의 알림 이메일이 {Inquiry.email}로부터 {settings.ADMIN_EMAIL}로 전송되었습니다.")
    except Exception as e:
        print(f"문의 알림 이메일 전송 실패: {e}")