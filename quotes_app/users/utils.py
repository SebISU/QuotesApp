from flask import url_for
from quotes_app import mail
from flask_mail import Message


def send_reset_token(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
    sender='noreply@sagesay.com', recipients=[user.email])
    msg.body = f'''To reset your password visit the following link:
{url_for('users.reset_password', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)
