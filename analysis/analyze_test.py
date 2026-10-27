"""test.csv: 予測対象ユーザーの属性分析と train.csv との分布比較."""
import pandas as pd

from analysis.common import load_csv, overview, show


def main():
    test = load_csv("test.csv")
    train = load_csv("train.csv")
    overview(test, "test.csv")

    # ID の重複チェック
    print(f"test のユーザーID重複: {test['ユーザーID'].duplicated().sum()}")
    print(f"train と共通のユーザーID: {test['ユーザーID'].isin(train['ユーザーID']).sum()}")

    # 列構成の比較
    print(f"train にのみ存在する列: {sorted(set(train.columns) - set(test.columns))}")
    print(f"test にのみ存在する列: {sorted(set(test.columns) - set(train.columns))}")

    # 各カテゴリ列の構成比を train / test で比較 (分布のずれを確認)
    cat_cols = [c for c in test.columns if c != "ユーザーID"]
    summary = []
    for col in cat_cols:
        tr = train[col].value_counts(normalize=True)
        te = test[col].value_counts(normalize=True)
        comp = pd.concat([tr.rename("train(%)"), te.rename("test(%)")], axis=1).fillna(0) * 100
        comp["差(pt)"] = comp["test(%)"] - comp["train(%)"]
        show(comp.round(2).sort_values("train(%)", ascending=False), f"{col} の構成比 train vs test")
        summary.append({
            "列": col,
            "最大差(pt)": comp["差(pt)"].abs().max().round(2),
            "testのみのカテゴリ": sorted(set(te.index) - set(tr.index)),
        })
    show(pd.DataFrame(summary).sort_values("最大差(pt)", ascending=False), "train/test 分布差のサマリ")


if __name__ == "__main__":
    main()
