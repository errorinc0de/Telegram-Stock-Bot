import sys
import json
import time
import requests
import yfinance as yf
import secret as botAuth
import urllib.parse
from datetime import date

def retrieveChatId():
    url = "https://api.telegram.org/bot" + botAuth.token + "/getUpdates"

    response = requests.get(url).text
    chatId = json.loads(response)["result"][-1]["message"]["chat"]["id"]
    #print(response)

    chatId = str(chatId)
    return chatId

def getStock(stockCom):
    #Validity checker for token
    if len(botAuth.token) > 40:
        botToken = botAuth.token
    else:
        print("Invalid Credential: Error in Token")
        quit()
    
    botChatId = retrieveChatId()
    
    currency = ''
    currPrice = 0
    prevPrice = 0

    #Getting the currency symbol for the company
    
    stockCompany = yf.Ticker(stockCom)
    #print(stockCompany)
    try:
        stockCompany_dict = stockCompany.info
    except:
        telegramMessage = "Wrong Keyword!\nTry Again with the proper keyword :("
        telegramMessage = urllib.parse.quote_plus(telegramMessage)
        url = "https://api.telegram.org/bot" + botToken + "/sendMessage?chat_id=" + botChatId + "&text=" + telegramMessage
        #print(url)
        response = requests.get(url)
        print("Try Again with the proper keyword")
        return
    
    #print(stockCompany_dict)
    stockCompany_json = json.dumps(stockCompany_dict)
    #print(stockCompany_json)
    stockCompany_json = json.loads(stockCompany_json)
    #print(stockCompany_json)
    company = stockCompany_json["longName"]
    fiftyTwoWeekHigh = stockCompany_json["fiftyTwoWeekHigh"]
    fiftyTwoWeekLow = stockCompany_json["fiftyTwoWeekLow"]
    marketCap = stockCompany_json["marketCap"]
    logoUrl = stockCompany_json["logo_url"]
    #print(marketCap)
    if stockCompany_json["currency"] != '':
        #print(currency)
        currency = stockCompany_json["currency"]
    
    #downloading the daily stock data
    stockCompany_dailyData = yf.download(stockCom,period="2d")
    #print(stockCompany_dailyData["Close"][1])

    if prevPrice == 0:
        prevPrice = (stockCompany_dailyData["Close"][0]).round(2)
    else:
        prevPrice = currPrice
    
    currPrice = (stockCompany_dailyData["Close"][1]).round(2)

    if currPrice == prevPrice or prevPrice == 0:
        priceChangeStatus = ''
        priceChangeValue_Description = ''
    elif currPrice > prevPrice:
        priceChangeStatus = "UP🔺"
        priceChangeValue = (currPrice - prevPrice).round(2)
        priceChangePercentage = (priceChangeValue/prevPrice)*100
        #print(priceChangeValue)
        priceChangeValue_Description = "\n▫ *Status:* " + priceChangeStatus + "\n▫ *Value:* {} +".format(currency) + str("{0:.2f}".format(priceChangeValue)).replace(',', '\'') + "\n▫ *Percentage:* +{0:.2f}%".format(priceChangePercentage)
        #print(priceChangeValue_Description)
    else:
        priceChangeStatus = "DOWN🔻"
        priceChangeValue = (prevPrice - currPrice).round(2)
        priceChangePercentage = (priceChangeValue/prevPrice)*100
        #print(priceChangeValue)
        priceChangeValue_Description = "\n▫ *Status:* " + priceChangeStatus + "\n▫ *Value:* {} -".format(currency) + str("{0:.2f}".format(priceChangeValue)).replace(',', '\'') + "\n▫ *Percentage:* -{0:.2f}%".format(priceChangePercentage)
        #print(priceChangeValue_Description)

    #Formatting MESSAGE
    telegramMessage = "*Current status of requested stock for {0}({1}):*\n\n".format(company,stockCom)
    telegramMessage += "▫ *Current Price:* " + currency + " " + str("{0:.2f}".format(currPrice)).replace(',', '\'') + " " + priceChangeValue_Description
    telegramMessage += "\n▫ *Market Capital:* " + currency + " {0:,}".format(marketCap)
    telegramMessage += "\n▫ *Fifty Two Week High:* {1} {0:.2f}".format(fiftyTwoWeekHigh,currency)
    telegramMessage += "\n▫ *Fifty Two Week Low:* {1} {0:.2f}".format(fiftyTwoWeekLow,currency)
    telegramMessage += "\n\n\n▫ *Logo:* " + logoUrl
    #print(telegramMessage)
    telegramMessage = urllib.parse.quote_plus(telegramMessage)
    #print(telegramMessage)

    url = "https://api.telegram.org/bot" + botToken + "/sendMessage?chat_id=" + botChatId + "&parse_mode=markdown&text=" + telegramMessage
    #print(url)
    response = requests.get(url)
    #print(response)

def retrieveInput(botChatId):
    """
    Pulls out the user input array
    """
    retrieveUrl = "https://api.telegram.org/bot" + botAuth.token + "/getUpdates?timeout=5"
    resIp = requests.get(retrieveUrl).text
    resIp = json.loads(resIp)
    resIp = resIp["result"][-1]["message"]
    if(str(resIp["chat"]["id"])==botChatId):
        try:
            reqCom = resIp["text"][1:]
        except:
            reqCom = 'st'
        if(reqCom.lower() == "start"):
            reqCom = 'st'
        elif(reqCom.lower() == "pause"):
            reqCom = 'pause'
        elif(reqCom.lower() == "end"):
            reqCom = 'end'
        return reqCom

def wait(botChatId):
    checkStaticUrl = "https://api.telegram.org/bot" + botAuth.token + "/getUpdates"
    lastMessage = requests.get(checkStaticUrl).text
    lastMessage = json.loads(lastMessage)
    lastMessage = lastMessage["result"][-1]["message"]
    if(str(lastMessage["chat"]["id"])==botChatId):
        msg = lastMessage["text"][1:]
        if(msg.lower() == "pause"):
            msg = 'pause'
        elif(msg.lower() == "end"):
            print("Exit request received.")
            message = "Exit request received.\nBot has successfully shut down!"
            url = "https://api.telegram.org/bot" + botAuth.token + "/sendMessage?chat_id=" + botChatId + "&disable_notification=true&text=" + message
            #print(url)
            response = requests.get(url)
            quit()
        return msg

while(True):
    botChatId = retrieveChatId()
    reqCom = retrieveInput(botChatId)
    time.sleep(2)
    if(reqCom == 'st'):
        message = "Please enter the Symbol of the Company according to NYSE in format: */SYMBOL* where SYMBOL is symbol of the company!"
        url = "https://api.telegram.org/bot" + botAuth.token + "/sendMessage?chat_id=" + botChatId + "&parse_mode=markdown&text=" + message
        #print(url)
        response = requests.get(url)
    elif(reqCom == 'pause'):
        message = "You have successfully stopped streaming updates!\nTo start streaming again, enter command /START"
        url = "https://api.telegram.org/bot" + botAuth.token + "/sendMessage?chat_id=" + botChatId + "&disable_notification=true&text=" + message
        #print(url)
        response = requests.get(url)
        while(reqCom == 'pause'):
            reqCom = wait(botChatId)
    elif(reqCom == 'end'):
        print("Exit request received.")
        message = "Exit request received.\nBot has successfully shut down!"
        url = "https://api.telegram.org/bot" + botAuth.token + "/sendMessage?chat_id=" + botChatId + "&disable_notification=true&text=" + message
        #print(url)
        response = requests.get(url)
        quit()
    else:
        getStock(reqCom)
    time.sleep(2)