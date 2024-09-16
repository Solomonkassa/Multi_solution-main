# import os
# import telebot
# from telebot import types
# from telebot.types import WebAppInfo
# from dotenv import load_dotenv
# from messages import *
# from translations import translate as _
# from account.models import *
# from enrollment.models import *
# from finance.models import *
# import threading
# import time

# load_dotenv()

# BOT_TOKEN = os.getenv('BOT_TOKEN')

# bot = telebot.TeleBot(BOT_TOKEN)
# DEFAULT_LANGUAGE = 'en'
# LANGUAGES = {}
# INVITE_LINK = "https://t.me/MultiSolutionBot?start={}"  



# @bot.message_handler(commands=["language", _("language", "amharic"), _("language", "oromic")])
# @bot.message_handler(
#     func=lambda msg: not Preference.objects.filter(tg_id=msg.from_user.id).exists()
# )
# def select_language(message):
#     markup = types.InlineKeyboardMarkup(row_width=2)
#     btn1 = types.InlineKeyboardButton("English", callback_data="english")
#     btn2 = types.InlineKeyboardButton("አማርኛ", callback_data="amharic")
#     btn3 = types.InlineKeyboardButton("Afaan Oromo", callback_data="oromic")
#     markup.add(btn1, btn2, btn3)
#     with open('/root/Multi_solution/Assets/languages.png', 'rb') as photo:
#         bot.send_photo(message.chat.id, photo, caption=choose_lang, reply_markup=markup)
        
# def delete_message_after_delay(chat_id, message_id, delay_seconds):
#     time.sleep(delay_seconds)
#     try:
#         bot.delete_message(chat_id=chat_id, message_id=message_id)
#     except Exception as e:
#         print(f"Error deleting message: {e}")



# @bot.callback_query_handler(func=lambda call: call.data in ['english', 'amharic', 'oromic'])
# def handle_language_selection(call: types.CallbackQuery):
#     user = call.from_user
#     pref = Preference.objects.filter(tg_id=user.id)
#     if pref.exists():
#         pref = pref.first()
#         created = False
#     else:
#         pref, created = Preference.objects.get_or_create(tg_id=user.id)

#     pref.language = call.data
#     pref.save()
#     msg = bot.send_message(call.message.chat.id, text=_("Language Selected Successfully ✅", pref.language),)
#     bot.delete_message(call.message.chat.id, call.message.id)

#     bot.answer_callback_query(
#         call.id,
#         _(f"The Language Preference is set to {pref.language.capitalize()}", pref.language),
#     )

#     msg.from_user = user
#     con = Contact.objects.filter(tg_id=msg.from_user.id).first()

#     if con:
#         welcome(msg)
#     else:
#         request_contact_share(msg)
        
        

# @bot.message_handler(
#     func=lambda msg: not Contact.objects.filter(tg_id=msg.from_user.id).exists()
# )

# def request_contact_share(message):
#     pref = Preference.objects.filter(tg_id=message.from_user.id).first()
    
#     keyboard = types.ReplyKeyboardMarkup(
#         row_width=1,
#         resize_keyboard=True,
#         one_time_keyboard=True
#     )
#     share = _("📲 Share your contact to get started!", pref.language)
#     btn1 = types.KeyboardButton(_("Share Contact 👩‍🎓", pref.language), request_contact=True)
#     keyboard.add(btn1)
    
#     with open('/root/Multi_solution/Assets/share_contact.png', 'rb') as photo:
#         response_message = bot.send_photo(
#             message.chat.id, photo, caption=f"{share}",
#             reply_markup=keyboard  
#         )
#     try:
#         bot.delete_message(message.chat.id, message.message_id)
#     except telebot.apihelper.ApiTelegramException as e:
#         print(f"Failed share to delete message {message.message_id}: {e}")
    
#     #Start a thread to delete the message after 10 seconds
#     threading.Thread(target=delete_message_after_delay, args=(message.chat.id, response_message.message_id, 10)).start()
    
# @bot.message_handler(content_types=["contact"])
# def handle_shared_contact(message: types.Message):
#     contact = message.contact
#     first_name = contact.first_name
#     phone_number = contact.phone_number
#     last_name = contact.last_name
#     user_id = contact.user_id

