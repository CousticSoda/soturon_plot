import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import matplotlib as mpl 
import re
import japanize_matplotlib
from matplotlib.ticker import FixedLocator, FixedFormatter
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import FuncFormatter, MultipleLocator

mpl.rcParams['font.size']      = 14
mpl.rcParams['axes.titlesize'] = 18
mpl.rcParams['axes.labelsize'] = 16
mpl.rcParams['xtick.labelsize']= 14
mpl.rcParams['ytick.labelsize']= 14

# --- 縦書きラベル用関数 ---
def vertical_label(text):
    tokens = re.findall(r'\([^)]*\)|.', text)
    return "\n".join(tokens)

# --- 元データ読み込み ---
data = """2/13 AM1	19.2	20.2	12.7	0	0	0	0	0	0
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
2/20 PM5	19	19.3	12.4	79	79	60	74	73	69
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

# --- インデックス前後空白除去＆「n日目 H時」変換 ---
df.index = df.index.str.strip()
unique_dates = sorted({ idx.split()[0] for idx in df.index },
                      key=lambda s: tuple(map(int, s.split('/'))))
date2day = { d: i+1 for i, d in enumerate(unique_dates) }

def convert_label(idx):
    m = re.match(r'(\d+/\d+)\s*(AM|PM)(\d+)', idx)
    if not m:
        return idx
    date, ampm, hour = m.group(1), m.group(2), int(m.group(3))
    if ampm == "PM":
        hour = 0 if hour == 12 else hour + 12
    else:
        hour = 12 if hour == 12 else hour
    return f"{date2day[date]}日目 {hour}時"

df.index = df.index.map(convert_label)

# --- 補間データ作成（欠損部もつなぐ用） ---
df_interp = df.interpolate(method='linear')

# --- 色の指定 ---
colors = ['tab:blue', 'tab:orange', 'tab:green']

# --- プロットループ ---
groups = [
    (["70dB,20℃_温度","40dB,20℃_温度","40dB,13℃_温度"], "各実験環境における温度差", "温度(℃)"),
    (["70dB,20℃_カイワレ大根","40dB,20℃_カイワレ大根","40dB,13℃_カイワレ大根"], "各実験環境におけるカイワレ大根の発芽数", "発芽数(個)"),
    (["70dB,20℃_小松菜","40dB,20℃_小松菜","40dB,13℃_小松菜"], "各実験環境における小松菜の発芽数", "発芽数(個)")
]

# --- y軸フォーマッターを定義 ---
def make_max_formatter(max_value):
  def formatter(x, pos):
    #少数誤差対策に int(x)で比較
    if int(x) == max_value:
      return f"{int(x)}(max)"
    return str(int(x))
  return FuncFormatter(formatter)


def convert_label(idx):
    m = re.match(r'(\d+/\d+)\s*(AM|PM)(\d+)', idx)
    if not m: 
        return idx
    date, ampm, hour = m.group(1), m.group(2), int(m.group(3))
    hour = (hour % 12) + (12 if ampm=="PM" else 0)
    # ← ここを「○日目(○時)」に
    return f"{date2day[date]}日目({hour}時)"

df.index = df.index.map(convert_label)

# --- プロットループ ---
for cols, title, ylabel in groups:
    plt.figure(figsize=(14,8))
    ax = plt.gca()
    df_interp[cols].plot(ax=ax, color=colors, marker=None)
    df[cols].plot (ax=ax, linestyle='None', marker='o', color=colors, legend=False)

    if "発芽数" in title:
        # 発芽数プロットは0～80に固定＆80(max)
        ax.set_ylim(0, 80)
        ax.yaxis.set_major_formatter(make_max_formatter(80))
           # Y 軸は少し下まで余白を取りつつ、目盛は 0,10,...,80 に限定
        ax.set_ylim(-5, 80)                      # グラフ領域は -5 から 80
        ax.yaxis.set_major_locator(MultipleLocator(10))  # 目盛を 0,10,20…,80 に
        ax.yaxis.set_major_formatter(make_max_formatter(80))
    else:
        # 温度差プロットは上限だけ21に設定
        ax.set_ylim(top=21)
        ax.yaxis.set_major_locator(MultipleLocator(1))   
        ax.yaxis.set_major_formatter(
            FuncFormatter(lambda x, pos: str(int(x)))
        )
    

    # ← ここで全ラベルを一括設定
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df.index, rotation=45, ha='right')

    ax.set_title(title)
    ax.set_xlabel("日付")
    ax.set_ylabel(vertical_label(ylabel),
                  rotation=0, labelpad=30, ha="right", va="center")
    plt.grid(True, axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()
