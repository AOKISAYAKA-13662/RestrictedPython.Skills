# 変換仕様書

## 1. 概要

- **目的**: SAP支払データをKyriba支払モジュール取り込み用に変換する
- **ERPシステム**: SAP
- **入力ファイル**: `20260219_COM_SAP_dummy_v8.IN.txt`
- **Kyriba取り込み先**: 支払いモジュール（Payments）
- **Restricted Python使用**: あり
- **変換内容の概要**:
  - T行のうち、出金口座コードがKyriba内部コードでBOTK系（col4マッピング後に4文字目からBOTK）かつ取引通貨が特定通貨の場合に2フィールドを設定する

---

## 2. 入力ファイル仕様

- **ファイル名パターン**: `YYYYMMDD_COM_SAP_dummy_vN.IN.txt`
- **形式**: TSV（タブ区切りテキスト）
- **文字コード**: UTF-8
- **ヘッダー行**: なし
- **区切り文字**: タブ（`\t`）
- **レコード種別**: 先頭フィールド（col1）により区別
  - `T` 行: 支払トランザクションヘッダー（処理対象）
  - `D` 行: 支払明細（今回の変換では変更なし）

### T行の入力項目一覧（変換に関係する列のみ）

| col番号 | 項目名 | 型 | 説明 | サンプル値 |
|--------|--------|-----|------|-----------|
| 1 | レコード区分 | 文字 | 常に"T" | `T` |
| 4 | 出金口座コード（ERP） | 文字 | ERPの外部口座コード。マッピング表で変換する | `CO501` |
| 23 | 取引通貨 | 文字 | ISO 3文字通貨コード | `MYR`, `IDR` |
| 24 | 取引金額 | 数値 | 取引通貨建ての支払金額 | `162312.77`, `105006000` |
| 25 | 換算後金額 | 数値 | 変換前は空欄。今回の変換で設定する | `（空欄）` |
| 26 | 換算レート | 数値 | 取引通貨→決済通貨（JPY）の換算レート。空欄の場合あり | `38.98`, `0.0092` |
| 56 | 決済区分 | 数値 | 変換前は存在しない（列数34まで）。今回の変換で設定する | `（なし）` |

> **注意**: 要件記述において「カラム23列目の取引金額」との記載があるが、
> col23はISO通貨コードであり、取引金額は**col24**に格納されている。
> 本仕様書では取引金額 = col24と解釈する。

---

## 3. マッピングテーブル仕様

- **ファイル**: `dummy_bank_accounts.xlsx`
- **用途**: col4（ERP外部コード）→ Kyriba内部口座コードへの変換
- **Kyriba設定**: フリーマッピング表として登録

### マッピング内容

| External code (col4) | Internal code (Kyriba) | 説明 |
|----------------------|------------------------|------|
| CO101 | COMMHCBJPY01 | Mizuho_Branch01_JPY |
| CO102 | COMMHCBJPY02 | Mizuho_Branch01_JPY |
| CO103 | COMMHCBJPY03 | Mizuho_Branch02_JPY |
| CO104 | COMMHCBUSD04 | Mizuho_Branch02_USD |
| CO105 | COMMHCBEUR05 | Mizuho_Branch02_EUR |
| CO106 | COMMHCBAUD06 | Mizuho_Branch02_AUD |
| CO107 | COMMHCBJPY07 | Mizuho_Branch02_JPY |
| CO108 | COMMHCBJPY08 | Mizuho_Branch02_JPY |
| CO109 | COMMHCBCNY09 | Mizuho_Branch02_CNY |
| CO901 | COMSMBCJPY01 | SMBC_Branch01_JPY |
| CO902 | COMSMBCJPY02 | SMBC_Branch02_JPY |
| CO903 | COMSMBCJPY03 | SMBC_Branch03_JPY |
| CO904 | COMSMBCJPY04 | SMBC_Branch04_JPY |
| CO905 | COMSMBCCNY05 | SMBC_Branch01_CNY |
| CO906 | COMSMBCUSD06 | SMBC_Branch01_USD |
| CO907 | COMSMBCEUR07 | SMBC_Branch01_EUR |
| CO908 | COMSMBCGBP08 | SMBC_Branch01_GBP |
| CO909 | COMSMBCAUD09 | SMBC_Branch01_AUD |
| CO501 | COMBOTKJPY01 | MUFG_Branch01_JPY ← **BOTK対象** |
| CO502 | COMBOTKJPY02 | MUFG_Branch02_JPY ← **BOTK対象** |
| CO503 | COMBOTK USD03 | MUFG_Branch01_USD ← **BOTK対象** |
| CO504 | COMBOTKEUR04 | MUFG_Branch01_EUR ← **BOTK対象** |

