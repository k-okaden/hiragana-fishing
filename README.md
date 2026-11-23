# ひらがな つり

iPad で あそぶ、ひらがなを かいて うみの いきものを つる がくしゅう ゲーム（しさくばん）。

## しくみ

- `src/index.html` … アプリ本体（HTML / CSS / JS 1ファイル）。データは build 時に埋め込み。
- `data/creatures.json` … いきもの ずかんの内容（66しゅるい、さめ 19しゅるい）。
- `data/strokes.json` … ひらがな 46文字の書き順データ（KanjiVG から変換）。
- `data/credits.json` … 写真のライセンス情報（Wikimedia Commons）。
- `data/overrides.json` …（任意）写真を差し替えたいとき `{"id": "File:ファイル名.jpg"}`。
- `data/skip_images.json` …（任意）写真を使わない id の配列（絵文字表示になる）。
- `dist/` … ビルド結果（`index.html` と `img/`）。

## ビルド

```bash
python3 -I tools/kanjivg_to_json.py vendor-raw/kanjivg data/strokes.json   # 書き順データ（取得済みなら不要）
python3 -I tools/fetch_images.py data/creatures.json vendor-raw/images data/credits.json   # 写真を取得
python3 -I tools/build.py   # dist/ を生成
```

ローカルで確認: `python3 -m http.server 8781 --directory dist` → http://localhost:8781

## 書き順の判定

- なぞる: 1画ずつ、次に書く画（みどりの まると矢印）と位置・向きを比べる。順番ちがい・向きちがいはその場で教える。
- みてかく / きいてかく: 「できた！」で文字全体を判定。画数 → 形 → 書き順 → 向き の順に見て、まちがいの種類ごとに声と文字で伝え、書き順アニメを流す。
- 2回まちがえると、その回は「なぞる」に切りかわる。
- 合成した手書き（ゆがみ・ずれ・ゆれ）でのテスト結果: 正解の受け入れ 約97〜99%、ほかの文字との取りちがえ 0件、書き順ちがい・向きちがいの検出 100%。実際の子どもの字での確認はまだ。

## ライセンス

素材ごとにライセンスが分かれています。

| 対象 | ライセンス |
|---|---|
| プログラム（`src/`, `tools/`） | MIT（[LICENSE](LICENSE)） |
| 書き順データ `data/strokes.json` | KanjiVG © Ulrich Apel から変換。CC BY-SA 3.0 |
| 写真 `dist/img/` | 各写真の元のライセンス（CC BY / CC BY-SA / CC0 / パブリックドメイン / KOGL Type 1） |
| 図鑑の文章 `data/creatures.json` | オリジナル（MIT と同じ扱い） |

作者とライセンスの一覧は [CREDITS.md](CREDITS.md) にあります（`tools/build.py` が自動生成）。アプリ内でも「ずかん → しゃしん・データの クレジット」で表示されます。

- 写真を差し替えたり追加したりしたら `tools/build.py` を実行して CREDITS.md を更新すること。
- 取得スクリプトが `WARN artist unclear` と出したときは、Commons のページで本当の作者を確認して `data/credits.json` を直すこと（「self」はアップロードした人が作者、という意味）。
- `vendor-raw/`（ダウンロードした元ファイル）は公開しない（`.gitignore` 済み）。
