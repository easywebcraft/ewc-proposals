# ewc-proposals — 提案用トップページの見本

営業先ごとに「作り直した場合のトップページ案」を置く。URLを [ewc-crm](https://github.com/easywebcraft/ewc-crm) の
営業リスト（`prospects.proposal_url`）に入れると、営業メールの本文に自動で差し込まれる。

公開先: https://easywebcraft.github.io/ewc-proposals/<会社のID>/

## 守ること

**相手の会社を名乗るページを公開するので、本物と誤認されない作りにする。**

- `<meta name="robots" content="noindex, nofollow, noarchive">` を必ず入れる
- 上部に閉じられない帯で「EasyWebCraftが作成した提案用の見本です。◯◯さまの公式サイトではありません」
- フッターにも同じ断りを書く
- **相手の写真・ロゴ・文章を使わない**（複製になる。しかも本人が見る）
  - 使ってよいのは公開されている事実だけ（社名・所在地・電話・設立年・事業の種類）
  - 文章は自分で書く。写真は使わず、面と余白で構成する
- **問い合わせフォームを置かない**（相手のお客様の個人情報を集めてしまう）
- 電話番号は実際の番号にリンクしてよい（事実であり、相手の利益になる）

## 作り方

自社の実績（`aandk-design` / `kaminote-design` / `salon-sample` など）を業種別の型として使う。
参考にするのは書体・配色・余白の取り方・レイアウトの型で、CSSは自前で書く。

単一HTMLに `<style>` を内包し、外部リソースを参照しない（1ファイルで完結させる）。
**スマートフォンから設計する。** 提案理由が「スマホで読めない」ことなので、見本が
スマホで崩れては話にならない。

## 作り方

`sites.json` に会社ごとの情報を書き、`python3 build.py` で生成する。

**1件ずつ手書きしない。** noindex と「見本です」の帯は絶対に落とせないので、
生成器が必ず付ける形にして書き忘れる余地をなくしている。

```sh
python3 build.py            # 全部
python3 build.py yak-k      # 1つだけ
```

`sites.json` に書くのは**事実**（社名・電話・住所・創業年）と、**自分で書いた文章**だけ。
相手のサイトから文章・写真・ロゴは持ってこない。事実の収集には
`~/kmtools/factfind.py`（電話・住所・創業年だけを拾う）を使う。

## 業種別の型（`build.py` の INDUSTRY）

| 型 | 業種 | 公開しているページ |
|---|---|---|
| `kensetsu` | 建設・住宅・塗装 | `yak-k` `kuniedatoso` `tatsukenhome` |
| `seizo` | 製造・金属加工 | `kg-koketsu` |
| `car` | 自動車整備 | `katoh-auto` |
| `clinic` | クリニック | `watanabe-clinic` |
| `shigyo` | 士業 | `kakamu-tax` |
| `chiryo` | 整体・治療院 | `fulcro` |
| 飲食・カフェ | — | 未（`izakaya-sample` が土台） |
| 美容室・サロン | — | 未（`salon-sample` が土台） |
