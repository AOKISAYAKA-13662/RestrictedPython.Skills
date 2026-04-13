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
- Restricted Pythonの制約はKyribaのバージョンにより異なります。
  developerスキル内の制約一覧は一般的なものなので、実環境に合わせて調整してください。
- テストはまずローカルPython環境で事前検証し、その後Kyribaテスト環境で最終確認することを推奨します。
