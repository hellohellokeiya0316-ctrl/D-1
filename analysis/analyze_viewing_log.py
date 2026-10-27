"""viewing_log.csv: 視聴ログの分析 (時間帯・デバイス・ユーザー/作品単位の集計, 継続との関係)."""
import matplotlib.pyplot as plt
import pandas as pd

from analysis.common import load_csv, overview, save_fig, show, value_counts_table


def main():
    log = load_csv("viewing_log.csv", parse_dates=["日時"])
    overview(log, "viewing_log.csv")
    print(f"期間: {log['日時'].min()} 〜 {log['日時'].max()}")
    print(f"完全重複行: {log.duplicated().sum()}")

    for col in ("視聴デバイス", "プロフィール"):
        show(value_counts_table(log[col]), f"{col} の分布")

    # 時間軸での傾向
    log["日付"] = log["日時"].dt.date
    log["時"] = log["日時"].dt.hour
    log["曜日"] = log["日時"].dt.day_name()
    daily = log.groupby("日付").agg(視聴数=("ユーザーID", "size"), ユーザー数=("ユーザーID", "nunique"),
                                    総視聴時間=("視聴時間", "sum"))
    show(daily.round(1), "日別の視聴数・ユーザー数・総視聴時間")
    show(value_counts_table(log["時"]).sort_index(), "時間帯別の視聴数")

    fig, axes = plt.subplots(1, 2, figsize=(13, 4))
    daily["視聴数"].plot(ax=axes[0], marker="o")
    axes[0].set_title("日別の視聴数")
    log["時"].value_counts().sort_index().plot.bar(ax=axes[1], color="#4C72B0")
    axes[1].set_title("時間帯別の視聴数")
    save_fig(fig, "log_time_trend.png")

    # 作品マスタと結合してカテゴリ別に集計
    films = load_csv("films.csv")
    merged = log.merge(films[["タイトルID", "タイトル名", "カテゴリ"]], on="タイトルID", how="left")
    print(f"タイトルID欠損のログ: {log['タイトルID'].isna().sum()}")
    unknown = log.loc[log["タイトルID"].notna() & ~log["タイトルID"].isin(films["タイトルID"]), "タイトルID"]
    print(f"films に存在しないタイトルID: {len(unknown)} 行 ({unknown.nunique()} 種類)")
    show(value_counts_table(unknown, top=15), "films に存在しないタイトルID (表記ゆれ・欠損の候補)")
    show(merged.groupby("カテゴリ").agg(視聴数=("ユーザーID", "size"), ユーザー数=("ユーザーID", "nunique"),
                                       平均視聴時間=("視聴時間", "mean")).round(2)
         .sort_values("視聴数", ascending=False), "カテゴリ別の視聴集計")
    show(merged.groupby(["タイトルID", "タイトル名", "カテゴリ"]).size().rename("視聴数")
         .sort_values(ascending=False).head(15).reset_index(), "視聴数の多い作品 TOP15")

    # ユーザー単位の特徴量 (モデリングにも流用可能)
    user = log.groupby("ユーザーID").agg(
        視聴回数=("タイトルID", "size"),
        視聴作品数=("タイトルID", "nunique"),
        総視聴時間=("視聴時間", "sum"),
        平均視聴時間=("視聴時間", "mean"),
        視聴日数=("日付", "nunique"),
        プロフィール数=("プロフィール", "nunique"),
        初回視聴=("日時", "min"),
        最終視聴=("日時", "max"),
    )
    user["視聴期間(日)"] = (user["最終視聴"] - user["初回視聴"]).dt.days
    show(user.drop(columns=["初回視聴", "最終視聴"]).describe().T.round(2), "ユーザー単位の集計値の統計量")

    # train の継続フラグと結合し、継続/非継続で比較
    train = load_csv("train.csv")[["ユーザーID", "継続フラグ"]]
    test = load_csv("test.csv")[["ユーザーID"]]
    print(f"ログのあるユーザー: train {train['ユーザーID'].isin(user.index).mean():.1%}, "
          f"test {test['ユーザーID'].isin(user.index).mean():.1%}")
    tu = train.merge(user.reset_index(), on="ユーザーID", how="left")
    tu["ログあり"] = tu["視聴回数"].notna().astype(int)
    show(tu.groupby("ログあり")["継続フラグ"].agg(件数="size", 継続率="mean").round(3), "ログ有無と継続率")
    num_cols = ["視聴回数", "視聴作品数", "総視聴時間", "平均視聴時間", "視聴日数", "視聴期間(日)"]
    show(tu.groupby("継続フラグ")[num_cols].median().round(2), "継続フラグ別のユーザー集計値 (中央値)")

    fig, axes = plt.subplots(2, 3, figsize=(14, 7))
    for ax, col in zip(axes.ravel(), num_cols):
        tu.boxplot(column=col, by="継続フラグ", ax=ax, showfliers=False)
        ax.set_title(col)
        ax.set_xlabel("継続フラグ")
    fig.suptitle("継続フラグ別のユーザー視聴行動")
    save_fig(fig, "log_user_by_target.png")

    # デバイス・カテゴリ別の継続率
    lt = merged.merge(train, on="ユーザーID")
    dev = pd.crosstab(lt["ユーザーID"], lt["視聴デバイス"]).gt(0).astype(int).join(train.set_index("ユーザーID"))
    rows = [{"デバイス": d, "利用ユーザー数": dev[d].sum(), "継続率": dev.loc[dev[d] == 1, "継続フラグ"].mean()}
            for d in dev.columns.drop("継続フラグ")]
    show(pd.DataFrame(rows).round(3), "視聴デバイス利用有無別の継続率")
    cat = lt.groupby("ユーザーID")["カテゴリ"].agg(lambda s: s.mode().iloc[0] if s.notna().any() else None)
    cat = train.set_index("ユーザーID").join(cat.rename("最多視聴カテゴリ"), how="inner")
    show(cat.groupby("最多視聴カテゴリ")["継続フラグ"].agg(件数="size", 継続率="mean").round(3),
         "最多視聴カテゴリ別の継続率")


if __name__ == "__main__":
    main()
