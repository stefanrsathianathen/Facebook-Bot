from flask import Flask, request
import sys
from pymessenger import Bot
from fbmq import Attachment, Template, QuickReply, Page


'''
Things to work on:
get user current location (maybe save it??)
automatic messages
start applying machine learning
for checiking if location is stored: any('value2' in sublist for sublist in mylist)

'''

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAAaVvLCGPDoBANvqBAXomih2ZBeGk1uIMxv5SBf4YIdUYLtRkgi3EajbtnB7Py7RffTUo6pPgo1cqnIa62yenH5cDk9dVrHjwzlLLbpBMD21svVObDS3HFJyiahBTb8RQ2QRtXOsAedipyNRZCsuLMSy9DyRaODTR4ZCY3elAZDZD"

bot = Bot(PAGE_ACCESS_TOKEN)
page = Page(PAGE_ACCESS_TOKEN)

@app.route('/', methods=['GET'])
def verify():
	if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
		if not request.args.get("hub.verify_token") == "hello":
			return "Verification token mismatch", 403
		return request.args["hub.challenge"],200
	return "Hello world", 200


@app.route('/',methods=['POST'])
def webhook():
	data = request.get_json()
	log(data)

	if data['object']=='page':
		for entry in data['entry']:
			for messaging_event in entry['messaging']:

				#IDs
				sender_id = messaging_event['sender']['id']
				recipient_id = messaging_event['recipient']['id']

				if messaging_event.get('message'):
					if 'text' in messaging_event['message']:
						messaging_text = messaging_event['message']['text']
					else:
						messaging_text = 'no text'

					route(sender_id,messaging_text)
					

					#response = route(sender_id,messaging_text)

					#bot.send_text_message(sender_id, response)

	return "ok",200



GREETINGS = ["hello", "hi", "greetings", "sup", "what's up","whats up","whats","what's","how are you","yo","what up"]
GREETING_RESPONSES = ["'sup bro", "hey", "*nods*", "hey you get my snap?","what up","what do you need","At your service","what up fam"]

BYE =['ttyl','bye','see you later','sounds good','later','later fam','night','aight']
BYE_RESPONSES = ['ttyl','bye','see you later','sounds good','okay','aight','later fam']
todo = []

def route(sender_id,message):
	message_te = message.lower()
	# to do first shot
	if "add to todo" in message_te or "add to todo list" in message_te:
		ad = 5
		if "list" in message_te:
			ad = 10 
		return addtodo(sender_id,message,ad)
	if "remove from todo" in message_te or "remove from todo list" in message_te:
		ad = 5
		if "list" in message_te:
			ad = 10 
		return removeToDo(sender_id,message,ad)
	if "todo list" in message_te or "todo" == message_te:
		return printToDo(sender_id)
	
	#fun stefan quote
	if 'stefan' in message_te:
		return bot.send_text_message(sender_id,"Stefan is my master. He is the greatest. ;)")
	#help
	if message_te == 'help':
		return bot.send_text_message(sender_id, help())
	#future versions
	if message_te == 'expand':
		return bot.send_text_message(sender_id, expand())
	#NEWS
	if 'news' in message_te:
		return news(sender_id,message_te)
	#GREETINGS
	if message_te in GREETINGS:
		return bot.send_text_message(sender_id,greeting())
	#bye
	if message_te in BYE:
		return bot.send_text_message(sender_id,bye())
	#Answer to life
	if message_te == 'whats the meaning of life' or message_te == "what's the meaning of life":
		return bot.send_text_message(sender_id,'42')

	#STOCK PRICE
	if 1<=len(message_te)<=4:
		return bot.send_text_message(sender_id, stock(message_te))

	if 'weather' in message_te:
		return bot.send_text_message(sender_id, weather())

	return bot.send_text_message(sender_id, "I don't follow :'(")

def greeting():
	import random
	return GREETING_RESPONSES[random.randint(0,len(GREETING_RESPONSES)-1)]

def bye():
	import random
	return BYE[random.randint(0,len(BYE_RESPONSES)-1)]

def stock(ticker):
	from yahoo_finance import Share
	#Apple Inc. AAPL, 141.05 USD, -0.53%

	share = Share(ticker.upper())
	price = share.get_price()
	if price is None:
		return "Not a stock, Try another ticker :("
	else:
		return share.get_name() + " " + ticker.upper() + ", " + str(price) + " USD, " + share.get_change() + "%"

def weather():
	import pyowm

	owm = pyowm.OWM('f6c6c0e21b7d53f4068d82dbe9e3890c') 

	observation = owm.weather_at_place("Melbourne,aus") #CHANGE FOR LOCATION 
	w = observation.get_weather()  
	temperature = w.get_temperature('celsius')
	wind = w.get_wind()  
	
	forc = owm.daily_forecast('Melbourne,aus') #CHANGE FOR LOCATION 
	
	re =""
	tmp = "High of " + str(temperature['temp_max']) + "C\n" + "Low of " + str(temperature['temp_min']) +"C"
	if forc.will_have_rain():
		re += "Wear a waterproof jacket\n"

	if temperature['temp_max'] <= 20 or wind['speed'] > 10:
		re+= "It's going to be cold today\n"

	if re =="":
		re = "Nothing to worry about today! :)\n"

	return re + tmp
