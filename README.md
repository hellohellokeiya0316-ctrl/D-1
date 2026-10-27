# 動画配信サービス 継続予測データの分析

各CSVを表形式で表示し、基本的な分析・可視化を行うPythonコードです。

## セットアップ

```bash
pip install -r requirements.txt
```

`data/` に以下のCSVを配置してください (`data/` は git 管理外)。

| ファイル | 内容 |
|---|---|
| `train.csv` | ユーザー属性・登録時アンケート + 目的変数 `継続フラグ` |
| `test.csv` | 予測対象ユーザーの属性・アンケート (目的変数なし) |
| `films.csv` | 作品マスタ (カテゴリ・配信形態・シーズン/話数・尺・概要) |
| `viewing_log.csv` | 視聴ログ (日時・ユーザー・プロフィール・作品・視聴時間・デバイス) |
| `sample_submit.csv` | 提出フォーマット (ヘッダなし: `ユーザーID,予測値`) |

## 実行

```bash
python -m analysis.run_all              # すべて実行
python -m analysis.analyze_train        # train.csv のみ
python -m analysis.analyze_test         # test.csv のみ (train との分布比較を含む)
python -m analysis.analyze_films        # films.csv のみ
python -m analysis.analyze_viewing_log  # viewing_log.csv のみ (films / train と結合した分析を含む)
python -m analysis.analyze_sample_submit
```

表はターミナルではテキスト表、Jupyter では HTML テーブルとして表示されます
(Jupyter ではリポジトリ直下で `from analysis import analyze_train; analyze_train.main()`)。
グラフは `outputs/` に PNG で保存されます。

## 各スクリプトの分析内容

- **共通 (`analysis/common.py`)**: 行数・列数、先頭行、列ごとの型/欠損/ユニーク数、数値列の統計量
- **train**: 継続フラグの分布、各属性・アンケート項目ごとの件数と継続率、年齢×性別の継続率ヒートマップ
- **test**: ID重複・train との ID 重複、各項目の構成比の train/test 比較
- **films**: カテゴリ別作品数、週次/独占配信、カテゴリ別の話数・尺、総視聴時間 TOP10
- **viewing_log**: 日別・時間帯別の視聴傾向、デバイス/プロフィール分布、films にないタイトルIDの検出、
  カテゴリ・作品別の視聴集計、ユーザー単位の集計特徴量と継続フラグとの関係、デバイス・最多視聴カテゴリ別の継続率
- **sample_submit**: test との ID・順序の一致確認、予測値の分布、提出ファイル書き出し関数 `write_submission`
