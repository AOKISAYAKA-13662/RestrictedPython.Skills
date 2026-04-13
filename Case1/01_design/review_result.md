# スクリプトレビュー結果

## レビュー日: 2026/04/12（改訂版）
## レビュー対象: 02_development/transform_script.py

## 結果サマリ: OK

---

## 改訂履歴

| 版 | 日付 | 内容 |
|----|------|------|
| v1 | 2026/04/12 | 初版（def/class使用版） |
| v2 | 2026/04/12 | Restricted Python制約対応: def/class禁止 → インライン実装に全面書き直し |

---

## 詳細

### OK項目

1. **Restricted Python制約への完全準拠（v2追加）**
   - `def` 文なし ✅（全ロジックをインラインに展開）
   - `class` 文なし ✅
   - スクリプト構成が `data = infile.read()` → 変換処理 → `outfile.write(data)` の3ステップ ✅
   - `open()` なし（`infile`/`outfile` のみ使用）✅
   - プリインポートモジュール（`re`等）のみ利用、`import` 文なし ✅

2. **条件A（BOTK口座判定）**
   - `ACCOUNT_MAP.get(account_code, "")` で内部コードを取得
   - `internal_code[3:7] == "BOTK"` で正しく判定（0-indexed、仕様書 §3 と一致）
   - BOTK対象: CO501〜CO504 のみ。CO1xx / CO9xx は非対象

3. **条件B（特定通貨チェック）**
   - `TARGET_CURRENCIES = {"BRL","IDR","KRW","MMK","MYR","TWD","VND"}` として7通貨を網羅

4. **ルール2: col25 換算後金額の計算**
   - `int(float(amount) * float(rate))` で小数点以下切り捨てを実装
   - 換算レート空白時は `int(float(amount))` のみで計算
   - サンプルデータでの検証:
     - MYR: `int(162312.77 × 38.98)` = **6,326,951** ✅
     - IDR: `int(105006000 × 0.0092)` = **966,055** ✅

5. **ルール1: col56 = "2" の設定**
   - `cols[IDX_PAYMENT_TYPE] = "2"` で設定（index=55 = col56）✅
   - 現在34列のT行を56列に拡張してから設定（`while len(cols) < 56: cols.append("")`）✅

6. **D行・非対象T行の不変性**
   - T行以外は早期 `continue` で変更なしにパス
   - BOTK以外の口座（CO107, CO901等）のT行も変更なし
   - AUD/USD/GBP等の特定通貨以外のT行も変更なし
   - ローカル検証: 212行 → 212行（全行一致、変換対象外行の改変なし）✅

7. **例外処理（def不使用でインライン実装）**
   - マッピング不在の口座コード → `ACCOUNT_MAP.get()` が `""` を返しBOTK判定False → 変更なし
   - col24が空欄/非数値 → `.replace(".", "", 1).isdigit()` がFalse → 変更なし
   - col26が非数値 → `.replace(".", "", 1).isdigit()` がFalse → 変更なし
   - col26が空欄 → `rate_is_blank = True` として `int(float(amount))` のみ計算

8. **出力形式の保持**
   - タブ区切りで再結合 ✅
   - `\r\n`/`\r` の統一処理あり（Windows・旧Macファイル対応）✅
   - 総行数が入出力で一致（212行 → 212行）✅

---

### NG項目（修正依頼）

なし

---

### 確認事項（ユーザーへ）

1. **`int()` による切り捨て挙動**
   今回 `math.floor` の代わりに `int()` を使用。
   支払金額・換算レートは正数のみという前提で設計（正数では `int()` と `floor()` の結果は同等）。
   負の値が渡された場合は結果が異なるため、Kyriba環境で問題ないか確認を推奨。

2. **マッピング表の更新運用**
   口座コードの追加・変更時はスクリプト先頭の `ACCOUNT_MAP` 辞書を手動更新。
   Kyriba側のフリーマッピング表と乖離しないよう変更管理を徹底すること。

3. **`isdigit()` の利用可能性**
   数値バリデーションに `str.isdigit()` メソッドを使用している。
   Kyribaの Restricted Python 環境でこのメソッドが利用可能か、本番適用前に確認を推奨。
