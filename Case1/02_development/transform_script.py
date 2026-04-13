# ============================================
# Kyriba Restricted Python - ファイル変換スクリプト
# 概要: SAP支払データ(TSV) → Kyriba支払モジュール取り込み用変換
#       BOTK口座 × 特定通貨のT行に対し col25(換算後金額) と col56(決済区分=2) を設定する
# 仕様書: 01_design/conversion_spec.md
# 作成日: 2026/04/12
# 改訂: def/class禁止のRestricted Python制約対応（インライン実装に変更）
# ============================================

# ==============================================
# 【マッピング設定】
# 出典: dummy_bank_accounts.xlsx（Kyriba フリーマッピング表）
# 口座コードの追加・変更時はこのセクションのみ更新すること
# ==============================================
ACCOUNT_MAP = {
    "CO101": "COMMHCBJPY01",
    "CO102": "COMMHCBJPY02",
    "CO103": "COMMHCBJPY03",
    "CO104": "COMMHCBUSD04",
    "CO105": "COMMHCBEUR05",
    "CO106": "COMMHCBAUD06",
    "CO107": "COMMHCBJPY07",
    "CO108": "COMMHCBJPY08",
    "CO109": "COMMHCBCNY09",
    "CO901": "COMSMBCJPY01",
    "CO902": "COMSMBCJPY02",
    "CO903": "COMSMBCJPY03",
    "CO904": "COMSMBCJPY04",
    "CO905": "COMSMBCCNY05",
    "CO906": "COMSMBCUSD06",
    "CO907": "COMSMBCEUR07",
    "CO908": "COMSMBCGBP08",
    "CO909": "COMSMBCAUD09",
    "CO501": "COMBOTKJPY01",
    "CO502": "COMBOTKJPY02",
    "CO503": "COMBOTK USD03",
    "CO504": "COMBOTKEUR04",
}

# 特定通貨リスト (仕様書 §4 条件B)
TARGET_CURRENCIES = {"BRL", "IDR", "KRW", "MMK", "MYR", "TWD", "VND"}

# カラムインデックス (0始まり)
IDX_RECORD_TYPE = 0   # col1:  レコード区分
IDX_ACCOUNT_CODE = 3  # col4:  ERP外部口座コード
IDX_TRX_CURRENCY = 22 # col23: 取引通貨
IDX_TRX_AMOUNT   = 23 # col24: 取引金額
IDX_CONV_AMOUNT  = 24 # col25: 換算後金額（設定対象）
IDX_RATE         = 25 # col26: 換算レート
IDX_PAYMENT_TYPE = 55 # col56: 決済区分（設定対象）
OUTPUT_COL_COUNT = 56  # 出力列数（条件一致T行のみ56列に拡張）


# --- Step 1: 入力データ受け取り ---
data = infile.read()


# --- Step 2: 変換処理 ---
# \r\n (Windows) と \r (旧Mac) を \n に統一してから行分割
lines = data.replace("\r\n", "\n").replace("\r", "\n").split("\n")
output_lines = []

for line in lines:
    cols = line.split("\t")

    # T行以外（D行等）は変更なしでそのまま出力
    # 例: D行、空行 → スキップして原文出力
    if not cols or cols[IDX_RECORD_TYPE] != "T":
        output_lines.append(line)
        continue

    # --- 条件A: BOTK口座チェック (仕様書 §4 条件A) ---
    # col4のERP外部コードをマッピング表で変換し、内部コードの[3:7]が"BOTK"かを判定
    # 例: CO501 → COMBOTKJPY01 → [3:7]="BOTK" → True
    #     CO107 → COMMHCBJPY07 → [3:7]="MHCB" → False
    account_code = cols[IDX_ACCOUNT_CODE] if len(cols) > IDX_ACCOUNT_CODE else ""
    internal_code = ACCOUNT_MAP.get(account_code, "")
    is_botk = (len(internal_code) >= 7 and internal_code[3:7] == "BOTK")

    if not is_botk:
        # 非BOTK口座 → 変更なし
        output_lines.append(line)
        continue

    # --- 条件B: 特定通貨チェック (仕様書 §4 条件B) ---
    # col23が BRL/IDR/KRW/MMK/MYR/TWD/VND のいずれかか判定
    trx_currency = cols[IDX_TRX_CURRENCY] if len(cols) > IDX_TRX_CURRENCY else ""
    if trx_currency not in TARGET_CURRENCIES:
        # 特定通貨以外（USD/AUD/EUR等）→ 変更なし
        output_lines.append(line)
        continue

    # --- 条件A + 条件B が両方True → 変換処理 ---

    # col24(取引金額) と col26(換算レート) を取得
    trx_amount_str = cols[IDX_TRX_AMOUNT].strip() if len(cols) > IDX_TRX_AMOUNT else ""
    rate_str       = cols[IDX_RATE].strip()        if len(cols) > IDX_RATE        else ""

    # 取引金額の妥当性チェック（空欄・非数値 → 変換スキップ）
    # isdigit() は文字列メソッドで使用可能。"." を1つだけ除去して数字のみか確認
    # 例: "162312.77".replace(".", "", 1).isdigit() → True
    #     "".replace(".", "", 1).isdigit()           → False（空欄はNG）
    #     "ABC".replace(".", "", 1).isdigit()        → False（非数値はNG）
    if not trx_amount_str.replace(".", "", 1).isdigit():
        # 取引金額が無効 → 変更なし (仕様書 §7 例外2)
        output_lines.append(line)
        continue

    # 換算レートの妥当性チェック（空欄はOK、非数値はNG）
    # 例: "38.98".replace(".", "", 1).isdigit()  → True（有効）
    #     "".replace(".", "", 1).isdigit()        → False（空欄 → レートなしとして扱う）
    #     "N/A".replace(".", "", 1).isdigit()     → False（非数値 → スキップ）
    rate_is_blank = (rate_str == "")
    rate_is_valid = rate_str.replace(".", "", 1).isdigit()

    if not rate_is_blank and not rate_is_valid:
        # 換算レートが空でも数値でもない → 変更なし (仕様書 §7 例外4)
        output_lines.append(line)
        continue

    # 換算後金額を計算（小数点以下切り捨て = int()）
    # ルール2: レートあり → floor(col24 × col26)
    #         レートなし → floor(col24)
    # 例: int(162312.77 * 38.98) = 6326951
    #     int(105006000 * 0.0092) = 966055
    #     int(5000.9)             = 5000   （レート空白時）
    if rate_is_blank:
        converted = str(int(float(trx_amount_str)))
    else:
        converted = str(int(float(trx_amount_str) * float(rate_str)))

    # 列数を OUTPUT_COL_COUNT(56) まで拡張（不足分は空文字で埋める）
    # 現在のT行はcol34まで。col35〜col55を空文字、col56に"2"を設定
    while len(cols) < OUTPUT_COL_COUNT:
        cols.append("")

    # ルール2: col25(index=24) に換算後金額を設定
    # 例: "6326951", "966055", "5000"
    cols[IDX_CONV_AMOUNT] = converted

    # ルール1: col56(index=55) に "2" を設定（決済区分）
    cols[IDX_PAYMENT_TYPE] = "2"

    # タブ結合して出力行を組み立て
    output_lines.append("\t".join(cols))

# 改行で結合して出力データを組み立て
data = "\n".join(output_lines)


# --- Step 3: 出力 ---
outfile.write(data)
