import requests
from datetime import datetime, timedelta
from xml.etree import ElementTree
from statistics import mean


def telegram_bot_sendtext(bot_message):

    bot_token = '965073923:AAFiaucweNmVcqIzZybls59IGZ4Nbc7Be1s'
    bot_chatID = "-356638403"
    # bot_chatID = "573696036"
    send_text = 'https://api.telegram.org/bot' + bot_token + \
        '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()


def epoch_to_date(date, hour=3):
    """
    Convert timestamp to datetime
    """
    return (datetime.utcfromtimestamp(date) + timedelta(hours=hour)).strftime("%d-%m-%Y %H:%M")


def now_local_date():
    """
    Return utc now plus 3 hours to get local time
    """
    return datetime.utcnow() + timedelta(hours=3)


def get_single_stock_target(userId, stockName):
    """
    Get stock target from database
    @return dict {id, name, buyTarget, sellTarget, prevBuyTarget, prevSellTarget}
    """
    QUERY_URL = "http://3.80.155.110/api/portfolio/single"
    res = requests.post(QUERY_URL, json={"name": stockName, "user": userId})
    data = res.json()

    if data == None:
        return {}
    return data


def get_single_stock_special_data(stockName):
    """
    Get stock details from database
    @return dict
    """
    QUERY_URL = "http://3.80.155.110/api/ticker/single"
    res = requests.post(QUERY_URL, json={'name': stockName})
    data = res.json()

    if data == None:
        return {}

    return data


def get_investments_data():
    """
    Get stock details from database
    @return dict
    """
    QUERY_URL = "http://34.67.211.44/api/transaction"
    res = requests.get(QUERY_URL)
    data = res.json()

    if data == None:
        return {}

    return data


def get_current_tickers_data(stockName):
    """
    Get stocks daily data
    @return dict
    """
    QUERY_URL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols={}"
    res = requests.get(QUERY_URL.format(stockName))
    try:
        data = res.json()["quoteResponse"]["result"]
    except KeyError:
        return []

    return data


def get_stock_historic_data(stockName, data_scope, additionalDays=30, interval="1d"):
    """
    Get stocks historic data
    Closes for stocks for X period of day. Additional Y day is needed for RSI calculation
    @return dict
    """
    QUERY_URL = "https://query1.finance.yahoo.com/v7/finance/chart/{}?range={}d&interval={}&indicators=quote&includeTimestamps=false"
    res = requests.get(QUERY_URL.format(
        stockName, data_scope + additionalDays, interval))
    data = res.json()["chart"]["result"][0]['indicators']["quote"][0]['close']

    for i in range(len(data)):  # Handle null values
        if data[i] == None:
            data[i] = data[i-1]

    return data


def get_stock_intraday_data(stockName):
    """
    Get stocks historic data
    Closes for stocks for X period of day. Additional Y day is needed for RSI calculation
    @return dict
    """

    QUERY_URL = 'https://query1.finance.yahoo.com/v7/finance/chart/{}?range=2d&interval=5m&includeTimestamps=false'
    res = requests.get(QUERY_URL.format(stockName))
    data = res.json()["chart"]["result"][0]["indicators"]["quote"][0]["close"]

    for i in range(len(data)):  # Handle null values
        if data[i] == None:
            data[i] = data[i-1]

    return data


def get_non_stock_historic_data(stockName, data_scope):
    """
    Get non-stocks historic data. Ex: GOLD
    Closes for non-stocks for X period of hours. Multiplication with 8 is to get data_scope days.
    @return dict
    """
    QUERY_URL = "https://query1.finance.yahoo.com/v7/finance/chart/{}?range={}d&interval=1h&indicators=quote&includeTimestamps=false"
    res = requests.get(QUERY_URL.format(stockName, (data_scope) + 30))
    data = res.json()["chart"]["result"][0]['indicators']["quote"][0]['close']
    data = data[::8]

    for i in range(len(data)):  # Handle null values
        if data[i] == None:
            data[i] = data[i-1]

    return data


def get_stock_news(stockName):
    """
    Get stocks news from api
    @return list
    """
    all_news = []
    QUERY_URL = "https://feeds.finance.yahoo.com/rss/2.0/headline?s={}&region=US&lang=en-US"
    res = requests.get(QUERY_URL.format(stockName))
    tree = ElementTree.fromstring(res.content)

    for child in tree.iter('item'):
        news = {"title": "", "description": "", "date": ""}
        news["title"] = child[4].text
        news["description"] = child[0].text
        news["date"] = child[3].text

        all_news.append(news)

    return all_news


