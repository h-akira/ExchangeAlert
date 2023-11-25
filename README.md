# Exchange Alert
## 概要
為替の最新の値動きを取得し，ゴールデンクロスまたはデッドクロスが発生し
ている場合にはメール通知を行う．為替データの取得には
`pandas-datareader`を，メールの送信にはGmailAPIを用いる．
## セットアップ

Pythonが利用可能な環境下で本リポジトリをCloneする．
Submoduleを含むので`--recursive`が必要．
```
cd /path/to/任意の場所
git clone --recursive git@github.com:h-akira/ExchangeAlert.git
```
必要に応じて仮想環境を用意したうえで必要なライブラリをインストールする．
```
pip3 install -r requurements.txt
```
GoogleのAPIを用いるため，
[公式ドキュメント](https://developers.google.com/gmail/api/quickstart/python?hl=ja)
を参照して`credentials.json `を得て，それを`secret`ディレクトリに置く．
この過程でGmailAPIを有効にしたうえでスコープには
`.../auth/gmail.modify`
（ユーザー向けの説明が「Gmail アカウントのメールの閲覧、作成、送信」であるもの）
を選択する．

以上が完了したら，`sample/config_sample.json`をもとにして
`config.json`を作成し，それをコマンドライン引数として`bin/alert.py`を
実行することで為替の値動きのチェックとメール通知が行われる．
初回は
`log.txt`が存在しないためそれを作成するかの
問に対し`y`を入力するのと，
googleアカウントへのログインが必要．
```
./bin/alert.py config.json
```
デフォルトでは15分足でチェックするが，`--interval 5m`などとすることで
変更可能．ただし，選択できるのは
"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "1wk", "1mo", "3mo"
のいずれかである．

定期実行したい場合は`cron`等を用いる．時間ちょうど（1時間足で毎時00分など）
に設定するとデータ取得時に最新の値の反映が間に合わない可能性があるため，
`sample/crontab_sample`のように1分ずらすのを推奨する．
なお，同じ理由で`bin/alert.py`では現在時刻をデフォルトでは5秒前として
データ取得している．これは`-p 10`などとして変更可能（単位は秒）．
```
crontab /path/to/crontab
```

