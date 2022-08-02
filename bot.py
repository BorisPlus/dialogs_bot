from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    Updater
)

access_list = {
    0,  # ID of Telegram User
}

TOKEN = '0123456789:987654321654987654321'


class BotResponse:
    text = ''

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return str(self.text)


def get_numeric_var(var_request):
    var_response = yield var_request
    while True:
        var_text = var_response.message.text
        if var_text and var_text.isnumeric():
            break
        var_response = yield f'Some thing wrong. {var_request}'
    return int(var_text)


# addition = x1 + x2 + x3
def addition_dialogue(chat_id):
    _ = yield 'X1 + X2 + X3 = Result'
    x1 = yield from get_numeric_var(f'Enter X1:')
    x2 = yield from get_numeric_var(f'Enter X2:')
    x3 = yield from get_numeric_var(f'Enter X3:')
    yield BotResponse(text=str(x1 + x2 + x3))


# subtraction = y1 - y2
def subtraction_dialogue(chat_id):
    _ = yield 'Y1 - Y2 = Result'
    y1 = yield from get_numeric_var(f'Enter Y1:')
    y2 = yield from get_numeric_var(f'Enter Y2:')
    yield BotResponse(text=str(y1 - y2))


class DialogueBot(object):

    def access_list_check(deorate_me):
        def decorator(self, update, *args, **kwargs):
            chat_id = update.message.chat_id
            if chat_id not in access_list:
                self._send_response(update, chat_id, BotResponse(text='Access denied.'))
                return
            deorate_me(self, update, *args, **kwargs)

        return decorator

    def __init__(self, token):
        self.updater = Updater(token=token)
        self.updater.dispatcher.add_handler(CommandHandler('addition', self.addition_handler))
        self.updater.dispatcher.add_handler(CommandHandler('subtraction', self.subtraction_handler))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.request_handler))
        self.handlers = dict()

    def start(self):
        self.updater.start_polling()

    @access_list_check
    def addition_handler(self, update, *args, **kwargs):
        chat_id = update.message.chat_id
        self.handlers[chat_id] = addition_dialogue(chat_id)
        self._send_response(update, chat_id, next(self.handlers[chat_id]))
        self._send_response(update, chat_id, next(self.handlers[chat_id]))

    @access_list_check
    def subtraction_handler(self, update, *args, **kwargs):
        chat_id = update.message.chat_id
        self.handlers[chat_id] = subtraction_dialogue(chat_id)
        self._send_response(update, chat_id, next(self.handlers[chat_id]))
        self._send_response(update, chat_id, next(self.handlers[chat_id]))

    @access_list_check
    def request_handler(self, update, *args, **kwargs):
        chat_id = update.message.chat_id
        if chat_id in self.handlers:
            try:
                answer = self.handlers[chat_id].send(update)
                self._send_response(update, chat_id, answer)
            except StopIteration:
                del self.handlers[chat_id]
                self._send_response(update, chat_id, "Choose new command: /addition, /subtraction.")

    def _send_response(self, update, chat_id, response):
        if isinstance(response, str):
            update.message.reply_text(response)
        elif isinstance(response, BotResponse):
            message = update.message.reply_text('Result:')
            update.message.reply_text(
                str(response),
                reply_to_message_id=message.message_id)
            _ = self.handlers[chat_id].send(update)
        else:
            update.message.reply_text('I did not understand.')


if __name__ == "__main__":
    dialog_bot = DialogueBot(TOKEN)
    dialog_bot.start()