#     pref = Preference.objects.filter(tg_id=user_id).first()

#     con, is_created = Contact.objects.get_or_create(
#         tg_id=user_id,
#         chat_id=message.chat.id,
#     )
#     user, is_created = User.objects.get_or_create(
#         tg_id=user_id,
#         chat_id=message.chat.id,
#     )
#     user.phone_number = phone_number
#     user.save()
    
#     con.first_name = first_name
#     con.last_name = last_name
#     con.phone_number = phone_number
#     con.save()
    
#     try:
#         bot.delete_message(message.chat.id, message.message_id)
#     except telebot.apihelper.ApiTelegramException as e:
#         print(f"Failed handle to delete message {message.message_id}: {e}")
        
#     # Send a message and store the returned message object
#     response_message = bot.send_message(
#         chat_id=message.chat.id,
#         text=_("Contact Received ✅", pref.language)
#     )
#     #Start a thread to delete the message after 1 seconds
#     threading.Thread(target=delete_message_after_delay, args=(message.chat.id, response_message.message_id, 1)).start()
    

#     start(message)
    
    
# @bot.message_handler(commands=['start', 'restart']) 
# def start(message):
#     select_language(message)
#     try:
#         bot.delete_message(message.chat.id, message.message_id)
#     except telebot.apihelper.ApiTelegramException as e:
#         print(f"Failed start to delete message {message.message_id}: {e}")
    

# @bot.message_handler(commands=['welcome']) 
# def welcome(message, userId=None):
#     if userId:
#         pref = Preference.objects.filter(tg_id=userId).first()
#     else:
#         pref = Preference.objects.filter(tg_id=message.from_user.id).first()

#     inline_markup = types.InlineKeyboardMarkup(row_width=2)
#     first_name = message.from_user.first_name.capitalize()
#     last_name = message.from_user.last_name.capitalize() if message.from_user.last_name else ""
#     full_name = f"{first_name} {last_name}"
#     welcome_msg = _(start_msg, pref.language)


#     btn1 = types.InlineKeyboardButton(_("Trainee 🦺", pref.language), callback_data="trainee")
#     btn2 = types.InlineKeyboardButton(_("Settings ⚙️", pref.language), callback_data="settings")
#     btn3 = types.InlineKeyboardButton(_("Invite Friends 🤝", pref.language), url='tg://share?text=Join https://t.me/JedanCodingSchoolBot')

#     inline_markup.row(btn1, btn2)
#     inline_markup.row(btn3)

#     with open('/root/Multi_solution/Assets/welcome_dr.png', 'rb') as photo:
#         bot.send_photo(message.chat.id, photo, caption=f"{welcome_msg}".format(full_name), reply_markup=inline_markup)

#     try:
#         bot.delete_message(message.chat.id, message.message_id)
#     except telebot.apihelper.ApiTelegramException as e:
#         print(f"Failed welcome to delete message {message.message_id}: {e}")

# def status(message, userId=None):
    
    
#     pref = Preference.objects.filter(tg_id=userId).first()
#     payment = TraineePayment.objects.filter(user__tg_id=userId).first()
#     con = Contact.objects.filter(tg_id=userId).first()
#     markup = types.InlineKeyboardMarkup(row_width=2)

#     if not pref:
#         btn = types.InlineKeyboardButton(_("⬅️ Back", pref.language), callback_data="trainee")
#         markup.add(btn)
#         with open('/root/Multi_solution/Assets/404-Error.png', 'rb') as photo:
#             bot.send_photo(message.chat.id, photo, caption=f"User preferences not found.",  reply_markup=markup)
        
#     if payment:
#         # Extract the necessary user information
#         first_name = con.first_name.capitalize()
#         trans_num = payment.trans_num
#         phone_number = payment.user.phone_number

#         # Prepare the success message
#         success_msg = _(transaction_success, pref.language)  
#         success_caption = success_msg.format(first_name, trans_num, phone_number)
#         pending_msg = _(transaction_pending, pref.language)
#         pending_caption = pending_msg.format(first_name, trans_num, phone_number)
        
