"""Check message status - last 10 WhatsApp messages"""
import sys
import os
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()
from twilio.rest import Client

client = Client(os.environ.get('TWILIO_ACCOUNT_SID'), os.environ.get('TWILIO_AUTH_TOKEN'))

status_ar = {'queued': 'في الانتظار', 'sending': 'جاري الإرسال', 'sent': 'تم الإرسال', 
             'delivered': 'تم التوصيل', 'read': 'تم القراءة', 'failed': 'فشل', 
             'undelivered': 'لم يُسلّم'}

messages = client.messages.list(limit=10, to='whatsapp:+966568112166')
print('='*55)
print('آخر 10 رسائل إلى 0568112166')
print('='*55)
for m in messages:
    st = status_ar.get(m.status, m.status)
    err = f' | Error: {m.error_code}' if m.error_code else ''
    print(f'{m.sid} | {st}{err} | {m.date_created}')
print('='*55)
