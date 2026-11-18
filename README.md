# 國小數學考卷圖庫

三至六年級資源班用的原創數學示意圖。PNG 檔案按年級存放在 `images/g3/` 至 `images/g6/`。`data/index.json` 以 UTF-8 儲存，每筆的 `img` 是相對於 `images/` 的路徑。

## 重新產生

在有 Python、Pillow 和 Noto Serif CJK 繁體中文字型的 Linux 環境執行。Debian 或 Ubuntu 的字型套件為 `fonts-noto-cjk`。

```sh
python -m pip install Pillow
python src/generate.py
```
