"""films.csv: 作品マスタ(カテゴリ・配信形態・話数・尺)の分析."""
import matplotlib.pyplot as plt
import seaborn as sns

from analysis.common import load_csv, overview, save_fig, show, value_counts_table


def main():
    df = load_csv("films.csv")
    df["総視聴時間(分)"] = df["エピソード数"] * df["1話当たりの時間(分)"]
    df["概要文字数"] = df["作品概要"].str.len()
    overview(df.drop(columns="作品概要"), "films.csv")

    print(f"タイトルIDの重複: {df['タイトルID'].duplicated().sum()}")
    print(f"タイトル名の重複: {df['タイトル名'].duplicated().sum()}")

    show(value_counts_table(df["カテゴリ"]), "カテゴリ別の作品数")
    for col in ("週次配信", "独占配信"):
        show(value_counts_table(df[col]), f"{col} の分布")

    # カテゴリ別の要約
    summary = df.groupby("カテゴリ").agg(
        作品数=("タイトルID", "size"),
        週次配信率=("週次配信", "mean"),
        独占配信率=("独占配信", "mean"),
        平均シーズン数=("シーズン数", "mean"),
        平均エピソード数=("エピソード数", "mean"),
        平均1話時間=("1話当たりの時間(分)", "mean"),
        平均総視聴時間=("総視聴時間(分)", "mean"),
    ).round(2)
    show(summary.sort_values("作品数", ascending=False), "カテゴリ別サマリ")

    show(df.nlargest(10, "総視聴時間(分)")[
        ["タイトルID", "タイトル名", "カテゴリ", "シーズン数", "エピソード数", "1話当たりの時間(分)", "総視聴時間(分)"]
    ], "総視聴時間が長い作品 TOP10")

    # 作図
    fig, ax = plt.subplots(figsize=(7, 4))
    df["カテゴリ"].value_counts().plot.bar(ax=ax, color="#4C72B0")
    ax.set_title("カテゴリ別の作品数")
    ax.set_ylabel("作品数")
    save_fig(fig, "films_category_count.png")

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.boxplot(data=df, x="カテゴリ", y="1話当たりの時間(分)", ax=ax)
    ax.set_title("カテゴリ別の1話当たり時間")
    save_fig(fig, "films_duration_box.png")

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.boxplot(data=df, x="カテゴリ", y="エピソード数", ax=ax)
    ax.set_title("カテゴリ別のエピソード数")
    save_fig(fig, "films_episodes_box.png")


if __name__ == "__main__":
    main()
