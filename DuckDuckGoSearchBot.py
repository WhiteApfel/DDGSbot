import logging
import requests
from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from bs4 import BeautifulSoup
from user_agent import generate_user_agent

API_TOKEN = '211412442:NJjdfsdfbsbjhb#Bjh3bjhb#HJV3ghhg3'

# webhook settings
WEBHOOK_HOST = f'https://any.host.tld'
WEBHOOK_PATH = f'/{API_TOKEN}'  # Или любой другой нужный путь
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'
# webserver settings
WEBAPP_HOST = '0.0.0.0'  # or ip
WEBAPP_PORT = 32123

logging.basicConfig(level=logging.CRITICAL)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


@dp.inline_handler()
async def inline_echo(inline_query: types.InlineQuery):
	req = " ".join(inline_query.query.split(" "))
	site = requests.get(f'https://duckduckgo.com/html?q={req}&b=&kl=ru-ru&df=',
						headers={"User-Agent": generate_user_agent()})
	data = site.text
	parsed = BeautifulSoup(data, "html.parser")
	topics = parsed.find_all("div", class_='links_main links_deep result__body')

	results = []
	for i in enumerate(topics[:10]):
		id_n = str(i[0])
		head = i[1].h2.a.text
		link = i[1].h2.a["href"]
		img = "https:" + i[1].div.div.span.a.img["src"]
		text = ''
		if link[4] != "s":
			text = i[1].find("a", class_="result__snippet").text
		markup = types.InlineKeyboardMarkup()
		callback_button = types.InlineKeyboardButton(text="Попробуй найти сам 🦆", url=f'http://duckduckgo.com?q={req}')
		markup.add(callback_button)
		results.append(types.InlineQueryResultArticle(
			id=id_n,
			title=head,
			input_message_content=types.InputTextMessageContent(
				f"<b>Я попросил найти </b><code>{req}</code>\n<b>🦆 Утка накрякала:</b>\n\n<b>{head}</b>\n{link}\n\n{text}",
				parse_mode="html"
			),
			reply_markup=markup,
			thumb_url=img,
			description=f"{link}\n{text}"
		))
	await bot.answer_inline_query(inline_query.id, results, cache_time=100)


@dp.message_handler(commands=["ping"])
async def echo(message: types.Message):
	await bot.send_message(message.chat.id, "/pong")


@dp.message_handler(commands=["start", "help"])
async def echo(message: types.Message):
	await bot.send_message(message.chat.id,
						   "Кря! 👋\n\nЯ - уткобот, помогу тебе отправлять результаты поиска 🦆 DuckDuckGo практически в любой чат через inline-запрос.\n\nПросто в нужном диалоге набери в поле вввода сообщения <code>@ddgsbot</code> и затем нужный запрос для поиска. Должно получиться что-то вроде <code>@ddgsbot штанишки</code>\n\nНадеюсь, я смог внести хоть немного позитива в твою жизнь 😅 С любовью, <a href='https://pfel.cc/'>WhiteApfel</a>")


async def on_startup(dp):
	await bot.set_webhook(WEBHOOK_URL)


# insert code here to run it after start


async def on_shutdown(dp):
	logging.warning('Shutting down..')

	# insert code here to run it before shutdown

	# Remove webhook (not acceptable in some cases)
	await bot.delete_webhook()

	# Close DB connection (if used)
	await dp.storage.close()
	await dp.storage.wait_closed()

	logging.warning('Bye!')


if __name__ == '__main__':
	start_webhook(
		dispatcher=dp,
		webhook_path=WEBHOOK_PATH,
		on_startup=on_startup,
		on_shutdown=on_shutdown,
		skip_updates=True,
		host=WEBAPP_HOST,
		port=WEBAPP_PORT
	)
