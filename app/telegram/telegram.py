from flask import current_app
from threading import Thread
from .. import db
import requests

def send_async_message(botToken, chatId, text):
    params = {'chat_id': chatId, 'text': text}
    response = requests.post('https://api.telegram.org/bot' + botToken + '/sendMessage', \
               data = params)
    print(response, 'https://api.telegram.org/bot' + botToken + '/sendMessage', text)

def generateDebtString(debt):
    return 'Id: {}\nFrom: {} on {}\nValue: {}\nDescription: {}' \
            .format(debt.id, debt.give.username, debt.debt_since.strftime('%d.%m.%y'), debt.total, debt.about)
    

def send_message(to, debt, text):
    if not to.isTelegram:
        return

    app = current_app._get_current_object()
    text = text + '\n' + generateDebtString(debt)
    
    thr = Thread(target=send_async_message, args=[app.config['TELEGRAM_BOT_TOKEN'], to.telegramChatId, text])
    thr.start()
    return thr