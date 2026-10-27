"""全CSVの分析をまとめて実行する: python -m analysis.run_all"""
from analysis import analyze_films, analyze_sample_submit, analyze_test, analyze_train, analyze_viewing_log

if __name__ == "__main__":
    for module in (analyze_train, analyze_test, analyze_films, analyze_viewing_log, analyze_sample_submit):
        print(f"\n\n{'#' * 30} {module.__name__} {'#' * 30}")
        module.main()