#         # Check the completion status of the payment
#         if payment.is_completed:
#             with open('/root/Multi_solution/Assets/approved.png', 'rb') as photo:
#                 btn = types.InlineKeyboardButton(_("⬅️ Back", pref.language), callback_data="trainee")
#                 markup.add(btn)
#                 bot.send_photo(message.chat.id, photo, caption=success_caption,  reply_markup=markup)
#         else:
#             with open('/root/Multi_solution/Assets/pending.png', 'rb') as photo:
#                     btn = types.InlineKeyboardButton(_("⬅️ Back", pref.language), callback_data="trainee")
#                     markup.add(btn)
#                     bot.send_photo(message.chat.id, photo, caption=pending_caption,  reply_markup=markup)
    
#     else:
#         btn = types.InlineKeyboardButton(_("⬅️ Back", pref.language), callback_data="trainee")
#         markup.add(btn)
#         with open('/root/Multi_solution/Assets/404-Error.png', 'rb') as photo:
#             bot.send_photo(message.chat.id, photo, caption=f"User Payment transaction number is not found.",  reply_markup=markup)
                

# @bot.callback_query_handler(func=lambda call: True)
# def handle_call_back(callback):
#     command = callback.data
#     pref = Preference.objects.filter(tg_id=callback.from_user.id).first() 
#     full_name = f"{callback.from_user.first_name} {callback.from_user.last_name}" if callback.from_user.last_name else callback.from_user.first_name

#     if command in ['english', 'amharic', 'oromic']:
#         LANGUAGES[callback.from_user.id] = command
#         bot.send_message(callback.message.chat.id, f'Language set to {command.capitalize()}')

#     elif command == 'back':
#         userId = callback.message.chat.id
#         welcome(callback.message, userId)

#     elif command == 'trainee':
#         langRegi = _(welcome_learner, pref.language)
#         markup = types.InlineKeyboardMarkup(row_width=2)
#         btn1 = types.InlineKeyboardButton(_('📝 Register', pref.language), callback_data='register')
#         btn2 = types.InlineKeyboardButton(_("📥 Documents", pref.language), web_app=WebAppInfo(url='https://drive.google.com/file/d/1ckOCVdlMukkvZn8RS0zhp97_3XzOlDfy/view?usp=sharing'))
#         btn3 = types.InlineKeyboardButton(_("🎬 How to work", pref.language), web_app=WebAppInfo(url='https://www.youtube.com/watch?v=ZBzhl4xKqe4'))
#         btn4 = types.InlineKeyboardButton(_("📊 Status", pref.language), callback_data='status')

#         btn5 = types.InlineKeyboardButton(_("⬅️ Back", pref.language), callback_data="back")


#         markup.add(btn1, btn2, btn3, btn4)
#         markup.add(btn5)

#         with open('/root/Multi_solution/Assets/trainee.png', 'rb') as photo:
#             bot.send_photo(callback.message.chat.id, photo, caption=f"{langRegi}".format(full_name), reply_markup=markup)

#         try:
#             bot.delete_message(callback.message.chat.id, callback.message.message_id)
#         except telebot.apihelper.ApiTelegramException as e:
#             print(f"Failed learner to delete message {callback.message.message_id}: {e}")
            
#     elif command == 'register':
        
#         term_msg = _(terms_msg, pref.language)
#         markup = types.InlineKeyboardMarkup(row_width=2)
#         btn1 = types.InlineKeyboardButton(_("✅ Accept", pref.language), callback_data='enroll')
#         btn2 = types.InlineKeyboardButton(_("❌ Decline", pref.language), callback_data='trainee')
        
#         markup.add(btn1, btn2)
#         with open('/root/Multi_solution/Assets/Accept-terms.png', 'rb') as photo:
#             bot.send_photo(callback.message.chat.id, photo, caption=term_msg, reply_markup=markup)
#         try:
#             bot.delete_message(callback.message.chat.id, callback.message.message_id)
#         except telebot.apihelper.ApiTelegramException as e:
#             print(f"Failed register to delete message {callback.message.message_id}: {e}")
            
#     elif command == 'enroll':
        
#         term_msg = _(enroll_msg, pref.language)
#         markup = types.InlineKeyboardMarkup(row_width=2)
#         btn1 = types.InlineKeyboardButton(_('📝 Register', pref.language),  web_app=WebAppInfo(url='https://multi-solution-frontend.vercel.app/'))
#         btn2 = types.InlineKeyboardButton(_("⬅️ Back", pref.language), callback_data="trainee")
        