### BOTK判定ロジック

```
内部口座コード = mapping[col4]
is_botk = (内部口座コード[3:7] == "BOTK")   # 0-indexed、先頭から4文字目が"BOTK"で始まる
```

例:
- `COMBOTKJPY01` → [3:7] = `"BOTK"` → True
- `COMMHCBJPY07` → [3:7] = `"MHCB"` → False
- `COMSMBCJPY01` → [3:7] = `"SMBC"` → False

---

## 4. 変換ルール

### 変換対象の条件

以下の**両方**を満たすT行が変換対象となる:

1. **条件A（BOTK口座）**: col4をマッピング表で変換した内部口座コードの4文字目から7文字目が `"BOTK"` である
2. **条件B（特定通貨）**: col23（取引通貨）が以下のいずれかである
   - `BRL`（ブラジルレアル）
   - `IDR`（インドネシアルピア）
   - `KRW`（韓国ウォン）
   - `MMK`（ミャンマーチャット）
   - `MYR`（マレーシアリンギット）
   - `TWD`（台湾ドル）
   - `VND`（ベトナムドン）

### ルール1: col56 設定（決済区分）

| 項目 | 内容 |
|------|------|
| 対象 | 条件A + 条件B を満たすT行 |
| 設定先 | col56 |
| 設定値 | `2` |
| 補足 | 現在のT行はcol34までしかない。col35〜col55は空文字、col56に`"2"`を設定してタブ区切りで拡張する |

### ルール2: col25 設定（換算後金額）

| 項目 | 内容 |
|------|------|
| 対象 | 条件A + 条件B を満たすT行 |
| 設定先 | col25 |
| 設定値（換算レートあり） | `floor(col24 × col26)` （小数点以下切り捨て） |
| 設定値（換算レート空白） | `floor(col24)` （col24をそのまま切り捨て） |

#### 計算例

| col4 | 内部コード | col23 | col24 | col26 | col25（計算結果） | col56 |
|------|-----------|-------|-------|-------|-----------------|-------|
| CO501 | COMBOTKJPY01 | MYR | 162312.77 | 38.98 | 6326951 | 2 |
| CO501 | COMBOTKJPY01 | IDR | 105006000 | 0.0092 | 966055 | 2 |
| CO501 | COMBOTKJPY01 | MYR | 5000.50 | （空白） | 5000 | 2 |

> **計算詳細（MYRの例）**:
> 162312.77 × 38.98 = 6,326,951.7746... → 切り捨て → 6,326,951

> **計算詳細（IDRの例）**:
> 105006000 × 0.0092 = 966055.2 → 切り捨て → 966055

---

## 5. 処理フロー

```
入力ファイルを1行ずつ読み込む
│
├─ T行かどうか判定（col1 == "T"）
│   │
│   ├─ True: col4をマッピング表で変換 → 内部口座コード取得
│   │         │
│   │         ├─ is_botk = (内部口座コード[3:7] == "BOTK")
│   │         │
│   │         └─ is_botk AND col23 in TARGET_CURRENCIES?
│   │               │
│   │               ├─ True:
│   │               │   ├─ col26が空白の場合: col25 = floor(col24)
│   │               │   ├─ col26が空白でない場合: col25 = floor(col24 × col26)
│   │               │   ├─ col56 = "2"
│   │               │   └─ 行を56列に拡張して出力
│   │               │
│   │               └─ False: 変更なしで出力
│   │
│   └─ False（D行等）: 変更なしで出力
│
出力ファイルに書き込む
```

---

## 6. 出力ファイル仕様

