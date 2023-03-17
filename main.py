from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram import executor, types, Bot, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.utils.callback_data import CallbackData
from selenium import webdriver
from selenium.webdriver.common.by import By
from threading import Thread
import codecs
import os
import time
import asyncio
import codecs

async def reg(message):
    db = await open('users.json')
    
    if message['from']['id'] not in db:
        db[message['from']['id']] = {'num': 0, 'status_download': False, 'link_channel': 0}
    

    await write('users.json', db)
    
    return db


async def open(file_name):
    with codecs.open(str(file_name), 'r', 'utf-8') as file:
        value = eval(str(file.readline()))
        file.close()
        
    return value

async def write(file_name, source):
    with codecs.open(str(file_name), 'w', 'utf-8') as file:
        value = file.write(str(source))
        file.close()

    return value

BOT_TOKEN = '' # Токен бота
admin = [6107240072] # Вставить свой ID
chromedriver = 'chromedriver' # Путь до драйвера хром

print('BOT WORK')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

source_res = str(os.getcwd())
url_ip = 'https://snaptik.app/'

def start_download_video(user_id, url):
    asyncio.run(download_video(user_id, url))

async def download_video(user_id, url):

    bot = Bot(token=BOT_TOKEN)
    db = await open('users.json')

    db[user_id]['status_download'] = False
    await write('users.json', db)

    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', {"download.default_directory": source_res})
    options.add_argument("headless")
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(executable_path = chromedriver, options = options)
    driver.get(url = url_ip)
    time.sleep(1)
    driver.find_element(By.XPATH, '/html/body/main/div[1]/div/div[2]/form/div/div[3]/input').send_keys(url)
    time.sleep(1)
    driver.find_element(By.XPATH, '/html/body/main/div[1]/div/div[2]/form/div/div[4]/button').click()
    time.sleep(5)
    driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div/div[2]/div/a[1]').click()
    time.sleep(5)

    
    names = os.listdir(source_res)

    for i in names:
        try:
            if str(i[-4:]) == '.mp4':
                name_file = str(i)
        except:
            pass

    value = InputFile(name_file)
    os.remove(name_file)

    

    await bot.send_video(chat_id = user_id, video = value, caption = '<b>✅ Ваше видео готово</b>', parse_mode = 'html')


@dp.message_handler(commands=['start'])
async def start(message):
    db = await reg(message)
    
    await bot.send_message(chat_id = message.chat.id, text = '''
<b>
✅ Я помогу тебе скачать видео из Тик Ток. Отправь мне ссылку
</b>
        ''', parse_mode = 'html')
    

@dp.message_handler()
async def all_handler(message):
    db = await reg(message)
    ig = str(message.text)
    next_stape = True
    if int(message.from_user.id) in admin:
        if ig[:5] == '/send' and next_stape == True:
            next_stape = False
            print(1)
            for i in db:
                try:
                    await bot.send_message(chat_id = i, text = message.text[6:])
                except:
                    pass

            await message.reply('Рассылка окончена')

        if ig[:6] == '/stats' and next_stape == True:
            next_stape = False

            await bot.send_message(chat_id = message.from_user.id, text = 'Пользователей в боте: ' + str(len(db)))
        if ig[:4] == '/del' and next_stape == True:
            next_stape = False
            try:

                value = await open('channels.json')

                del value[str(message.text)[5:]]
                await write('channels.json', value)

                await bot.send_message(chat_id = message.from_user.id, text = 'Канал удалён')

            except Exception as ex:
                print(ex) 
                await bot.send_message(chat_id = message.from_user.id, text = 'После команды /del укажите ссылку канала чере @\n\nПример: /del @asdasdasd')

        if db[message.from_user.id]['num'] == 1 and next_stape == True:
            next_stape = False
            db[message.from_user.id]['link_channel'] = str(message.text)
            db[message.from_user.id]['num'] = 2

            await write('users.json', db)

            await bot.send_message(chat_id = message.from_user.id, text = '''
Введите называние канала, которое будет отображаться для пользователя
                ''')

        if db[message.from_user.id]['num'] == 2 and next_stape == True:
            next_stape = False
            
            value = await open('channels.json')

            value[str(db[message.from_user.id]['link_channel'])] = str(message.text)

            db[message.from_user.id]['num'] = 0
            await write('users.json', db)
            await write('channels.json', value)

            await bot.send_message(chat_id = message.from_user.id, text = 'Канал успешно добавлен')

        if ig[:4] == '/add' and next_stape == True:
            next_stape = False

            db[message.from_user.id]['num'] = 1
            await write('users.json', db)

            await bot.send_message(chat_id = message.from_user.id, text = '''
Введите ссылку на канал без @

Пример: для добавления канала @twochannel, введите twochannel
                ''')

    if next_stape == True:
        with codecs.open('channels.json', 'r' ,encoding="UTF-8") as file:
            channels_me = str(file.readline())
            channels_me = eval(channels_me)
            file.close()
        

        if len(channels_me) == 0:
            c = 1
        else:
            inline_kb1 = InlineKeyboardMarkup()
            for i in channels_me:
                print(i)
                user_channel_status = await bot.get_chat_member(chat_id='@' + str(i), user_id= message.from_user.id)

                if user_channel_status["status"] == 'left':
                    

                    for i in channels_me:
                        inline_btn_1 = InlineKeyboardButton(str(channels_me[i]), url='https://t.me/'+ str(i))
                        
                        inline_kb1.add(inline_btn_1)
                    
                    
                    await bot.send_message(chat_id = message.from_user.id, text = '*📝 Для использования бота, вы должны быть подписаны на каналы:*',reply_markup = inline_kb1,parse_mode = 'Markdown')
                    c = 0
                    break
                else:
                    c = 1
        if c == 1:



            if db[message.from_user.id]['status_download'] == False:
                db[message.from_user.id]['status_download'] = True
                await write('users.json', db)

                await bot.send_message(chat_id = message.from_user.id, text = '''
<b>
⏳ Начали скачивание вашего видео, ожидайте...
</b>
                    ''', parse_mode = 'html')
                my_id = int(message.from_user.id)
                url = str(message.text)

                give= Thread(target=start_download_video, args=(my_id, url))
                give.start()

            else:
                await bot.send_message(chat_id = message.from_user.id, text = '''
<b>
❌ У вас уже есть активное скачивание видео, ожидайте...
</b>
                    ''', parse_mode = 'html')




if __name__ == "__main__":
    executor.start_polling(dp, skip_updates = True)