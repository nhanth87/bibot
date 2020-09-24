import ccxt
import time
import operator
import datetime
import math

binance = ccxt.binance(
    {
        'apiKey': 'your api key',
        'secret': 'your token',
        'enableRateLimit': True

}
)

start_price = 0
end_price = 0
first_run = True
start_time = datetime.datetime.now()
end_time = 0

money = 0.0
stored_tong_bid = 100000
stored_tong_asks = 0

gia_da_mua = 0
first_bid = False
da_mua = False

count_loi = 0
count_lo = 0
tong_tien_loi = 0
check_gia_sau_300_secs = 0

print(" my order book LINK/USDT")


def getDataBinance(order_json):
    tong_10 = 0
    tong_20 = 0
    tong = 0

    loop_count = 0
    for i in order_json:
        loop_count += 1
        tong += i[1]

        if loop_count < 10:
            tong_10 += i[1]
        if loop_count < 20:
            tong_20 += i[1]

    return tong, tong_10, tong_20

def round_down(n, decimals=5):
    multiplier =  10 ** decimals

    return math.floor(n * multiplier) / multiplier


def printTopValue(order_json):
    global first_run

    global money
    global stored_tong_asks
    global stored_tong_bid

    global count_loi
    global count_lo

    global first_bid
    global gia_da_mua
    global da_mua
    global tong_tien_loi
    global binance
    global check_gia_sau_300_secs

    balance_btc = 0
    balance_usdt = 0

    params = {
        'test': False,  # test if it's valid, but don't actually place it
    }

    ### calculating money
    while True:
        try:
            balance_btc = round_down(binance.fetch_balance()['BTC']['free'] - binance.fetch_balance()['BTC']['free']*0.1/100)
            balance_usdt = round_down(binance.fetch_balance()['USDT']['free'] - binance.fetch_balance()['USDT']['free']*0.1/100)
            print(str(balance_btc))
            print(str(balance_usdt))
            break
        except:
            print('some bug when get balance')
            continue

    order_json_bids = sorted(order_json["bids"], key=operator.itemgetter(0))
    order_json_asks = sorted(order_json["asks"], key=operator.itemgetter(0))

    if first_run:
        global start_price
        global start_time
        start_price = order_json_asks[0][0]

        first_run = False

    else:
        global end_price
        global end_time
        end_price = order_json_asks[0][0]
        end_time = order_json["timestamp"]

    tong_bid_100, tong_bid_10, tong_bid_20 = getDataBinance(order_json_bids)
    tong_ask_100, tong_ask_10, tong_ask_20 = getDataBinance(order_json_asks)

    s2 = "ask min: - " + str(order_json_asks[0][0]) + "\t\t\t ask max: - " + str(order_json_asks[9][0]) + "\t\t\t Tổng ask 10: - " + str("{:,}".format(tong_ask_10)) + "\t\t\t\t\t Tổng ask 20: - " + str(
        "{:,}".format(tong_ask_20)) +  "\t\t\t\t\t Tổng ask 100: - " + str("{:,}".format(tong_ask_100))
    s = "bid min: - " + str(order_json_bids[99][0]) + "\t\t\t bid max: - " + str(order_json_bids[89][0]) + "\t\t\t Tổng bid 10: - " + str("{:,}".format(tong_bid_10)) + "\t\t\t\t\t Tổng bid 20: - " + str(
        "{:,}".format(tong_bid_20)) + "\t\t\t\t\t Tổng bid 100: - " + str("{:,}".format(tong_bid_100))



    bid = order_json['bids'][0][0] if len(order_json['bids']) > 0 else None
    ask = order_json['asks'][0][0] if len(order_json['asks']) > 0 else None

    spread = (ask - bid) if (bid and ask) else None
    market_price = {
        'bid': bid,
        'ask': ask,
        'spread': spread
    }

    print("market price: " + str(market_price))

    print(s2)
    print(s)
    print("")
    print("stored_tong_ban =" + str("{:,}".format(stored_tong_asks)))
    print("stored_tong_mua =" + str("{:,}".format(stored_tong_bid)))

    if first_bid is True:
        # swap - FIXME: khong mua ban trong candle dau tien
        stored_tong_bid = 100000
        stored_tong_asks = 0
        first_bid = False

    if da_mua == False:
        if (check_gia_sau_300_secs > order_json_bids[89][0]):
            print("gia dang down, khong mua")

            if check_gia_sau_300_secs > 0:
                check_gia_sau_300_secs = (check_gia_sau_300_secs + order_json_bids[89][0])/2  #2 candle
            else:
                check_gia_sau_300_secs = order_json_bids[89][0]
        else:
            if (round(stored_tong_bid*2) < tong_bid_20):

                gia_da_mua = order_json_bids[89][0]
                print("mua, gia: " + str(order_json_asks[9][0]))
                da_mua = True
                money = 0
                ###place order
                type = 'market'  # or 'market'
                side = 'buy'  # or 'buy'
                amount = round_down( balance_usdt/gia_da_mua)


                buy_id = binance.create_order('BTC/USDT', type, side, amount,price=None)
                print("buy_id = " + str(buy_id))
            else:
                print("khong mua")
    else:
        if (round(stored_tong_asks) + 0.2 > round(tong_ask_20 + tong_ask_20 * 0.2)):
            print("khong ban")
        else:
            print("ban gia market" + str(order_json_bids[89][0]))
            da_mua = False
            type = 'market'  # or 'market'
            side = 'sell'  # or 'buy'
            amount = round_down(balance_btc)

            sell_id = binance.create_order('BTC/USDT', type, side, amount,price=None)
            print("sell_id = " + str(sell_id))

            check_gia_sau_300_secs = (check_gia_sau_300_secs + order_json_bids[89][0])/2 # 2 candles

    stored_tong_bid = tong_bid_20
    stored_tong_asks = tong_ask_20

    print("tong_tien_loi =" + str("{:,}".format(tong_tien_loi)))


### Main code ###
while True:
    try:
        binance_markets = binance.load_markets()
        break
    except:
        print("trying to load market")
        continue

while True:
    ### try catch o day
    try:
        order_json = binance.fetch_l2_order_book('BTC/USDT')

    except:
        print("some bug")
        continue

    st = datetime.datetime.now()
    print("\n******   ****** - " + str(st))
    printTopValue(order_json)

    try:
        st = 300 - (datetime.datetime.now() - st).total_seconds()
        time.sleep(st)
    except KeyboardInterrupt:
        time.sleep(2)
        print("\nclear all orders and exit")
        sdate = start_time
        edate = datetime.datetime.now()
        print("start time: " + str(sdate) + " - end time: " + str(edate) + " - chênh lệch: " + str(edate - sdate))
        print("start price: " + str(start_price) + " - end price: " + str(end_price))
        if start_price < end_price:
            print("thị trường lên:  " + str("{:.8f}".format(end_price - start_price)))
        else:
            print("thị trường xuống: " + str("{:.8f}".format(start_price - end_price)))

        print("done!!!")

        exit()
