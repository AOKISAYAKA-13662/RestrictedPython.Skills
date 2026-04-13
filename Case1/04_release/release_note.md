# リリースノート

## 基本情報

| 項目 | 内容 |
|------|------|
| リリース名 | COM SAP → Kyriba 支払データ変換スクリプト v1.0 |
| リリース日 | 2026/04/12 |
| 対象ファイル | 02_development/transform_script.py |
| 対象ERP | SAP |
| Kyriba取り込み先 | 支払いモジュール（Payments） |

---

## 変更内容

### 新規作成

SAP出力の支払データ（TSV形式）をKyriba支払モジュールへ取り込む際、
特定通貨建て支払の換算後金額と決済区分を自動設定するRestricted Pythonスクリプトを新規作成。

---

## 機能概要

### 変換対象の条件

以下の**両方**を満たすT行（支払ヘッダー行）に変換を適用する。

**条件A — BOTK系口座**
: col4（ERP外部口座コード）をマッピング表で変換したKyriba内部コードの4〜7文字目が `BOTK`
: 対象口座コード: `CO501`（COMBOTKJPY01）、`CO502`（COMBOTKJPY02）、`CO503`（COMBOTK USD03）、`CO504`（COMBOTKEUR04）

**条件B — 特定通貨**
: col23（取引通貨）が `BRL / IDR / KRW / MMK / MYR / TWD / VND` のいずれか

### 設定される値

| 列 | 設定内容 |
|----|---------|
| col25（換算後金額） | `floor(col24 × col26)`。col26（換算レート）が空欄の場合は `floor(col24)` |
| col56（決済区分） | `2`（固定） |

T行が34列から56列に拡張される（col35〜col55は空文字）。

---

## 適用ファイルとマッピング表

| ファイル | 用途 |
|---------|------|
| `20260219_COM_SAP_dummy_v8.IN.txt` | SAP出力の支払データ（変換元） |
| `dummy_bank_accounts.xlsx` | 口座コードマッピング表（Kyribaフリーマッピング表として登録） |

---

## テスト結果サマリ

| カテゴリ | 件数 | PASS | FAIL |
|---------|------|------|------|
| 正常系 | 13 | 13 | 0 |
| 異常系 | 8 | 8 | 0 |
| 境界値 | 10 | 10 | 0 |
| **合計** | **31** | **31** | **0** |

詳細: [03_test/test_report.md](../03_test/test_report.md)

---

## 注意事項・運用上のポイント

1. **マッピング表の更新**
   口座コードの追加・変更が発生した場合、スクリプト内の `ACCOUNT_MAP` 辞書と
   Kyriba側のフリーマッピング表を**両方**更新すること。

2. **Kyriba環境での最終確認を推奨**
   本スクリプトはローカルPython環境での事前検証済み。
   本番リリース前にKyribaテスト環境での動作確認を実施すること。

3. **支払金額は正数前提**
   `int()` による小数点以下切り捨ては正の数値に対して正しく動作する。
   マイナス金額が発生する場合は挙動を別途確認すること（例: `int(-1.5)` = -1）。

4. **D行（明細行）は変更なし**
   変換処理はT行のみに適用される。D行は一切変更されない。

---

## 成果物一覧

| フェーズ | 成果物 | パス |
|---------|--------|------|
| Phase 1 | 変換仕様書 | [01_design/conversion_spec.md](../01_design/conversion_spec.md) |
| Phase 3 | レビュー結果 | [01_design/review_result.md](../01_design/review_result.md) |
| Phase 2 | 変換スクリプト | [02_development/transform_script.py](../02_development/transform_script.py) |
| Phase 4 | テストシナリオ | [03_test/test_scenarios.md](../03_test/test_scenarios.md) |
| Phase 4 | テスト結果報告書 | [03_test/test_report.md](../03_test/test_report.md) |
| Phase 6 | リリースノート | 本ファイル |
