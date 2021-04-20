from flask_mail import Message
from flask import current_app, render_template
from .. import mail
from threading import Thread

def send_async_mail(app, message):
    with app.app_context():
        mail.send(message)

    
def send_mail(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    message = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[to])
    message.body = render_template(template + '.txt', **kwargs)
    message.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_mail, args=[app, message])
    thr.start()
    return thr

#db.session.delete(User.query.first())
#db.session.commit()