def help():
	
	return "Things that I can do right now:\n Tell you about the weather(today's only) :(\n Give you stock quotes\n A simple todo list\n Give you news\n 	-Breaking/Latest\n 	-Sports\n 	-Money/Financial\n 	-Tech\n 	-Social/Funny\n 	-Or just input news for something totally 	random :)\n;)"

def expand():

	return "Future versions will include:\n Better weather prediction \n Better conversation abilities\n And so much more :)"

def log(message):
	print(message)
	sys.stdout.flush()

def news(sender_id,message):
	#put urllib2 for heroku
	import urllib2, json, random
	#use case statment to filter through news 
 	#urllib2.urlopen
	source = " "
	if "breaking" in message or "latest" in message:
 		breaking = ['al-jazeera-english','abc-news-au','associated-press','bbc-news','business-insider','cnn','daily-mail','google-news','the-wall-street-journal','the-washington-post','time','the-guardian-au','the-guardian-uk','the-new-york-times','the-telegraph','the-huffington-post','usa-today']
 		source = breaking[random.randint(0,len(breaking)-1)]
 		
	elif "sports" in message or "sport" in message:
		sports = ['bbc-sport','espn','fox-sports','nfl-news','talksport','the-sport-bible','football-italia']
		source = sports[random.randint(0,len(sports)-1)]
		
	elif "money" in message or "financial" in message:
		money = ['bloomberg','breitbart-news','business-insider','business-insider-uk','cnbc','financial-times','fortune','the-economist']
		source = money[random.randint(0,len(money)-1)]
		
	elif "tech" in message or "technology" in message:
		tech = ['hacker-news','techcrunch','techradar','the-next-web','the-verge']
		source = tech[random.randint(0,len(tech)-1)]
		
	elif "social" in message or "funny" in message:
		funny =['buzzfeed','daily-mail','entertainment-weekly','ign','independent','mashable','mirror','mtv-news','mtv-news-uk','polygon','reddit-r-all','usa-today']
		source = funny[random.randint(0,len(funny)-1)],
		
	else:
		news = ['abc-news-au','al-jazeera-english','ars-technica','associated-press','bbc-news','bbc-sport','bild','bloomberg','breitbart-news','business-insider','business-insider-uk','buzzfeed','cnbc','cnn','daily-mail','der-tagesspiegel','die-zeit','engadget','entertainment-weekly','espn','espn-cric-info','financial-times','focus','football-italia','fortune','four-four-two','fox-sports','google-news','gruenderszene','hacker-news','handelsblatt','ign','independent','mashable','metro','mirror','mtv-news','mtv-news-uk','national-geographic','new-scientist','newsweek','new-york-magazine','nfl-news','polygon','recode','reddit-r-all','reuters','spiegel-online','t3n','talksport','techcrunch','techradar','the-economist','the-guardian-au','the-guardian-uk','the-huffington-post','the-lad-bible','the-new-york-times','the-next-web','the-sport-bible','the-telegraph','the-verge','the-wall-street-journal','the-washington-post','time','usa-today','wired-de']
		source = news[random.randint(0,len(news)-1)]

	newslink = urllib2.urlopen("https://newsapi.org/v1/articles?source=%s&sortBy=latest&apiKey=ad99bdcfb0954307abf6e0d3012dc1c7"%(source))
	response = json.loads(newslink.read().decode('utf-8'))

	re = []

	print(response['articles'])
	
	for x in response['articles']:
	    t = Template.GenericElement(x['title'],
                          subtitle=x['description'],
                          item_url=x['url'],
                          image_url=x['urlToImage'],
                          buttons=[
                              Template.ButtonWeb("Open Article", x['url'])
                          ])
	    re.append(t)

	
	page.send(sender_id, Template.Generic(re))






	'''page.send(sender_id, Template.Generic([
  Template.GenericElement(response['articles'][0]['title'],
                          subtitle=response['articles'][0]['description'],
                          item_url=response['articles'][0]['url'],
                          image_url=response['articles'][0]['urlToImage'],
                          buttons=[
                              Template.ButtonWeb("Open Article", response['articles'][0]['url'])
                          ])
]))'''


def addtodo(sender_id,message,ad):
	global todo
	
	loc = message.index("todo")
	todo.append([sender_id,message[loc+ad:]])
	printToDo(sender_id)

def printToDo(sender_id):
	global todo

	re = "TO-DO List:\n"
	for x in todo:
		if x[0]==sender_id:
			re += "-"+x[1] + "\n"
	'''
	if re == "TO-DO List:\n":
		re = "You have nothing to todo"'''
	bot.send_text_message(sender_id, re)	

def removeToDo(sender_id,message,ad):
	global todo

	loc = message.index('todo')
	for x in todo:
		if x[0] == sender_id and x[1] == message[loc+ad:]:
			todo.remove(x)
			print(todo)

	printToDo(sender_id)



if __name__ == '__main__':
	app.run(debug=False)