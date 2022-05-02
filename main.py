# Imports
import requests
import urllib
import json
import telegram.ext
import random, string
from telegram import *
from telegram.ext import *
from telegram.ext import ConversationHandler
import logging

# Reads the link shortener API ###
with open('cuttly_key.txt') as f:
    cuttly_api = f.read()
# Reads the Telegram API ###
with open('API_theshortener.txt') as g:
    api_telegram = g.read()
# Reads the Stripe(Payment) Test API ###
with open('stripe_test.txt') as h:
    api_stripe_test = h.read()
# Reads the Stripe(Payment) LIVE API ###
with open('stripe_live.txt') as o:
    api_stripe_live = o.read()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

LINK = range(1)


# Functions ###

def first_access(update, context):
    with open('first_access.txt', 'r') as rr:
        seek = rr.readlines()

    seek = [i.replace('\n', '') for i in seek]

    with open('first_access.txt', 'a') as ra:
        if str(update.message.chat.id) not in seek:
            ra.writelines(str(update.message.chat.id))
            ra.writelines('\n')


def instructions(update, context):  # Function to send the instructions to the user.
    print('triggered_instructions')
    text = 'In order to use the link shortener function, just paste the link /here'
    update.message.reply_text(text)  # Command that sends the message to the user.


def here(update, context):
    print('triggered_here')
    text = "Ok, send me the link you want to shorten!"
    update.message.reply_text(text)
    return LINK


def here_qr(update, context) -> None:
    print('triggered_here_qr')
    keyboard = [['Yes', 'No']]
    with open('premium.txt', 'r') as rr:
        seek = rr.readlines()
        seek = [i.replace('\n', '') for i in seek]

    if str(update.message.chat.id) in seek:
        text = "Ok, just send me the link and I'll be right back with your QR Code"
        update.message.reply_text(text)
        return LINK

    else:
        my_file = open("qrcode_log.txt", "r")
        data = my_file.read()
        data_into_list = data.split("\n")
        id = str(update.message.chat.id)
        print(id)
        print(data_into_list)
        counter = data_into_list.count(id)
        if counter < 5:
            text = """Ok, just send me the link and I'll be right back with your QR Code.
            
You've used <b>{} of your 5</b> trial QR Code generations""".format(counter)
            update.message.reply_text(text, parse_mode='HTML')
            with open('qrcode_log.txt', 'a') as ra:
                ra.writelines(str(update.message.chat.id))
                ra.writelines('\n')
            return LINK
        else:
            update.message.reply_text(
                'Oh...Unfortunately you do not have access to this function anymore.\n\n'
                """<b>To have unlimited access to QR Code generator you must be premium.</b>\n
Do you want to become a premium member?""",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard, one_time_keyboard=True, input_field_placeholder='Yes or No?'), parse_mode='HTML')
            return ConversationHandler.END


# """Unused for now... TO BE IMPLEMENTED"""
def premiumm(update, context) -> str:
    print('triggered_premium')
    f = update.message.text
    print(f)

    url = 'https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=N6PVHHQVAHCJE'

    buttons = [[InlineKeyboardButton("Become Premium!", url=url)]]
    reply_markup = InlineKeyboardMarkup(buttons)

    update.message.reply_text('To become a premium member and <b>enjoy unlimited benefits</b>, click the button below!',
                              disable_web_page_preview=True, reply_markup=reply_markup, parse_mode='HTML')

    return ConversationHandler.END  # Uni


def premium(update, context) -> None:
    chat_id = update.message.chat_id
    title = "Premium User"
    description = "Premium 'The Shortener'"
    payload = "The Shortener Bot"
    provider_token = api_stripe_live
    currency = "USD"
    price = 5
    prices = [LabeledPrice("Test", price * 100)]

    context.bot.send_invoice(
        chat_id,
        title,
        description,
        payload,
        provider_token,
        currency,
        prices,
        need_name=True
    )


def precheckout_callback(update, context) -> None:
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload != 'The Shortener Bot':
        # answer False pre_checkout_query
        query.answer(ok=False, error_message="Something went wrong...")
    else:
        query.answer(ok=True)


def successful_payment_callback(update: Update, context: CallbackContext) -> None:
    with open('premium.txt', 'r') as rr:
        seek = rr.readlines()

    seek = [i.replace('\n', '') for i in seek]

    with open('premium.txt', 'a') as ra:
        if str(update.message.chat.id) not in seek:
            ra.writelines(str(update.message.chat.id))
            ra.writelines('\n')
    update.message.reply_text("Great! Your payment was successful! You can now enjoy everything this bot has to offer!")


def qr(update, context):
    print('triggered_qr')
    f = update.message.text
    qr_code = 'https://api.qrserver.com/v1/create-qr-code/?size=350x350&data={}'.format(f)
    update.message.reply_photo(qr_code)
    update.message.reply_text("Done! You're ready to go")

    return ConversationHandler.END


def shortener(update, context):
    print('triggered_shortener')
    update.message.reply_text("Your link is on it's way!")
    f = update.message.text
    x = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    # url = urllib.parse.quote(f)
    name = x
    r = requests.get('http://cutt.ly/api/api.php?key={}&short={}&name={}'.format(cuttly_api, f, name))
    curto = r.json()

    shortened = curto['url']['shortLink']

    update.message.reply_text(shortened)
    update.message.reply_text("Done! You're ready to go")

    return ConversationHandler.END


def thank_you(update, context):
    print('triggered_thankyou')
    update.message.reply_text("You're welcome!! It's always a pleasure!")


def issue(update, context):
    print('triggered_issue')
    update.message.reply_text("Looks like what you sent something wrong...")


def message_handle(update, context):
    # print('triggered_message_handle')

    first_access(update, context)

    keyboard = [['Shorten a Link', 'Generate QR Code', 'Instructions']]

    update.message.reply_text("""Hi! Welcome to <b>'The Shortener'</b>, the best service for shortening links and generating QR Codes!

Choose one of the options below to get started!""",
                              reply_markup=ReplyKeyboardMarkup(
                                  keyboard, one_time_keyboard=True, input_field_placeholder='Choose an option'),
                              parse_mode='HTML')


# Telegram Updater ans Conversation Handlers ###

def main() -> None:
    updater = telegram.ext.Updater(api_telegram, use_context=True)
    disp = updater.dispatcher

    # Conversation Handler 01 ###
    conv_handler1 = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Shorten a Link'), here)],
        states={
            LINK: [MessageHandler(Filters.text, shortener)]},
        fallbacks=[CommandHandler('issue', issue)]
    )

    # Conversation Handler 02 ###

    conv_handler2 = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Generate QR Code'), here_qr)],

        states={
            LINK: [
                MessageHandler(
                    Filters.text, qr
                ),
            ],
        },
        fallbacks=[CommandHandler('issue', issue)]
    )

    # Functions triggers ###

    disp.add_handler(conv_handler1)
    disp.add_handler(conv_handler2)

    disp.add_handler(MessageHandler(Filters.regex('Yes'), premium))
    disp.add_handler(MessageHandler(Filters.regex('Shorten a Link'), here))
    disp.add_handler(MessageHandler(Filters.regex('Generate QR Code'), here_qr))
    disp.add_handler(MessageHandler(Filters.regex('Instructions'), instructions))
    disp.add_handler(MessageHandler(Filters.regex('Thank you'), thank_you))

    disp.add_handler(MessageHandler(Filters.text, message_handle))

    disp.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    disp.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))

    # Updates the "timeline" seeking for new messages ###

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
