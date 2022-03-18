import re
import sqlite3
import datetime
import string    
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update , Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from telegram import *
from telegram.ext import *
import telegram

from web3 import Web3
from ethtoken.abi import EIP20_ABI
bsc =  "https://rpc.tomochain.com"
w3 = Web3(Web3.HTTPProvider(bsc))




# create a code incloud ascii_uppercase + digits od any lens
def create_trace_code(len_of_code):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k = len_of_code))    


# connect to sqlite
def db_connect():
    return sqlite3.connect('tel.db')

# connect to bot
new_bot = Bot("bot api")
print(new_bot)

# Basic info
channelv =  ["@SolidityDevelopers"] 


#connet to db and create tables if its not exist in first run
con = db_connect()
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS user_info (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    tel_id VARCHAR(30),
    user_id VARCHAR(30),
    twitter VARCHAR(100),
    instagram VARCHAR(100),
    trace_code VARCHAR(24),
    referral_count INTEGER,
    date DATETIME);""")

cur.execute("CREATE INDEX IF NOT EXISTS index_user_info ON user_info (user_id);")

cur.execute("""CREATE TABLE IF NOT EXISTS step (
    id INTEGER PRIMARY KEY,
    user_id VARCHAR(30),
    instagram VARCHAR(100),
    referral VARCHAR(30),
    this_step VARCHAR(1),
    date DATETIME);""")

cur.execute("CREATE INDEX IF NOT EXISTS index_step ON step (user_id);")

con.commit()
con.close()

# keyboard layouts



keyee =[["🆔 Account"],["👫 Referrals","💸 Withdraw"],["ℹ️ More Information"]]
vemi = ReplyKeyboardMarkup(keyee,one_time_keyboard=False,resize_keyboard=True)
def check_member(user_id):
    for i in channelv:
        temp = new_bot.get_chat_member(i, user_id)
        if temp['status'] == 'left':
            return False
        else:
            return True
    return True


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    if update.message.chat['type'] == "private":
    # get user informations
        referral = re.escape(update.message.text[7:36])
        user = update.effective_user
        user_id = user['id']

    # dont let user to refferal him self
        if str(user_id) == referral:
            referral = ''

        this_date = datetime.datetime.now()
        con = db_connect()
        cur = con.cursor()

    # create or update step table row
        cur.execute("SELECT EXISTS(SELECT user_id from step WHERE user_id={});".format(user_id))
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO step (user_id, instagram, referral, this_step, date) VALUES ({},'','{}',0,'{}');".format(user_id, referral, this_date))
        else:
            cur.execute("UPDATE step SET instagram='', referral='{}', this_step=0, date='{}' WHERE user_id={};".format(referral, this_date, user_id))

    # detect that user already done steps or not and send related text to him
        cur.execute("SELECT EXISTS(SELECT user_id from user_info WHERE user_id={});".format(user_id))
        if cur.fetchone()[0] == 0:
            keyee =[["Continue ✅"]]
            svemi = ReplyKeyboardMarkup(keyee,one_time_keyboard=False,resize_keyboard=True)
            msg_start = f"Hi *{user.first_name}* I am your friendly *Elon Floki Doge* Airdrop Bot\n\n" \
                     "✅Please complete all the tasks and submit details correctly to be eligible for the airdrop\n\n" \
                     "💲* Total for airdrop: 500 Billion Elon Floki Doge Token\n" \
                     "🔸 1 Million ($12) Elon Floki Doge for each valid referal\n" \
                     "👫 Airdrop Distrribution is paid INSTANTLY*.\n\n" \
                     "📘 By Participating you are agreeing to the *Elon Floki Doge* Bot (Airdrop) Program Term's and Conditions. Please see pinned post for more information.\n\n" \
                     "Click \"*Continue*\" to proceed"
            update.message.reply_text(msg_start, reply_markup=svemi,parse_mode="markdown")
        else:
        # alredy exists
            update.message.reply_markdown_v2('Hey {} \nWelcome back'.format(user.mention_markdown_v2()), reply_markup=vemi)

        con.commit()
        con.close()

def join_channels(update: Update, context: CallbackContext) -> None:
    if update.message.chat['type'] == "private":
        msg_start = f"*Complete the task below!\n\nAll the tasks are mandatory*\n\n" \
                    f"*1.* Join *Elon Floki Doge* [Channel](https://t.me/ElonflokiDogeAnn) || [Group](https://t.me/ElonFlokiDogeChat)\n" \
                    f"*2.* Join *Sponsor* [Channel](t.me/Defi_Clan)\n*3.* Join *Promoter* [Channel](https://t.me/legitairdrops010)\n\n" \
                    f"Click \"*Joined *✅\""
        keyee =[["Joined ✅"]]
        svemi = ReplyKeyboardMarkup(keyee,one_time_keyboard=False,resize_keyboard=True)
        update.message.reply_text(msg_start,parse_mode="markdown",disable_web_page_preview=True,reply_markup=svemi)
        
def joined(update: Update, context: CallbackContext) -> None:
    if update.message.chat['type'] == "private":
        user = update.effective_chat.id

        con = db_connect()
        cur = con.cursor()
        
        if check_member(user) == True:
            cur.execute("UPDATE step SET this_step=0 WHERE user_id={};".format(user))
            msg_start = f"*Complete the task below!\n\nAll the tasks are mandatory*\n\n" \
                        f"*1.* Follow *Elon Floki Doge* on [Twitter](https://twitter.com/intent/follow?screen_name=ElonFlokiDoge)\n" \
                        f"*2.* Follow *Sponsor* on [Twitter](https://twitter.com/intent/follow?screen_name=Defi_Clan))\n*3.* Follow *Promoter* on [Twitter](https://twitter.com/intent/follow?screen_name=DynamicAirdrops)" \
                        "\n\nSubmit your *Twitter* profile link (Example: https://www.twitter.com/yourusername)"
            update.message.reply_text(msg_start,parse_mode="markdown",disable_web_page_preview=True)
            
        else:
            msg_start = f"*Complete the task below!\n\nAll the tasks are mandatory*\n\n" \
                        f"*1.* Join *Elon Floki Doge* [Channel](https://t.me/ElonflokiDogeAnn) || [Group](https://t.me/ElonFlokiDogeChat)\n" \
                        f"*2.* Join *Sponsor* [Channel](t.me/Defi_Clan)\n*3.* Join *Promoter* [Channel](https://t.me/legitairdrops010)\n\n" \
                        f"Click \"*Joined *✅\""
            update.message.reply_text(msg_start,parse_mode="markdown",disable_web_page_preview=True)
            
        con.commit()
        con.close()
def referals(update: Update, context: CallbackContext) -> None:
    if update.message.chat['type'] == "private":
        user_id = update.message.chat.id
        con = db_connect()
        cur = con.cursor()
        cur.execute("SELECT EXISTS(SELECT user_id from step WHERE user_id={});".format(user_id))
        cur.execute("SELECT this_step,instagram,referral FROM step WHERE user_id={};".format(user_id))
        
        cur.execute("SELECT referral_count FROM user_info WHERE user_id={};".format(user_id))
        data = cur.fetchone()
        update.message.reply_text('⏯️* Total Invites : {} Users\n\n🔗 Referral Link ⬇️\n\nhttps://telegram.me/ElonFlokiDogeRound2AirdopBot?start={}*'.format(data[0],user_id),parse_mode="markdown",disable_web_page_preview=True)
 
        con.commit()
        con.close()
        

def more_info(update: Update, context: CallbackContext) -> None:
    if update.message.chat['type'] == "private":
        msg = f"Hey <b>{update.message.chat.first_name}</b>\n\n" \
              f"☎️ <b>Telegram Announcement</b> -: https://t.me/ElonFlokiDogeAnn \n\n" \
              f"🐦 Twitter  -: https://twitter.com/intent/follow?screen_name=ElonFlokiDoge \n\n" \
              f"🦜 <b>Telegram Community</b> - : https://t.me/ElonFlokiDogeChat \n\n" \
              f"💹 <b>Contract</b> -: <code>0x01bBd41d1a7068ce176aa4b3189a508a6c915183</code> \n\n" \
              f"💩 <b>listing price will be Upto 12$ per 1M</b> 🤝 \n\n" \
              f"You will get 12$ Worth of EFD for each valid referal."
        update.message.reply_text(msg,parse_mode="html",disable_web_page_preview=True)



def echo(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    user_id = user['id']
    if update.message.chat['type'] == "private":
        con = db_connect()
        cur = con.cursor() 
        cur.execute("SELECT this_step,instagram,referral FROM step WHERE user_id={};".format(user_id))
        data = cur.fetchone()
        temp = data[0]
        print(temp)
        cur.execute("SELECT EXISTS(SELECT user_id from step WHERE user_id={});".format(user_id))
        if cur.fetchone()[0] == 0:
            cur.execute("SELECT EXISTS(SELECT user_id from user_info WHERE user_id={});".format(user_id))
            x = datetime.datetime.now()
            if cur.fetchone()[0] == 0:
            # new user
                cur.execute("INSERT INTO step (user_id, instagram, referral, this_step, date) VALUES ({},'','',0,'{}');".format(user_id, x))
                update.message.reply_markdown_v2('Hey {} \njoin the group'.format(user.mention_markdown_v2()))
            else:
            # alredy exists
                cur.execute("INSERT INTO step (user_id, instagram, referral, this_step, date) VALUES ({},'','',0,'{}');".format(user_id, x))
                update.message.reply_markdown_v2('Hey {} \nyou already done'.format(user.mention_markdown_v2()),reply_markup=vemi)
        else:
            cur.execute("SELECT this_step,instagram,referral FROM step WHERE user_id={};".format(user_id))
            data = cur.fetchone()
            temp = data[0]
            if temp == '1':
            # twitter
                temp = re.escape(update.message.text[0:100])
                username = user['username']
                name = update.message.chat.first_name if update.message.chat.first_name != None else ''
                lname = update.message.chat.last_name if update.message.chat.last_name != None else ''
                name = name + ' ' + lname
                wall = update.message.text
                print(wall)
                update.message.reply_text("Wallet Set: {}".format(update.message.text),reply_markup=vemi)
                cur.execute("SELECT EXISTS(SELECT user_id from user_info WHERE user_id={});".format(user_id))
                cur.execute("UPDATE step SET this_step=2 WHERE user_id={};".format(user_id))
                x = datetime.datetime.now()
                cur.execute("SELECT EXISTS(SELECT user_id from user_info WHERE user_id={});".format(user_id))
                if cur.fetchone()[0] == 0:
                # insert info
                # get uniqe trace_code
                    while(1):
                        trace_code = create_trace_code(12)
                        cur.execute("SELECT EXISTS(SELECT user_id from user_info WHERE trace_code='{}');".format(trace_code))
                        if cur.fetchone()[0] == 0:
                            break

                    cur.execute("INSERT INTO user_info (name,tel_id,user_id,twitter,instagram,trace_code,referral_count,date) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}');".format(name,username,user_id,temp,wall,trace_code,0,x))
                
                # update referraler counter when new user created
                    if data[2] != '':
                        cur.execute("SELECT referral_count FROM user_info WHERE user_id={};".format(data[2]))
                        try:
                            counter = cur.fetchone()[0]
                            cur.execute("UPDATE user_info SET referral_count={} WHERE user_id={};".format(counter+1,data[2]))
                        except:
                            pass
                    else:
                # update info
                        cur.execute("UPDATE user_info SET name='{}',tel_id='{}',twitter='{}',instagram='{}',date='{}' WHERE user_id={};".format(name,username,temp,data[1],x,user_id))
                        cur.execute("SELECT trace_code from user_info WHERE user_id={};".format(user_id))
                        trace_code = cur.fetchone()[0]
            
                        cur.execute("DELETE FROM step WHERE user_id={};".format(user_id))
                        update.message.reply_text('thanks\nyour tracking code is this: `{}` \n'.format(trace_code, user_id),reply_markup=vemi,parse_mode="markdown")
                        cur.execute("SELECT EXISTS(SELECT user_id from user_info WHERE user_id={});".format(user_id))
                        cur.execute("UPDATE step SET this_step=2 WHERE user_id={};".format(user_id))
            elif temp == '0':
                cur.execute("SELECT EXISTS(SELECT user_id from user_info WHERE user_id={});".format(user_id))
                cur.execute("UPDATE step SET this_step=1 WHERE user_id={};".format(user_id))
                update.message.reply_text('enter your *TOMO WALLET*\nMake sure wallet is correct',parse_mode="markdown")
            # group
           
        con.commit()
        con.close()

def acc(update: Update, context: CallbackContext) -> None:
    if update.message.chat['type'] == "private":
        user_id = update.message.chat.id
        con = db_connect()
        cur = con.cursor()
        cur.execute("SELECT EXISTS(SELECT user_id from step WHERE user_id={});".format(user_id))
        
        cur.execute("SELECT twitter,referral_count FROM user_info WHERE user_id={};".format(user_id))
        
        data = cur.fetchone()
        print(data)
        bal = data[1]
        man ="{0:,}".format(int(int(bal)*2000000+1000000))
        update.message.reply_text('*⚙️ Wallet :* `{}`\n\n💸 *Balance : {} EFDD*\n\nIf your wallet not correct type /reset'.format(data[0],man),parse_mode="markdown",disable_web_page_preview=True)
 
        con.commit()
        con.close()


def bot_bal():
    try:
        contract = w3.eth.contract(address="0x01bBd41d1a7068ce176aa4b3189a508a6c915183 ", abi=abis)
        decimal = decimals_contract(address)
        wal = w3.toChecksumAddress("0x8FFbdb92009Ca4b71Be47491F80fdb1174788784") 
        dead1 = float(contract.functions.balanceOf(wal).call({'from': address})/10 ** 18)
        return dead1
    except Exception:
        return "0"        
def withy(update: Update, context: CallbackContext) -> None:
    if update.message.chat['type'] == "private":
        user_id = update.message.chat.id
        con = db_connect()
        cur = con.cursor()
        cur.execute("SELECT EXISTS(SELECT user_id from step WHERE user_id={});".format(user_id))
        
        cur.execute("SELECT referral_count,twitter FROM user_info WHERE user_id={};".format(user_id))
        
        data = cur.fetchone()
        if data[0] < 5:
            update.message.reply_text("Minimum withdraw is 10,000,000 EFD\nMinimum of 5 referrals")
        elif float(bot_bal())< float("100000000"):
            update.message.reply_text("Bot Balance less than 100,000,000\nPlease wait for refill then make request")
        else:
            try:
                
                amo = int(data[0])*2000000
                token_to = data[1]
                contract = w3.eth.contract(address="0x01bBd41d1a7068ce176aa4b3189a508a6c915183", abi=EIP20_ABI)

                nonce = w3.eth.getTransactionCount("0x8FFbdb92009Ca4b71Be47491F80fdb1174788784")  



        # Build a transaction that invokes this contract's function, called transfer
                token_txn = contract.functions.transfer(
                    token_to,
                    w3.toWei(amo,'ether'),
                ).buildTransaction({
                    'chainId': 88,
                    'gas': 80000,
                    'gasPrice': w3.toWei('1', 'gwei'),
                    'nonce': nonce,
                })


                signed_txn = w3.eth.account.signTransaction(token_txn, private_key="c7f3a1d052f9c1d4d55818cd0d23e68dd29f4c3973f14fc20b0a4583f2891ba7")
                txm = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
                hass= w3.toHex(txm)
                update.message.reply_text( f"✅* Withdraw is request is processed automatically*\n\nhttps://tomoscan.io/tx/{hass}", parse_mode="Markdown",disable_web_page_preview=True)
                cur.execute("SELECT EXISTS(SELECT user_id from step WHERE user_id={});".format(user_id))
                cur.execute("UPDATE user_info SET referral_count={} WHERE user_id={};".format(0,user_id))
                cur.execute("SELECT EXISTS(SELECT user_id from step WHERE user_id={});".format(user_id))
            except Exception as err:
                update.message.reply_text(f"An error ocuured please retry\nif continues message support\n\n`{err}`\n\nSend admin this message only if you retry and it didn't work",parse_mode="markdown")
        
        con.commit()
        con.close()
def reset(update: Update, context: CallbackContext) -> None:
    if update.message.chat['type'] == "private":
        user_id = update.message.chat.id
        con = db_connect()
        cur = con.cursor()
        this_date = datetime.datetime.now()
        cur.execute("DELETE FROM user_info WHERE user_id={};".format(user_id))
        cur.execute("DELETE FROM step WHERE user_id={};".format(user_id))
        update.message.reply_text(f"reset done restart bot")
        
        con.commit()
        con.close()
        

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("your bot api")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("reset", reset))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('^ℹ️ More Information$'),more_info))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('^Continue ✅$'),join_channels))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('^Joined ✅$'),joined))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('^👫 Referrals$'),referals))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('^🆔 Account$'),acc))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('^💸 Withdraw$'),withy))
    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
