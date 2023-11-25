#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Created: 2023-11-25 14:12:18

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../lib")
from  google_api_operator.authentication import get_service
from google_api_operator.gmail import send_mail
import json
import datetime
from pytz import timezone
import pandas_datareader.data as web
import yfinance as yf
yf.pdr_override()

def parse_args():
  import argparse
  parser = argparse.ArgumentParser(description="""\

""", formatter_class = argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("--version", action="version", version='%(prog)s 0.0.1')
  parser.add_argument(
    "--interval",
    metavar="interval",
    choices=["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "1wk", "1mo", "3mo"],
    default="15m", 
    help="interval"
  )
  parser.add_argument("-p", "--plenty", metavar="seconds", type=int, default=5, help="現在時刻を何秒前とするか")
  parser.add_argument("-o", "--output", metavar="output-file", default="output", help="output file")
  parser.add_argument("--log", metavar="log-file", default=os.path.join(os.path.dirname(__file__), "../secret/log.txt"), help="output file")
  parser.add_argument("-t", "--token", metavar="Path", default=os.path.join(os.path.dirname(__file__),"../secret/token.json"), help="token.json（存在しない場合は生成される）")
  parser.add_argument("-c", "--credentials", metavar="Path", default=os.path.join(os.path.dirname(__file__),"../secret/credentials.json"), help="credentials.json（client_secret_hogehoge.json）")
  parser.add_argument("-r", "--re-authenticate", action="store_true", help="token.jsonを削除して再認証する")
  parser.add_argument("-s", "--service", action="store_true", help="通知メールを送信しない場合でもtokenが有効かどうか確認のためserviceを取得する")
  parser.add_argument("file", metavar="json-file", help="json file")
  options = parser.parse_args()
  if not os.path.isfile(options.file): 
    raise Exception("The json file does not exist.") 
  if not os.path.isfile(options.credentials):
    raise Exception("The credentials file does not exist.")
  if not os.path.isfile(options.log):
    if "y" == input(f"The log file `{options.log}` does not exist. \nCreate it? [y/other] : "):
      with open(options.log, mode="w") as f:
        f.write("")
    else:
      options.log = None
  if os.path.isfile(options.token) and options.re_authenticate:
    print(f"Delete `{options.token}` to re-authenticate.")
    os.remove(options.token)
  return options

def cross_checker(df, long=20, short=9, inclination=False):
  df["long"] = df["Close"].rolling(window=long).mean()
  df["short"] = df["Close"].rolling(window=short).mean()
  df["long_delta"] = df["long"].diff()
  df["short_delta"] = df["short"].diff()
  if df["long"].iloc[-1] > df["short"].iloc[-1] and df["long"].iloc[-2] < df["short"].iloc[-2]:
    dead=True
  else:
    dead=False
  if df["long"].iloc[-1] < df["short"].iloc[-1] and df["long"].iloc[-2] > df["short"].iloc[-2]:
    golden=True
  else:
    golden=False
  if df["long_delta"].iloc[-1] > 0:
    long_increasing = True
  else:
    long_increasing = False
  if df["short_delta"].iloc[-1] > 0:
    short_increasing = True
  else:
    short_increasing = False
  if golden:
    if long_increasing and short_increasing:
      return "golden cross (both inclination value are positive)"
    else:
      if inclination:
        return None
      else:
        return "golden cross"
  elif dead:
    if not long_increasing and not short_increasing:
      return "dead cross (both inclination value are negative))"
    else:
      if inclination:
        return None
      else:
        return "dead cross"
  else:
    return None

def main():
  options = parse_args()
  config = json.load(open(options.file))
  if options.log:
    with open(options.log, mode="r") as f:
      log = f.readlines()
  end = datetime.datetime.now(timezone(config["yfinance"]["timezone"]))-datetime.timedelta(seconds=options.plenty)
  if "m" in options.interval or options.interval == "1h":
    start = end-datetime.timedelta(days=6)
  elif options.interval == "1d":
    start = end-datetime.timedelta(days=40)
  elif options.interval == "1wk":
    start = end-datetime.timedelta(days=180)
  elif options.interval == "1mo":
    start = end-datetime.timedelta(days=365*2)
  elif options.interval == "3mo":
    start = end-datetime.timedelta(days=365*6)
  message = "=== Exchange Alert ==="
  send = False
  for ticker in config["yfinance"]["tickers"]:
    print("ticker: {}".format(ticker))
    pair = ticker[:3]+"/"+ticker[3:6]
    df = web.get_data_yahoo(
      tickers=ticker,
      start=start,
      end=end,
      interval=options.interval
    )
    latest = df.index[-1]
    if options.log:
      if f"{pair}: {latest}\n" in log:
        print("skip")
        continue
      else:
        with open(options.log, mode="a") as f:
          f.write(f"{pair}: {latest}\n")
    cross = cross_checker(
      df,
      long=config["checker"]["cross"]["period"]["long"],
      short=config["checker"]["cross"]["period"]["short"],
      inclination=config["checker"]["cross"]["inclination"]
    )
    if cross:
      send = True
      message += "\n{}: {}".format(pair, cross)
  
  # send mail
  if send or not os.path.isfile(options.token) or options.service:
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    service = get_service(
      SCOPES, 
      options.credentials,
      options.token,
      "gmail",
      "v1",
      if_RefreshError=True
    )
    if send:
      args = {
        "service": service,
        "Subject": "Exchange Alert",
        "Message": message,
      }
      if config["mail"]["To"]:
        args["To"] = config["mail"]["To"]
      if config["mail"]["Bcc"]:
        args["Bcc"] = config["mail"]["Bcc"]
      send_mail(**args)
      print("Sent mail. Message is below.")
      print(message)

if __name__ == '__main__':
  main()
