# secret
`credentials.json`, `token.json`, `log.txt`, `error.txt`, `state.txt`を
このディレクトリに置く．
## credentials.json
認証情報が記述されたファイル．
## token.json
ログインすることで得られるトークンファイル．
## log.txt
取得できたレートの最終日時を通貨ペアとともに記録したファイル．
これとの重複を調べることで
週末など市場が閉じているときに
繰り返し通知メールを送信してしまうことを
防止する．
## error.txt
エラーが発生した時にその内容を記録する．
ただし，トークンの有効期限が切れたことによる
`RefreshError`は記録しない．
## state.txt
`alert.py`が複数同時に実行されるのを防止するために状態を記録する．
実行中である場合は`Runnning`，
前回実行時に`RefreshError`が発生した場合は`Expired`，
他のエラーが発生した場合は`Error`，
失敗した場合は`Failed`，
成功した場合は`Successed`
と記録される．