def calculate_rsi_index(historic_data, data_scope):
    """
    Calculation of RSI index
    """
    rsi_values = []
    historic_data = historic_data[-1 * (data_scope + 14):]
    for i in range(0, data_scope):
        upmoves = []
        downmoves = []
        rsi_closes = historic_data[i:i+15]

        for i in range(len(rsi_closes) - 1):
            diff = rsi_closes[i+1] - rsi_closes[i]
            if diff > 0:
                upmoves.append(diff)
            elif diff < 0:
                downmoves.append(diff * -1)

        AvgU = sum(upmoves) / 14
        AvgD = sum(downmoves) / 14
        try:
            RS = AvgU / AvgD
        except ZeroDivisionError:
            RS = 100

        RSI = (100 - 100 / (1 + RS))
        rsi_values.append(round(RSI, 2))

    return rsi_values


def calculate_env_index(historic_data, data_scope):
    historic_data = historic_data[-1 * (data_scope + 20):]

    env_values = {"upper": [], "lower": []}

    for i in range(0, data_scope):
        try:
            env_data = historic_data[i:i+21]

            data_avg = mean(env_data)
            upper = data_avg + (data_avg * 0.025)
            lower = data_avg - (data_avg * 0.025)

            env_values["upper"].append(upper)
            env_values["lower"].append(lower)
        except:
            pass

    return env_values


def calculate_ninja_index(historic_data, data_scope):
    historic_data = historic_data[-1 * (data_scope + 1):]
    prev = 0
    ninja_values = []
    for i in range(0, len(historic_data)-1):
        try:
            current = (historic_data[i+1] -
                       historic_data[i]) / historic_data[i]

            if current == 0:
                ninja_values.append(round(prev, 2))
            elif (current > 0 and prev > 0) or (current < 0 and prev < 0):
                current += prev
                ninja_values.append(round(current, 2))
            else:
                ninja_values.append(round(current, 2))
            prev = current
        except:
            pass

    return ninja_values


def calculate_ninja_index_s(historic_data, data_scope):
    historic_data = historic_data[-1 * (data_scope + 1):]
    prev = 0
    ninja_values = []
    for i in range(0, len(historic_data)-1):
        try:
            current = (historic_data[i+1] -
                       historic_data[i]) / historic_data[i]

            current += prev
            ninja_values.append(current)
            prev = current
        except:
            pass

    return ninja_values


def calculate_triple_index(historic_data, data_scope):
    first_data = historic_data[-1 * (data_scope + 21):]
    second_data = historic_data[-1 * (data_scope + 14):]
    third_data = historic_data[-1 * (data_scope + 7):]

    triple_index_values = {"first_list": [],
                           "second_list": [], "third_list": []}

    for i in range(0, data_scope):
        try:
            triple_index_values["first_list"].append(mean(first_data[i:i+21]))
            triple_index_values["second_list"].append(
                mean(second_data[i:i+14]))
            triple_index_values["third_list"].append(
                round(mean(third_data[i:i+7]), 2))
        except Exception as ex:
            print(ex)
            pass

    return triple_index_values


def calculate_williams_index(historic_data, data_scope):
    """
    Calculation of Williams index
    """
    williams_values = []
    historic_data = historic_data[-1 * (data_scope + 13):]

    for i in range(0, data_scope):
        closes = historic_data[i:i+13]
        min_value = min(closes)
        max_value = max(closes)

        williams_value = (
            max_value - closes[-1]) / (max_value - min_value + 1) * -100

        williams_values.append(round(williams_value, 2))

    return williams_values


def calculate_aroon_index(historic_data, data_scope):
    """
    Calculation of Aroon index
    """
    aroon_index_values = {"upper": [], "lower": []}
    historic_data = historic_data[-1 * (data_scope + 13):]

    for i in range(0, data_scope):
        closes = historic_data[i:i+14]
        min_value = min(closes)
        max_value = max(closes)

        upper_value = (14 - closes[::-1].index(max_value)) / 14 * 100
        lower_value = (14 - closes[::-1].index(min_value)) / 14 * 100

        aroon_index_values['upper'].append(round(upper_value, 2))
        aroon_index_values['lower'].append(round(lower_value, 2))

    return aroon_index_values


def get_prices(stock_names):
    prices = {}

    QUERY_URL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols={}"

    stock_names = ",".join(stock_names)

    res = requests.get(QUERY_URL.format(stock_names))
    datas = res.json()["quoteResponse"]["result"]

    for data in datas:
        stock_name = data['symbol']
        current_price = data['regularMarketPrice']

        prices[stock_name] = current_price

    return prices


def get_my_stocks():
    res = requests.get("http://34.67.211.44/api/stock")
    data = res.json()

    stocks = []
    for datum in data:
        stocks.append(datum['name'])

    return stocks, data


def rateCalculator(price, prevClose):
    rate = (((price - prevClose) / prevClose) * 100)
    rate = round(rate, 2)

    return rate
