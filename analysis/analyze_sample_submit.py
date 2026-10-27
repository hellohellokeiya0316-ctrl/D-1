"""sample_submit.csv: 提出フォーマットの確認 (ヘッダなし: ユーザーID, 継続確率)."""
import matplotlib.pyplot as plt

from analysis.common import load_csv, overview, save_fig, show


def main():
    sub = load_csv("sample_submit.csv", header=None, names=["ユーザーID", "予測値"])
    overview(sub, "sample_submit.csv")

    test = load_csv("test.csv")
    print(f"行数: submit {len(sub)} / test {len(test)}")
    print(f"ID集合が test と一致: {set(sub['ユーザーID']) == set(test['ユーザーID'])}")
    print(f"ID の並び順が test と一致: {sub['ユーザーID'].tolist() == test['ユーザーID'].tolist()}")
    print(f"予測値の範囲: {sub['予測値'].min():.4f} 〜 {sub['予測値'].max():.4f} (0〜1 の確率値)")
    show(sub["予測値"].describe().to_frame().T.round(4), "予測値の統計量")

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(sub["予測値"], bins=20, color="#4C72B0", edgecolor="white")
    ax.set_title("sample_submit の予測値分布")
    save_fig(fig, "sample_submit_hist.png")


def write_submission(user_ids, preds, path):
    """sample_submit.csv と同じ形式 (ヘッダなし, ユーザーID,予測値) で提出ファイルを書き出す."""
    import pandas as pd

    pd.DataFrame({"ユーザーID": user_ids, "予測値": preds}).to_csv(path, header=False, index=False)


if __name__ == "__main__":
    main()