#         markup.add(btn1, btn2)
#         with open('/root/Multi_solution/Assets/Forms.png', 'rb') as photo:
#             bot.send_photo(callback.message.chat.id, photo, caption=term_msg, reply_markup=markup)
#         try:
#             bot.delete_message(callback.message.chat.id, callback.message.message_id)
#         except telebot.apihelper.ApiTelegramException as e:
#             print(f"Failed enroll to delete message {callback.message.message_id}: {e}")
            
        
#     elif command == 'status':
#         userId = callback.message.chat.id
#         status(callback.message, userId)
#         try:
#             bot.delete_message(callback.message.chat.id, callback.message.message_id)
#         except telebot.apihelper.ApiTelegramException as e:
#             print(f"Failed language to delete message {callback.message.message_id}: {e}")
            
#     elif command == 'settings':

#         langSettings = _(settings_msg, pref.language)
#         markup = types.InlineKeyboardMarkup(row_width=2)
#         btn1 = types.InlineKeyboardButton(_('👤 Profile', pref.language), callback_data='profile')
#         btn2 = types.InlineKeyboardButton(_('🌐 Language', pref.language), callback_data='language')
#         btn3 = types.InlineKeyboardButton(_('📞 Contact Support', pref.language), web_app=WebAppInfo(url='https://multi-solution-frontend.vercel.app/contact-us'))
#         btn4 = types.InlineKeyboardButton(_("⬅️ Back", pref.language), callback_data="back")

#         markup.add(btn1, btn2, btn3)
#         markup.add(btn4)
#         with open('/root/Multi_solution/Assets/settings.png', 'rb') as photo:
#             bot.send_photo(callback.message.chat.id,photo, caption=langSettings, reply_markup=markup)

#         try:
#             bot.delete_message(callback.message.chat.id, callback.message.message_id)
#         except telebot.apihelper.ApiTelegramException as e:
#             print(f"Failed settings to delete message {callback.message.message_id}: {e}")

#     elif command == 'profile':
#         langMar = _(profile_msg, pref.language)
#         markup = types.InlineKeyboardMarkup(row_width=2)
#         btn1 = types.InlineKeyboardButton(_('🔄 Update', pref.language), web_app=WebAppInfo(url='https://www.google.com/'))
#         btn2 = types.InlineKeyboardButton(_("⬅️ Back", pref.language), callback_data="settings") 

#         markup.add(btn1)
#         markup.add(btn2)

#         with open('/root/Multi_solution/Assets/profile.png', 'rb') as photo:
#             bot.send_photo(callback.message.chat.id, photo, caption=langMar, reply_markup=markup)

#         try:
#             bot.delete_message(callback.message.chat.id, callback.message.message_id)
#         except telebot.apihelper.ApiTelegramException as e:
#             print(f"Failed profile to delete message {callback.message.message_id}: {e}")
#     elif command == 'language':
#         select_language(callback.message)

#         try:
#             bot.delete_message(callback.message.chat.id, callback.message.message_id)
#         except telebot.apihelper.ApiTelegramException as e:
#             print(f"Failed language to delete message {callback.message.message_id}: {e}")

#     elif command == 'close':
#         bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id, reply_markup=None)
        
#     else:
#         bot.send_message(callback.message.chat.id, 'Invalid option')
        
#         try:
#             bot.delete_message(callback.message.chat.id, callback.message.message_id)
#         except telebot.apihelper.ApiTelegramException as e:
#             print(f"Failed profile to delete message {callback.message.message_id}: {e}")

# @bot.message_handler(commands=['help'])
# def help_command(message):
#     pref = Preference.objects.filter(tg_id=message.from_user.id).first()
#     helpText = _(help, pref.language)
#     with open('/root/Multi_solution/Assets/help_dr.png', 'rb') as photo:
#         bot.send_photo(message.chat.id,photo, caption=helpText)

#     try:
#         bot.delete_message(message.chat.id, message.message_id)
#     except telebot.apihelper.ApiTelegramException as e:
#         print(f"Failed help to delete message {message.message_id}: {e}")

# bot.infinity_polling()
