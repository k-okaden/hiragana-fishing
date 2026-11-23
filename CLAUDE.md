# ひらがな つり — 作業メモ

iPad の Safari で遊ぶ、こども向けのひらがな学習ゲーム。ひらがなを書くと、海の生き物が釣れる。
公開: https://k-okaden.github.io/hiragana-fishing/ (`main` に push すると GitHub Actions で自動公開)

## 返答について
- 返答は、途中経過も含めて、自然な日本語で書く。
- 画面の文字はこども向けにひらがな(+カタカナ)。保護者向けの説明だけは漢字を使ってよい。

## 続きの作業
- やること・やったことは GitHub の issue にまとめてある。閉じた issue(#1〜#9)には、解決ログとして原因・決めたこと・コミットが書いてある。
- 残りは open の issue(#10〜)。作業したら、その issue に何をしたか・確認したことをコメントで残し、終わったら閉じる。

## 構成
- `src/index.html` — アプリ本体(HTML/CSS/JS 1ファイル)。ここを編集する。
- `data/creatures.json` — ずかん(67種類)。`fact` は画面用(ひらがな・分かち書き)、`speak` は読み上げ用(漢字かな交じり)。両方そろえて直す。
- `data/strokes.json` — 書き順データ(KanjiVG から `tools/kanjivg_to_json.py` で変換)。
- `data/credits.json` — 写真の作者・ライセンス。`data/overrides.json` で写真の差し替え先を指定できる。
- `tools/build.py` — データを埋め込んだ `dist/index.html`、縮小した `dist/img/*.jpg`、`CREDITS.md` を作る。
- `dist/` — 公開されるもの。**`src/` や `data/` を変えたら必ず `python3 -I tools/build.py` を実行して `dist/` も一緒にコミットする。**
- `vendor-raw/` — ダウンロードした元ファイル(git に入れない)。

## 動かし方・確かめ方
```bash
python3 -I tools/build.py
python3 -m http.server 8781 --directory dist   # → http://localhost:8781
```
- iPad を想定して、ブラウザを 1180×820(横向き)や 820×1180 にして確認する。
- **ボタンやタップの確認は、実際のクリック・ドラッグで行う。** プログラムから `.click()` すると、透明な画面がタップを横取りしている不具合を見逃す(#7)。
- 書き順判定を変えたら、`tools/recognizer-test.js` をページのコンソールで実行し、取りちがえが 0 のままか確認する。
- 読み上げは `speechSynthesis.speak` を横取りすると、実際に読ませた文を確認できる。

## はまりどころ
- このページは Claude のアーティファクトとしても公開している。アーティファクトでは外側のページが `[hidden]{display:none!important}` などを足すが、GitHub Pages では足されない。必要なものは `src/index.html` に自分で書く。
- 重ねて出す画面は `.overlay`。後から開く画面ほど `z-index` を上にする(もじひょう → 書く画面 で後ろに隠れた)。
- ページが見えていないタブでは `requestAnimationFrame` が動かないので、起動処理は `setTimeout` で行う。
- Wikimedia は短時間に取得しすぎると 429 を返す。`tools/fetch_images.py` は間隔をあけて再試行する。
- Commons の作者名が `self` のときは「アップロードした人が作者」という意味。`Unknown` のときはファイルのページの本文で撮影者を確認する。
- 読み上げにひらがな+スペースの文を渡すと、区切りで止まって不自然になる。読み上げ用の文は漢字かな交じりで書く。生き物の名前はカタカナにして読ませる。

## ライセンス
- プログラム: MIT(`LICENSE`)。書き順データ: KanjiVG、CC BY-SA 3.0。写真: それぞれ元のライセンス(`CREDITS.md`)。
- 写真を追加・差し替えたら、作者名とライセンスを確認し、`tools/build.py` で `CREDITS.md` を更新する。
