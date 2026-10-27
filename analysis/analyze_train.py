"""train.csv: ユーザー属性・登録時アンケートと継続フラグ(目的変数)の分析."""
import matplotlib.pyplot as plt
import seaborn as sns

from analysis.common import load_csv, overview, save_fig, show, value_counts_table

TARGET = "継続フラグ"


def main():
    df = load_csv("train.csv")
    overview(df, "train.csv")

    # 目的変数の分布
    show(value_counts_table(df[TARGET]), f"目的変数 {TARGET} の分布")
    print(f"継続率: {df[TARGET].mean():.3f}")

    # カテゴリ列ごとの度数と継続率
    cat_cols = [c for c in df.columns if c not in ("ユーザーID", TARGET)]
    for col in cat_cols:
        table = df.groupby(col, dropna=False)[TARGET].agg(件数="size", 継続率="mean")
        table["継続率"] = table["継続率"].round(3)
        table["全体との差"] = (table["継続率"] - df[TARGET].mean()).round(3)
        show(table.sort_values("件数", ascending=False), f"{col} 別の件数と継続率")

    # 継続率の可視化 (ユニーク数が少ない列のみ)
    plot_cols = [c for c in cat_cols if df[c].nunique() <= 12]
    for i, col in enumerate(plot_cols):
        rate = df.groupby(col)[TARGET].mean().sort_values()
        fig, ax = plt.subplots(figsize=(8, 0.4 * len(rate) + 1.5))
        ax.barh(rate.index.astype(str), rate.values, color="#4C72B0")
        ax.axvline(df[TARGET].mean(), color="gray", ls="--", label="全体平均")
        ax.set_xlabel("継続率")
        ax.set_title(f"{col} 別の継続率")
        ax.legend()
        save_fig(fig, f"train_rate_{i:02d}.png")

    # 年齢レンジ x 性別 のクロス集計(継続率)
    pivot = df.pivot_table(index="年齢レンジ", columns="性別", values=TARGET, aggfunc="mean")
    show(pivot.round(3), "年齢レンジ x 性別 の継続率")
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.heatmap(pivot, annot=True, fmt=".2f", cmap="Blues", ax=ax)
    ax.set_title("年齢レンジ x 性別 の継続率")
    save_fig(fig, "train_age_gender_heatmap.png")


if __name__ == "__main__":
    main()
