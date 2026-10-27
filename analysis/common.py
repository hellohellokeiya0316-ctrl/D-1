"""各CSV分析スクリプトで共通に使う読み込み・表示・作図のユーティリティ."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"

pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 200)
pd.set_option("display.max_colwidth", 40)
pd.set_option("display.unicode.east_asian_width", True)


def setup_japanese_font():
    """グラフで日本語が文字化けしないよう、利用可能な日本語フォントを設定する."""
    candidates = [
        "Noto Sans CJK JP", "Noto Sans JP", "IPAexGothic", "IPAGothic",
        "Hiragino Sans", "Hiragino Maru Gothic Pro", "Yu Gothic", "Meiryo", "MS Gothic",
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams["font.family"] = name
            return name
    print("[warn] 日本語フォントが見つかりません。グラフの日本語が豆腐(□)になる場合があります。")
    return None


setup_japanese_font()


def load_csv(name, **kwargs):
    """data/ 配下のCSVを読み込む (BOM付きUTF-8にも対応)."""
    path = Path(name) if Path(name).is_absolute() else DATA_DIR / name
    return pd.read_csv(path, encoding="utf-8-sig", **kwargs)


def show(df, title=None, n=None):
    """DataFrameを表形式で表示する. Jupyter上ではHTMLテーブル、ターミナルではテキスト表."""
    if title:
        print(f"\n### {title}")
    view = df if n is None else df.head(n)
    try:
        from IPython import get_ipython
        from IPython.display import display

        if get_ipython() is not None:
            display(view)
            return
    except ImportError:
        pass
    print(view.to_string())


def overview(df, name):
    """行数・列数、先頭行、型・欠損・ユニーク数、数値列の基本統計量を表示する."""
    print("=" * 80)
    print(f"[{name}] shape = {df.shape[0]:,} 行 x {df.shape[1]} 列")
    print("=" * 80)
    show(df, "先頭5行", n=5)

    info = pd.DataFrame({
        "型": df.dtypes.astype(str),
        "欠損数": df.isna().sum(),
        "欠損率(%)": (df.isna().mean() * 100).round(2),
        "ユニーク数": df.nunique(),
        "例": df.apply(lambda s: s.dropna().iloc[0] if s.notna().any() else None),
    })
    show(info, "列ごとの情報")

    num = df.select_dtypes("number")
    if not num.empty:
        show(num.describe().T.round(3), "数値列の基本統計量")


def value_counts_table(s, top=None):
    """件数と割合を並べた度数表を返す."""
    vc = s.value_counts(dropna=False)
    table = pd.DataFrame({"件数": vc, "割合(%)": (vc / vc.sum() * 100).round(2)})
    return table if top is None else table.head(top)


def save_fig(fig, filename):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    print(f"[saved] {path.relative_to(ROOT)}")
