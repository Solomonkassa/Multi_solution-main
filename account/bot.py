import os
import telebot
from telebot import types
from telebot.types import WebAppInfo
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from dotenv import load_dotenv
from .messages import *
from .translations import translate as _
from .models import *
from enrollment.models import *
from finance.models import *
import threading
import time

User = get_user_model()
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
DEFAULT_LANGUAGE = 'en'
LANGUAGES = {}
INVITE_LINK = "https://t.me/EyasuPortfolioBot?start={}"



@bot.message_handler(commands=["language", _("language", "amharic")])
@bot.message_handler(
    func=lambda msg: not Preference.objects.filter(tg_id=msg.from_user.id).exists()
)
def select_language(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("English", callback_data="english")
    btn2 = types.InlineKeyboardButton("አማርኛ", callback_data="amharic")
    #btn3 = types.InlineKeyboardButton("Afaan Oromo", callback_data="oromic")
    markup.add(btn1, btn2)
    with open('./Assets/languages.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=choose_lang, reply_markup=markup)

def delete_message_after_delay(chat_id, message_id, delay_seconds):
    time.sleep(delay_seconds)
    try:
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")



@bot.callback_query_handler(func=lambda call: call.data in ['english', 'amharic'])
def handle_language_selection(call: types.CallbackQuery):
    user = call.from_user
    pref = Preference.objects.filter(tg_id=user.id)
    if pref.exists():
        pref = pref.first()
        created = False
    else:
        pref, created = Preference.objects.get_or_create(tg_id=user.id)

    pref.language = call.data
    pref.save()
    msg = bot.send_message(call.message.chat.id, text=_("Language Selected Successfully ✅", pref.language),)
    bot.delete_message(call.message.chat.id, call.message.id)

    bot.answer_callback_query(
        call.id,
        _(f"The Language Preference is set to {pref.language.capitalize()}", pref.language),
    )

    msg.from_user = user
    Traineecon = Trainee.objects.filter(tg_id=msg.from_user.id).first()

    if Traineecon:
        welcome(msg)
    else:
        request_contact_share(msg)



def request_contact_share(message):
    pref = Preference.objects.filter(tg_id=message.from_user.id).first()

    keyboard = types.ReplyKeyboardMarkup(
        row_width=1,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    share = _("📲 Share your contact to get started!", pref.language)
    btn1 = types.KeyboardButton(_("Share Contact 👩‍🎓", pref.language), request_contact=True)
    keyboard.add(btn1)

    with open('./Assets/share_contact.png', 'rb') as photo:
        response_message = bot.send_photo(
            message.chat.id, photo, caption=f"{share}",
            reply_markup=keyboard
        )
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Failed share to delete message {message.message_id}: {e}")

    #Start a thread to delete the message after 10 seconds
    threading.Thread(target=delete_message_after_delay, args=(message.chat.id, response_message.message_id, 10)).start()

@bot.message_handler(content_types=["contact"])
def handle_shared_contact(message: types.Message):
    try:
        # Extract contact information
        contact = message.contact
        user_id = contact.user_id
        phone_number = contact.phone_number


        # Modify phone number if it starts with '+'
        if phone_number.startswith('+'):
            phone_number = phone_number[1:]

        # Retrieve user preferences based on Telegram ID
        pref = Preference.objects.filter(tg_id=user_id).first()

        # Check if the phone number already exists in the User table
        phone_exists = User.objects.filter(phone_number=phone_number).exists()
        user, is_created = User.objects.get_or_create(
                tg_id=user_id,
                defaults={
                    'chat_id': message.chat.id,
                    'phone_number': phone_number,
                    'is_phone_verified': True,
                    'is_trainee': True,
                }
            )
        if not is_created:
                # Update existing Trainee object
            user.chat_id = message.chat.id
            user.is_phone_verified = True
            user.save()

    except Exception as e:
        print(f"Failed to save contact information to the database: {e}")

    # Send confirmation message
    response_message = bot.send_message(
        chat_id=message.chat.id,
        text=_("Contact Received ✅", pref.language)
    )

    # Start a thread to delete the confirmation message after 1 second
    threading.Thread(target=delete_message_after_delay, args=(message.chat.id, response_message.message_id, 1)).start()

    # Call start function to initiate further actions
    start(message)


@bot.message_handler(commands=['start', 'restart']) 
def start(message):

    Traineecon= Trainee.objects.filter(tg_id=message.from_user.id).first()
    if Traineecon:
        welcome(message)

    else:
        select_language(message)
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"This is Failed start to delete message {message.message_id}: {e}")


@bot.message_handler(commands=['welcome']) 
def welcome(message, userId=None):
    if userId:
        pref = Preference.objects.filter(tg_id=userId).first()
    else:
        pref = Preference.objects.filter(tg_id=message.from_user.id).first()
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    welcome_msg = _(start_msg, pref.language)


    btn1 = types.InlineKeyboardButton(_("Trainee 🦺", pref.language), callback_data="trainee")
    btn2 = types.InlineKeyboardButton(_("Settings ⚙️", pref.language), callback_data="settings")
    btn3 = types.InlineKeyboardButton(_("Invite Friends 🤝", pref.language), url=INVITE_LINK)

    inline_markup.row(btn1, btn2)
    inline_markup.row(btn3)


    with open('./Assets/welcome_dr.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=welcome_msg, reply_markup=inline_markup)

    try:
        bot.delete_message(message.chat.id, message.message_id)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Failed welcome to delete message {message.message_id}: {e}")
          

@bot.callback_query_handler(func=lambda call: True)
def handle_call_back(callback):
    command = callback.data
    pref = Preference.objects.filter(tg_id=callback.from_user.id).first()
    userlang = pref.language[:2]
    user_lang = userlang if userlang in ["en", "am"] else "en"
    Traineecon = Trainee.objects.filter(tg_id=callback.from_user.id).first()
    phone_number = Traineecon.phone_number
    user = get_object_or_404(User, phone_number=phone_number)
    trainee_payment = TraineePayment.objects.filter(user=user).first()
    monthly_payment_cycle =  MonthlyPaymentCycle.objects.filter(is_active=True).first()

    full_name = f"{callback.from_user.first_name} {callback.from_user.last_name}" if callback.from_user.last_name else callback.from_user.first_name

    if command in ['english', 'amharic']:
        LANGUAGES[callback.from_user.id] = command
        bot.send_message(callback.message.chat.id, f'Language set to {command.capitalize()}')

    def back():
        userId = callback.message.chat.id
        welcome(callback.message, userId)

    def trainee():

            langRegi = _(welcome_learner, pref.language)
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton(_('📝 Register', pref.language), callback_data='register')
            btn3 = types.InlineKeyboardButton(_("📥 Documents", pref.language), web_app=WebAppInfo(url='https://drive.google.com/file/d/1ckOCVdlMukkvZn8RS0zhp97_3XzOlDfy/view?usp=sharing'))
            btn4 = types.InlineKeyboardButton(_("🎬 How to work", pref.language), web_app=WebAppInfo(url='https://www.youtube.com/watch?v=ZBzhl4xKqe4'))
            btn5 = types.InlineKeyboardButton(_("💳 Monthly Payment", pref.language), callback_data='monthlypayment')
            btn6 = types.InlineKeyboardButton(_("⬅️ Back", pref.language), callback_data="back")

            try:
                # Check if the trainee payment is completed and the monthly payment cycle is active
                if hasattr(trainee_payment, 'is_completed') and hasattr(monthly_payment_cycle, 'is_active') and trainee_payment.is_completed and monthly_payment_cycle.is_active:
                    url = f"http://localhost:5173/bot/success/monthly-payment/invoice/{phone_number}?lng={user_lang}"
                    status_button = types.InlineKeyboardButton(_('📊 Status', pref.language), web_app=WebAppInfo(url=url))

                    # Add the buttons to the markup
                    markup.add(status_button, btn3, btn4, btn5)
                    markup.add(btn6)
                elif hasattr(Traineecon, 'is_reg_complete') and hasattr(Traineecon, 'is_trainee') and Traineecon.is_reg_complete and Traineecon.is_trainee:
                    url = f"http://localhost:5173/bot/success/invoice/{phone_number}?lng={user_lang}"
                    btn2 = types.InlineKeyboardButton(_('📊 Status', pref.language), web_app=WebAppInfo(url=url))
                    markup.add(btn2, btn3, btn4)
                    markup.add(btn6)
                else:
                    markup.add(btn1, btn3, btn4)
                    markup.add(btn6)
            except Exception as e:

                print(f"An error occurred: {e}")


            with open('./Assets/trainee.png', 'rb') as photo:
                bot.send_photo(callback.message.chat.id, photo, caption=f"{langRegi}".format(full_name), reply_markup=markup)

            try:
                bot.delete_message(callback.message.chat.id, callback.message.message_id)
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Failed to delete message {callback.message.message_id}: {e}")


    def monthlypayment():
        try:
            phone_number = Traineecon.phone_number
            monthly_msg = _(monthly_pay, pref.language)
            url = f"http://localhost:5173/bot/payment/monthly-payment/{phone_number}?lng={user_lang}"
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton(_('💳 Monthly Payment', pref.language), web_app=WebAppInfo(url=url))
            btn2 = types.InlineKeyboardButton(_("⬅️ Back", pref.language), callback_data="trainee")
            markup.add(btn1, btn2)
            with open('./Assets/Forms.png', 'rb') as photo:
                bot.send_photo(callback.message.chat.id, photo, caption=monthly_msg, reply_markup=markup)
            try:
                bot.delete_message(callback.message.chat.id, callback.message.message_id)
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Failed to delete message {callback.message.message_id}: {e}")

        except Exception as e:
            print(f"Error in monthlypayment function: {e}")


    def register():

        term_msg = _(terms_msg, pref.language)
        markup = types.InlineKeyboardMarkup(row_width=2)

        btn1 = types.InlineKeyboardButton(_("✅ Accept", pref.language), callback_data='enroll')
        btn2 = types.InlineKeyboardButton(_("❌ Decline", pref.language), callback_data='trainee')

        markup.add(btn1, btn2)
        with open('./Assets/Accept-terms.png', 'rb') as photo:
            bot.send_photo(callback.message.chat.id, photo, caption=term_msg, reply_markup=markup)
        try:
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Failed register to delete message {callback.message.message_id}: {e}")

    def enroll():

        term_msg = _(enroll_msg, pref.language)
        
        url = f"http://localhost:5173/bot/account/update/{phone_number}/?lng={user_lang}"
        # url = f"https://www.youtube.com/watch?v=ZBzhl4xKqe4"
        Traineecon.is_reg_complete = True
        Traineecon.save()

        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton(_('📝 Register', pref.language),  web_app=WebAppInfo(url=url))
        btn2 = types.InlineKeyboardButton(_("⬅️ Back", pref.language), callback_data="trainee")

        markup.add(btn1, btn2)
        with open('./Assets/Forms.png', 'rb') as photo:
            bot.send_photo(callback.message.chat.id, photo, caption=term_msg, reply_markup=markup)
        try:
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Failed enroll to delete message {callback.message.message_id}: {e}")

    def settings():

        userlang = pref.language[:2]
        user_lang = userlang if userlang in ["en", "am", "or"] else "en"
        url = f"http://localhost:5173/bot/contact-us/?lng={user_lang}"
        langSettings = _(settings_msg, pref.language)
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton(_('👤 Profile', pref.language), callback_data='profile')
        btn2 = types.InlineKeyboardButton(_('🌐 Language', pref.language), callback_data='language')
        btn3 = types.InlineKeyboardButton(_('📞 Contact Support', pref.language), web_app=WebAppInfo(url=url))
        btn4 = types.InlineKeyboardButton(_("⬅️ Back", pref.language), callback_data="back")

        markup.add(btn1, btn2, btn3)
        markup.add(btn4)
        with open('./Assets/settings.png', 'rb') as photo:
            bot.send_photo(callback.message.chat.id,photo, caption=langSettings, reply_markup=markup)

        try:
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Failed settings to delete message {callback.message.message_id}: {e}")

    def profile():
        userlang = pref.language[:2]
        user_lang = userlang if userlang in ["en", "am", "or"] else "en"
        url = f"http://localhost:5173/bot/account/update/{phone_number}/?lng={user_lang}"
        langMar = _(profile_msg, pref.language)
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton(_('🔄 Update', pref.language), web_app=WebAppInfo(url=url))
        btn2 = types.InlineKeyboardButton(_("⬅️ Back", pref.language), callback_data="settings") 

        markup.add(btn1)
        markup.add(btn2)

        with open('./Assets/profile.png', 'rb') as photo:
            bot.send_photo(callback.message.chat.id, photo, caption=langMar, reply_markup=markup)

        try:
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Failed profile to delete message {callback.message.message_id}: {e}")

    def language():
        select_language(callback.message)

        try:
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Failed language to delete message {callback.message.message_id}: {e}")

    def close():
        bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id, reply_markup=None)

    call_back = {
        "back": back, "trainee": trainee,
        "register": register, "enroll": enroll,
        "settings": settings, "profile": profile,
        "language": language, "monthlypayment": monthlypayment,
        "close": close
    }

    if command in call_back:
        call_back[command]()
    else:
        bot.send_message(callback.message.chat.id, 'Invalid option')
        
        try:
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Failed profile to delete message {callback.message.message_id}: {e}")
    



#bot.infinity_polling()

# http://localhost:5173/
# https://multisolution.et

# solo tg id 6296919002  1109337954