- **ファイル名パターン**: 入力ファイル名と同一（上書き or 別名保存）
- **形式**: TSV（タブ区切り）
- **文字コード**: UTF-8
- **変更点**:
  - 条件を満たすT行: col25に換算後金額、col56に`"2"`を設定（34列→56列に拡張）
  - その他のT行・D行: 変更なし（列数もそのまま）

---

## 7. 例外処理ルール

| ケース | 挙動 |
|--------|------|
| col4がマッピング表に存在しない | その行は変換対象外とし、変更なしで出力する |
| col24（取引金額）が空欄または数値以外 | その行は変換対象外とし、変更なしで出力 |
| col26（換算レート）が空欄 | col25 = floor(col24) を設定する |
| col26が数値以外 | その行は変換対象外とし、変更なしで出力 |
| 入力ファイルが空 | 空の出力ファイルを生成する |

---

## 8. テスト用サンプルデータ

### ケース1: 正常系 — BOTK口座 × MYR（換算レートあり）

**入力（line 116, 抜粋）**:
```
T	INTR	260227P000002730	CO501	TITAN EQUIPMENT MALAYSIA SDN. BHD.	1	MY		...	MYR	162312.77		38.98	20260227	...	2
（col25は空欄、col56は存在しない）
```

**期待出力**:
```
T行col25 = 6326951
T行col56 = 2
```

### ケース2: 正常系 — BOTK口座 × IDR（換算レートあり）

**入力（line 129, 抜粋）**:
```
T	INTR	260227P000002733	CO501	PT KARYA EQUIPMENT INDONESIA	1	ID		...	IDR	105006000		0.0092	20260227	...	2
（col25は空欄、col56は存在しない）
```

**期待出力**:
```
T行col25 = 966055
T行col56 = 2
```

### ケース3: 非対象 — 非BOTK口座 × MYR

**入力（line 110, CO107のMYR行）**:
```
T	INTR	260227P000002728	CO107	... MYR	162312.77		38.98	...
```

**期待出力**: 変更なし（col25は空のまま、col56は設定しない）

### ケース4: 非対象 — BOTK口座 × AUD（特定通貨以外）

**入力**: CO501でcol23 = AUD
**期待出力**: 変更なし

### ケース5: 正常系 — BOTK口座 × MYR（換算レート空白）

**入力**: CO501, col23 = MYR, col24 = 5000.9, col26 = （空白）
**期待出力**: col25 = 5000、col56 = 2

---

## 9. Restricted Pythonの制約事項（開発者向け）

| 制約 | 内容 |
|------|------|
| **関数定義禁止** | `def` 文は使用不可。すべての処理をインラインで記述する |
| **クラス定義禁止** | `class` 文は使用不可 |
| スクリプト構成 | `data = infile.read()` → 変換処理 → `outfile.write(data)` の3ステップ必須 |
| ファイルI/O | `open()`は使用不可。入力は `infile.read()`、出力は `outfile.write()` のみ |
| プリインポート済みモジュール | `ET`, `csv`, `re`, `datetime`, `time`, `collections`, `random`, `hashlib`, `base64`, `json`, `math` |
| 使用可能組み込み関数 | `len`, `range`, `print`, `str`, `list`, `set`, `max`, `reversed`, `slice`, `enumerate`, `any`, `sum` |
| 外部ライブラリ | 不可（`pandas`, `openpyxl`等は使用不可） |
| マッピング表 | スクリプト先頭の `ACCOUNT_MAP` 辞書に定義。内容は `dummy_bank_accounts.xlsx` から引用（外部ファイル参照が不可のため定数として埋め込む） |
| 数値変換 | `math.floor` の代わりに `int()` を使用（正数の小数点切り捨てと同等） |

---

## 10. 変換対象件数（サンプルファイル分析結果）

サンプルファイル `20260219_COM_SAP_dummy_v8.IN.txt` の分析結果:

| 項目 | 件数 |
|------|------|
| 総行数 | 212 行 |
| T行総数 | 47 行 |
| BOTK口座のT行 | - |
| BOTK × 特定通貨のT行（変換対象） | 2 行（line 116: MYR, line 129: IDR） |
