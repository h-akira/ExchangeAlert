# Exchange Alert
## 概要
為替の最新の値動きを取得し，ゴールデンクロスまたはデッドクロスが発生し
ている場合にはメール通知を行う．為替データの取得には
`pandas-datareader`を，メールの送信にはGmailAPIを用いる．
## セットアップ
Pythonが利用可能な環境下で本リポジトリをCloneする．
Submoduleを含むので`--recursive`が必要．
```
git clone --recursive git@github.com:h-akira/ExchangeAlert.git
```
