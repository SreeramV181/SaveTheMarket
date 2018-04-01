#Tweet splitting
import pandas as pd
from datetime import datetime
import fix_yahoo_finance as yf

#Reads in JSON file, sets up DataFrame, and removes unnececessary fields
tweetFrame = pd.read_json("tweets.json",orient='records')
tweetFrame.drop(columns=['id', 'images', 'isPinned', 'quote', 'urls', 'screenName', 'isReplyTo', 'isRetweet'], inplace=True)

#Reformat date
for index in range(0,len(tweetFrame.index)):
    date = datetime.strptime(tweetFrame.iloc[index]['time'], "%Y-%m-%dT%H:%M:%S.%fZ")
    tweetFrame.loc[index, 'DATE'] = date.strftime('%d-%m-%Y')#
    
    usersMentioned = [];
    for user in tweetFrame.at[index, 'userMentions']:
        usersMentioned.append(user['screenName'])
    tweetFrame.at[index, 'usersMentioned'] = usersMentioned
   
tweetFrame.drop(columns=['time', 'userMentions', 'hashtags'],inplace=True)

#Add common dates together
i = 0
while i < len(tweetFrame.index):
    i += 1
    if(tweetFrame.iloc[i]['DATE'] == tweetFrame.iloc[i - 1]['DATE']):#
        print("%d %s", i, tweetFrame.iloc[i]['DATE'])#
        tweetFrame.loc[i - 1, 'favoriteCount'] += tweetFrame.loc[i]['favoriteCount']
        tweetFrame.loc[i - 1,'replyCount'] += tweetFrame.loc[i,  'replyCount']
        tweetFrame.loc[i - 1,'retweetCount'] += tweetFrame.loc[i,  'retweetCount']
        tweetFrame.at[i - 1,'usersMentioned'] += tweetFrame.loc[i, 'usersMentioned']
        tweetFrame.at[i - 1,'text'] += " " + tweetFrame.loc[i,'text']
        tweetFrame.drop(i, inplace=True)
        tweetFrame = tweetFrame.reset_index(drop=True)
        i -= 1

#Add new feautres tp tweet frame
for index,row in tweetFrame.iterrows():
    text = row[3]
    words = text.split()
    numOfCaps = 0
    numOfPunc = 0
    for word in words:
        for letter in word:
            if letter.isalnum() == False:
                numOfPunc += 1
            elif letter == letter.upper():
                numOfCaps += 1
    
    tweetFrame.loc[index, 'Num Of Caps'] = numOfCaps
    tweetFrame.loc[index, 'Num Of Punc'] = numOfPunc
    tweetFrame.loc[index, 'Tweet Length'] = len(words)

tweetFrame.set_index('DATE', inplace=True)

#Read in stock data
tickers = ['AAPL', 'AET', 'AMZN', 'AOBC', 'BA', 'BAC', 'C', 'CAT', 'DIS', 'F', 'FB', 'GM', 'GOOGL', 'GS', 'IBM', 'JPM',
           'KO', 'LMT', 'MMM', 'MRK', 'MS', 'NFLX', 'NKE', 'PFE', 'PG', 'RGR', 'RTN', 'SNAP', 'T', 'TSLA', 'UHS', 
           'UNH', 'UTX', 'VSTO', 'VZ', 'WFC', 'WMT', "XOM"]

pctChange = pd.DataFrame()

for ticker in tickers:
    print(ticker)
    stockData = yf.download(ticker, start='2015-06-16', end='2018-03-30')
    pctChange[ticker] = (stockData['Close']-stockData['Open'])/stockData['Open']
    
for index,row in pctChange.iterrows():
    day = index.day
    month = index.month
    year = index.year
    newDate = datetime(year,month,day)
    pctChange.at[index, 'DATE'] = newDate.strftime('%d-%m-%Y')
    
pctChange.set_index('DATE', inplace=True)

FINAL_DATA = pd.concat([tweetFrame, pctChange], axis=1)
FINAL_DATA.dropna()
