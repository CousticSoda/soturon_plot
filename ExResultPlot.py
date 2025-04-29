import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import re
import japanize_matplotlib

# --- 縦書きラベル用関数 ---
def vertical_label(text):
    tokens = re.findall(r'\([^)]*\)|.', text)
    return "\n".join(tokens)

# --- 元データ読み込み ---
data = """2/12 AM1	19.2	20.2	12.7	0	0	0	0	0	0
2/13 AM9	20.1	20.3	13.4	0	0	0	0	0	0
2/13 PM5	20	20	13.4	0	0	0	0	0	0
2/13 AM1	20.1	20.3	13	0	0	0	0	0	0
2/14 AM9	19.7	20.1	12.7	0	0	0	0	0	0
2/14 PM5	20.3	20.3	13.4	0	0	0	0	0	0
2/14 AM1	18.7	19.4	13.2	0	0	0	0	0	0
2/15 AM9	20.1	20.1	13.6	2	1	0	2	2	0
2/15 PM5	19.5	19.7	13.1	14	6	0	9	4	0
2/15 AM1	20	20.1	13.4	20	12	0	13	11	0
2/16 AM9	20	19.7	13.1	36	23	0	25	27	2
2/16 PM5	NaN	NaN	NaN	NaN	NaN	NaN	NaN	NaN	NaN
2/16 AM1	19.1	20.1	13.2	49	42	0	45	40	12
2/17 AM9	19.5	19.3	13.4	51	50	3	59	45	25
2/17 PM5	20.2	20	12.5	60	59	4	60	57	33
2/17 AM1	19.8	19.3	13.3	66	63	6	62	58	40
2/18 AM9	19.8	20.1	13.3	68	65	14	66	59	40
2/18 PM5	19.2	19.1	12.9	71	66	37	70	65	51
2/18 AM1	19.8	20	12.2	77	74	42	71	67	59
2/19 AM9	19.6	19	12.8	77	74	47	74	67	63
2/19 PM5	20	19.2	13.6	77	78	50	74	71	66
2/19 AM1	18.9	19.5	13.3	79	79	54	74	72	69
2/20 AM9	19.5	19.6	12.2	79	79	54	74	73	69
2/20 PM9	19	19.3	12.4	79	79	60	74	73	69
2/20 AM1	19.9	19.8	12.6	79	79	66	74	73	69
2/21 AM9	19.6	19	12.7	79	79	66	74	73	69
2/21 PM5	19.7	19.1	12.9	79	79	68	74	73	69
"""
df = pd.read_csv(StringIO(data), sep='\t', header=None)
df.columns = [
    "Datetime",
    "70dB,20℃_温度", "40dB,20℃_温度", "40dB,13℃_温度",
    "70dB,20℃_カイワレ大根", "40dB,20℃_カイワレ大根", "40dB,13℃_カイワレ大根",
    "70dB,20℃_小松菜", "40dB,20℃_小松菜", "40dB,13℃_小松菜"
]
df.set_index("Datetime", inplace=True)

# --- インデックス前後空白除去 & 「n日目 H時」変換 ---
df.index = df.index.str.strip()
unique_dates = sorted({ idx.split()[0] for idx in df.index },
                      key=lambda s: tuple(map(int, s.split('/'))))
date2day = { d: i+1 for i, d in enumerate(unique_dates) }

def convert_label(idx):
    m = re.match(r'(\d+/\d+)\s*(AM|PM)(\d+)', idx)
    if not m: return idx
    date, ampm, h = m.group(1), m.group(2), int(m.group(3))
    hour = (h % 12) + (12 if ampm=="PM" else 0)
    return f"{date2day[date]}日目 {hour}時"

df.index = df.index.map(convert_label)

# --- 補間データ作成 ---
df_interp = df.interpolate(method='linear')

# --- 色指定（青・オレンジ・緑） ---
colors = ['tab:blue', 'tab:orange', 'tab:green']
groups = [
    (["70dB,20℃_温度","40dB,20℃_温度","40dB,13℃_温度"], "各実験環境における温度差", "温度(℃)"),
    (["70dB,20℃_カイワレ大根","40dB,20℃_カイワレ大根","40dB,13℃_カイワレ大根"], "各実験環境におけるカイワレ大根の発芽数", "発芽数(個)"),
    (["70dB,20℃_小松菜","40dB,20℃_小松菜","40dB,13℃_小松菜"], "各実験環境における小松菜の発芽数", "発芽数(個)")
]

# --- 切り離し表示 ---
for cols, title, ylabel in groups:
    fig, ax = plt.subplots(figsize=(10, 6))
    # 線（補間済みデータで描画）
    df_interp[cols].plot(ax=ax, color=colors, marker=None)
    # マーカー（元データのみ、NaNは描画されない）
    df[cols].plot(ax=ax, linestyle='None', marker='o', color=colors, legend=False)
    ax.set_title(title)
    ax.set_xlabel("日付")
    ax.set_ylabel(vertical_label(ylabel), rotation=0, labelpad=30, ha="right", va="center")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid()
    plt.show()
