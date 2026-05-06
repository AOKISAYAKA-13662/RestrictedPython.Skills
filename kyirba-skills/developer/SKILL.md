---
name: developer
description: |
  Kyribaファイル連携のプログラマースキル。
  変換仕様書に基づいてKyribaのRestricted Pythonスクリプトを作成する。
  「スクリプト作成」「コーディング」「Python」「開発」「実装」「修正」と言われたらこのスキルを使う。
  Restricted Pythonの制約を理解し、許可された関数・構文のみでスクリプトを書く。
---

You are helping me write a Restricted Python script for Kyriba file transformation.

# プログラマー（Developer）スキル

## 役割
業務担当者が作成した変換仕様書を読み、KyribaのRestricted Pythonスクリプトとして実装する。

## Restricted Pythonの基本

KyribaのRestricted Pythonは通常のPythonとは異なり、使える機能が厳しく制限されている。
以下の制約を**必ず**守ってスクリプトを書く。

### 使用可能なライブラリ（プリインポート済み）
- `ET` (xml.etree.ElementTree)
- `csv`
- `re`
- `datetime`
- `time`
- `collections`
- `random`
- `hashlib`
- `base64`
- `json`
- `math`

### 使用可能な組み込み関数
`len`, `range`, `print`, `str`, `list`, `set`, `max`, `reversed`, `slice`, `enumerate`, `any`, `sum`

### 使用可能なデータ型・制御構文
- 基本型: str, int, float, list, dict, tuple, bool
- 制御構文: if/elif/else, for, while, break, continue
- 文字列操作: split, join, strip, replace, upper, lower, startswith, endswith, find
- リスト操作: append, extend, insert, pop, sort, reverse, index
- 辞書操作: keys, values, items, get, update
- 型変換: str(), int(), float(), bool()
- 文字列フォーマット: f-string, format(), %演算子

### **禁止事項（厳守）**
- **関数定義禁止**: `def` 文は使用不可
- **クラス定義禁止**: `class` 文は使用不可
- ファイルI/O（open, read, write）→ Kyribaが `infile` / `default_out` で管理（**`outfile` は存在しない**）
- exec, eval, compile
- os, sys, subprocess等のシステム関連
- ネットワーク関連

### スクリプト構成（必須の流れ）
スクリプトは必ず以下の3ステップ構成に従う:

```
1. data = infile.read()          # Kyribaから入力データを受け取る
2. （変換処理）                   # データを加工・変換する
3. default_out.write(data)       # Kyribaへ出力データを渡す（outfile ではなく default_out）
```

> **重要**: 出力に使う変数は `outfile` ではなく **`default_out`**。
> `outfile` はKyriba Restricted Python環境に存在しないため、スクリプトがエラーになる。

## スクリプト開発手順

### Step 1: 変換仕様書の読み込み
`01_design/conversion_spec.md` を読み、以下を把握する:
- 入力ファイルの構造
- 出力ファイルの構造
- 変換ルール一覧
- 例外処理ルール

### Step 2: スクリプトの設計
仕様書の変換ルールをコードに落とし込む前に、処理の流れを整理する:

```
1. 入力データの受け取り（Kyribaが渡すデータ構造に依存）
2. ヘッダー処理（必要に応じて）
3. 行ごとのループ処理
   3a. フィルタリング（対象外の行をスキップ）
   3b. 各項目の変換
   3c. バリデーション（例外処理）
   3d. 出力行の組み立て
4. 出力データの返却
```

### Step 3: スクリプトの実装

以下のテンプレートに沿ってスクリプトを作成する（**def/class は一切使わない**）:

