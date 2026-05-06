# Kyriba Restricted Python - ファイル変換スクリプト（修正版）
# 概要: SAP支払データ(TSV) → Kyriba支払モジュール取り込み用変換
# 対応: Restricted Python ルール（def/class禁止, import不要, 入出力は infile/default_out）
# 修正点: 出力ハンドラを outfile → default_out に修正。Step構成も準拠。

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
# 必須: Restricted Pythonの定形。infile.read() で全件読み込み。
data = infile.read()

# --- Step 2: 変換処理 ---
# 改行コードを統一して行分割
lines = data.replace("\r\n", "\n").replace("\r", "\n").split("\n")

output_lines = []

for line in lines:
    # 空行はそのまま透過
    if line == "":
        output_lines.append(line)
        continue

    cols = line.split("\t")

    # T行以外（D行等）は変更なしでそのまま出力
    if not cols or cols[IDX_RECORD_TYPE] != "T":
        output_lines.append(line)
        continue

    # --- 条件A: BOTK口座チェック ---
    # ① col4の値を取り出す（列が存在しない場合は空文字にする）
    if len(cols) > IDX_ACCOUNT_CODE:
        account_code = cols[IDX_ACCOUNT_CODE]
    else:
        account_code = ""

    # ② ACCOUNT_MAPで内部コードに変換する（マップにない場合は空文字）
    internal_code = ACCOUNT_MAP.get(account_code, "")

    # ③ 内部コードの4〜7文字目が "BOTK" か判定する
    if len(internal_code) >= 7 and internal_code[3:7] == "BOTK":
        is_botk = True
    else:
        is_botk = False

    if not is_botk:
        output_lines.append(line)
        continue

    # --- 条件B: 特定通貨チェック ---
    # ① col23の値（取引通貨）を取り出す
    if len(cols) > IDX_TRX_CURRENCY:
        trx_currency = cols[IDX_TRX_CURRENCY]
    else:
        trx_currency = ""

    # ② 特定通貨かどうか判定する
    if trx_currency in TARGET_CURRENCIES:
        is_target_currency = True
    else:
        is_target_currency = False

    if is_target_currency == False:
        output_lines.append(line)
        continue

    # --- 条件A + 条件B が両方True → 変換処理 ---
    # ① col24（取引金額）を取り出す（前後の空白を除去）
    if len(cols) > IDX_TRX_AMOUNT:
        trx_amount_str = cols[IDX_TRX_AMOUNT].strip()
    else:
        trx_amount_str = ""

    # ② col26（換算レート）を取り出す（前後の空白を除去）
    if len(cols) > IDX_RATE:
        rate_str = cols[IDX_RATE].strip()
    else:
        rate_str = ""

    # ③ 金額が数値かチェックする（小数点1個を除いて数字のみならOK）
    amount_check = trx_amount_str.replace(".", "", 1)
    if amount_check.isdigit() == True:
        amount_is_valid = True
    else:
        amount_is_valid = False

    if amount_is_valid == False:
        output_lines.append(line)
        continue

    # ④ レートのチェック（空欄はOK、非数値はNG）
    if rate_str == "":
        rate_is_blank = True
    else:
        rate_is_blank = False

    rate_check = rate_str.replace(".", "", 1)
    if rate_check.isdigit() == True:
        rate_is_valid = True
    else:
        rate_is_valid = False

    if rate_is_blank == False and rate_is_valid == False:
        output_lines.append(line)
        continue

    # ① 換算後金額を計算する（小数点以下切り捨て）
    if rate_is_blank == True:
        # レートが空欄の場合: 取引金額をそのまま切り捨て
        converted = str(int(float(trx_amount_str)))
    else:
        # レートがある場合: 取引金額 × 換算レートを切り捨て
        converted = str(int(float(trx_amount_str) * float(rate_str)))

    # ② 列数を56列まで拡張する（不足分は空文字で埋める）
    while len(cols) < OUTPUT_COL_COUNT:
        cols.append("")

    # ③ col25（換算後金額）に計算結果を設定する
    cols[IDX_CONV_AMOUNT] = converted

    # ④ col56（決済区分）に "2" を設定する
    cols[IDX_PAYMENT_TYPE] = "2"

    # ⑤ タブで結合して出力リストに追加する
    output_lines.append("\t".join(cols))

# 改行で結合して出力データを組み立て
data = "\n".join(output_lines)

# --- Step 3: 出力 ---
# 必須: Restricted Pythonの定形。default_out.write() を使用。
default_out.write(data)