#i think here in this case i donnot use the tools of telegram directly
#import telegram
from telegram import update, Update
#telegram.ext is a submodule of telegram
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext
import configparser
#a python standard lib for log
import logging
import redis
#update chatbot with chatgpt api
from ChatGPT_HKBU import HKBU_ChatGPT

#global variable redis1
global redis1

def main():
    config=configparser.ConfigParser()
    config.read('config.ini')
#Updater : continuously fetch new updates from telegram and pass them on to Dispatcher class
#create an instance of Updater class
#use_context=True : my handler will recieve the Context object as a argument
    updater=Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']),use_context=True)
    dispatcher=updater.dispatcher

    global redis1
#create an instance of Redis
    redis1=redis.Redis(host=(config['REDIS']['HOST']),
                       password=(config['REDIS']['PASSWORD']),
                       port=(config['REDIS']['REDISPORT']),
                       decode_responses=(config['REDIS']['DECODE_RESPONSE']),
                       username=(config['REDIS']['USER_NAME']))

#config the format or others for the output log
    logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#diapater for echo function
#Filters.text is a filter,~Filters.command is a deny filter to exclude commands text,
# here combine these 2 filters
#echo is a callback function (i defined it) to deal with the messages
    #echo_handler=MessageHandler(Filters.text & (~Filters.command),echo)
    #dispatcher.add_handler(echo_handler)

#dispater for chatgpt
    global chatgpt
    chatgpt=HKBU_ChatGPT(config)
    chatgpt_handler=MessageHandler(Filters.text & (~Filters.command),equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

#dispatchers for self defined cmd
    dispatcher.add_handler(CommandHandler("add",add))
    dispatcher.add_handler(CommandHandler("help",help_command))
    dispatcher.add_handler(CommandHandler("hello",hello_name))
    
#start chatbot
    updater.start_polling()
    updater.idle()

#use ChatGPT API
def equiped_chatgpt(update,context):
    global chatgpt
    reply_message=chatgpt.submit(update.message.text)
    logging.info("Update:"+str(update))
    logging.info("context:"+str(context))
    context.bot.send_message(chat_id=update.effective_chat.id,text=reply_message)

#define the function echo to process the updated messages
def echo(update,context):
    reply_message=update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("Context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id,text=reply_message)

# no return value
#Send a message when the command /help is issue.
def help_command(update:Update,context:CallbackContext):
    update.message.reply_text("Helping you helping you.")


#no return value
#Send a message when the command /add is issue
def add(update:Update,context:CallbackContext):
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]
        redis1.incr(msg)
# get(msg) may not need decode???
        update.message.reply_text('You have said ' + msg + ' for ' + redis1.get(msg) + ' times.')
    except(IndexError,ValueError):
        update.message.reply_text('Usage: /add <keyword>')

#define /hello <name> , no return value
def hello_name(update:Update,context:CallbackContext):
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]
        redis1.incr(msg)
        update.message.reply_text('Good day , '+msg+' !')
    except(IndexError,ValueError):
        update.message.reply_text('Usage: /hello <your name>')



if __name__=='__main__':
    main()