```python
# ============================================
# Kyriba Restricted Python - ファイル変換スクリプト
# 概要: [変換の概要を記載]
# 仕様書: 01_design/conversion_spec.md
# 作成日: YYYY/MM/DD
# ============================================

# --- Step 1: 入力データ受け取り ---
data = infile.read()

# --- 定数定義 ---
# コード変換マッピング等をここに定義
CODE_MAP = {
    "入力値1": "出力値1",
    "入力値2": "出力値2",
}

# --- Step 2: 変換処理 ---
output_lines = []
error_log = []

# \r\n (Windows) と \r (旧Mac) を \n に統一してから行分割（改行コード正規化は必須）
lines = data.replace("\r\n", "\n").replace("\r", "\n").split("\n")
for row_index, line in enumerate(lines):
    # 空行は先にスキップ（split前に行う。splitすると空リストになり cols[0] でエラーになる）
    if line == "":
        output_lines.append(line)
        continue

    # フィールド分割（CSV形式の例）
    fields = line.split(",")

    # --- フィルタリング ---
    # 仕様書のフィルタリングルールに基づいて対象外の行をスキップ
    # 例: if fields[0] == "H":  # ヘッダー行をスキップ
    #         continue

    # --- バリデーション ---
    # 必須項目チェック（defが使えないのでインラインで記述）
    # 例:
    # field_取引日 = fields[1].strip()
    # if field_取引日 == "":
    #     error_log.append(f"行{row_index}: 取引日が空です")
    #     continue

    # --- 変換処理 ---
    output_row = []

    # 出力項目1: [項目名]
    # 変換ルール: [仕様書のルール番号と内容]
    # output_row.append(変換後の値)

    # 出力項目2: [項目名]
    # output_row.append(変換後の値)

    # ... 項目の数だけ繰り返す

    output_lines.append(",".join(output_row))

# 出力文字列を組み立て
data = "\n".join(output_lines)

# --- Step 3: 出力 ---
# 必須: outfile ではなく default_out を使うこと
default_out.write(data)
```

### Step 4: コメントの記載
スクリプト内に以下を必ず記載する:
- 各変換処理と仕様書のルール番号の対応
- 変換ロジックの入出力例（コメントとして）
- 例外処理の挙動説明

## 修正対応

レビューやテストで修正依頼が来た場合:
1. 修正依頼内容を確認
2. 該当箇所を特定
3. 修正を実施
4. 修正箇所にコメントで修正理由を記載
5. 修正前後の動作の違いを説明

## 成果物
- `02_development/transform_script.py` にスクリプトを保存
- 修正版は同じファイルを更新（Gitで管理されている想定）

## よくある変換パターン

**注意**: def/class は禁止。すべてインラインで記述する。

### 日付変換（文字列操作）
```python
# YYYYMMDD -> YYYY/MM/DD
d = fields[2]  # 例: fields[2] が日付列
date_slash = d[0:4] + "/" + d[4:6] + "/" + d[6:8]

# YYYYMMDD -> YYYY-MM-DD
date_hyphen = d[0:4] + "-" + d[4:6] + "-" + d[6:8]

# MM/DD/YYYY -> YYYYMMDD
parts = d.split("/")
date_compact = parts[2] + parts[0] + parts[1]
```

### 日付変換（datetimeモジュール使用）
```python
# datetimeはプリインポート済み
# YYYYMMDD -> YYYY/MM/DD
d = fields[2]
dt = datetime.datetime.strptime(d, "%Y%m%d")
date_slash = dt.strftime("%Y/%m/%d")
```

### 金額変換
```python
# 文字列 -> 小数点2桁の金額文字列
val = fields[3]
num = float(val)
integer_part = int(num * 100)
amount_str = str(integer_part // 100) + "." + str(integer_part % 100).zfill(2)
```

### 固定長データの分割
```python
# 固定長レコードをフィールドに分割（def不使用）
WIDTHS = [10, 8, 20, 12]  # 各フィールドの幅
fields = []
pos = 0
for w in WIDTHS:
    fields.append(line[pos:pos+w].strip())
    pos += w
```

### コード変換（辞書マッピング）
```python
CODE_MAP = {"01": "USD", "02": "JPY", "03": "EUR"}
raw_code = fields[4].strip()
converted_code = CODE_MAP.get(raw_code, "")  # マップにない場合は空文字
```

### CSVパース（csvモジュール使用）
```python
# csv はプリインポート済み。import文は不要（import自体も禁止）
# io.StringIO は使えないため、行ごとに csv.reader を使う
lines = data.replace("\r\n", "\n").replace("\r", "\n").split("\n")
for line in lines:
    if line == "":
        continue
    # csv.reader に1行ずつ渡す場合はリストでラップする
    for row in csv.reader([line]):
        # row はフィールドのリスト
        pass
```
