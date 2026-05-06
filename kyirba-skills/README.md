# Kyribaファイル変換プロジェクト - スキルセット

## 概要
ERPからKyribaへのファイル連携で使うRestricted Pythonスクリプトを、
設計→開発→テストの流れで作るためのClaude Code用スキルセットです。

## スキル構成

```
kyirba-skills/
├── pm/                    # PMスキル（全体統括）
│   └── SKILL.md
├── business-analyst/      # 業務担当者スキル（仕様書作成・レビュー）
│   └── SKILL.md
├── developer/             # プログラマースキル（スクリプト開発）
│   └── SKILL.md
└── tester/                # テスト担当者スキル（テスト設計・実施）
    └── SKILL.md
```

## セットアップ方法

### 1. スキルフォルダをプロジェクトに配置
このフォルダをプロジェクトのルートに置きます。

### 2. Claude Codeの設定にスキルを登録
プロジェクトの `.claude/settings.json` に以下を追加します:

```json
{
  "skills": [
    "kyirba-skills/pm/SKILL.md",
    "kyirba-skills/business-analyst/SKILL.md",
    "kyirba-skills/developer/SKILL.md",
    "kyirba-skills/tester/SKILL.md"
  ]
}
```

または、`.claude/commands/` にカスタムコマンドとして登録することもできます。

## 使い方（Claude Codeへの指示例）

### プロジェクト全体を開始する場合
```
PMスキルを使って、ERPからKyribaへの支払いデータ変換プロジェクトを開始してください。
ERPはSAPで、CSV形式のファイルをKyribaの支払いモジュールに取り込みます。
```

### 各フェーズを個別に実行する場合

#### Phase 1: 仕様書作成
```
business-analystスキルを使って、以下の変換仕様書を作成してください。
- 入力: SAPからの支払いCSV（日付、取引先コード、金額、通貨の4列）
- 出力: Kyribaの支払い取り込みフォーマット
- 変換: 日付をYYYYMMDD→YYYY/MM/DDに変換、通貨コードを数字→ISO文字列に変換
```

#### Phase 2: スクリプト開発
```
developerスキルを使って、01_design/conversion_spec.md の変換仕様書に基づいて
Restricted Pythonスクリプトを作成してください。
```

#### Phase 3: レビュー
```
business-analystスキルを使って、02_development/transform_script.py が
01_design/conversion_spec.md の仕様に適合しているかレビューしてください。
```

#### Phase 4: テスト
```
testerスキルを使って、以下のテストを実施してください。
- 仕様書: 01_design/conversion_spec.md
- スクリプト: 02_development/transform_script.py
正常系・異常系・境界値の全カテゴリでテストシナリオを作成し、テストしてください。
```

## 成果物ディレクトリ構成
プロジェクト実行後、以下の構成で成果物が生成されます:

```
project/
├── 01_design/
│   ├── conversion_spec.md        # 変換仕様書
│   └── review_result.md          # レビュー結果
├── 02_development/
│   └── transform_script.py       # Restricted Pythonスクリプト
├── 03_test/
│   ├── test_scenarios.md         # テストシナリオ
│   ├── test_data/
│   │   ├── input_normal.csv
│   │   ├── input_error.csv
│   │   ├── input_boundary.csv
│   │   ├── expected_normal.csv
│   │   ├── expected_error.csv
│   │   └── expected_boundary.csv
│   └── test_report.md            # テスト結果報告
└── 04_release/
    └── release_note.md           # リリースノート
```

## 注意事項

### Kyriba Restricted Pythonの重要ルール（実環境で確認済み）

| ルール | 内容 |
|--------|------|
| **出力ハンドラ** | `default_out.write(data)` を使用。`outfile` は存在しない（致命的エラーになる） |
| **入力ハンドラ** | `data = infile.read()` で全テキストを取得する |
| **関数定義禁止** | `def` 文は使用不可。すべての処理をスクリプトのトップレベルにインラインで記述する |
| **クラス定義禁止** | `class` 文は使用不可 |
| **import禁止** | `import` 文は不要（モジュールはプリインポート済み）かつ禁止 |
| **改行コード正規化** | `data.replace("\r\n","\n").replace("\r","\n").split("\n")` で統一してから行分割する |
| **空行処理** | `line.split("\t")` の**前**に `if line == "": continue` でスキップする |

### スクリプトの必須フォーマット

```python
# --- Step 1: 入力 ---
data = infile.read()

# --- Step 2: 変換処理 ---
lines = data.replace("\r\n", "\n").replace("\r", "\n").split("\n")
output_lines = []
for line in lines:
    if line == "":
        output_lines.append(line)
        continue
    # ... 変換ロジック ...
data = "\n".join(output_lines)

# --- Step 3: 出力 ---
default_out.write(data)   # ← outfile ではなく default_out
```

- developerスキル内の制約一覧は実環境での確認を経て更新済みです。
- テストはまずローカルPython環境で事前検証し、その後Kyribaテスト環境で最終確認することを推奨します。
