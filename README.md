# Stlite Project

This project is a Streamlit application that runs entirely in the browser using [stlite](https://github.com/whitphx/stlite).

## How to run

### 1. In the Browser (stlite)

You can serve the project using a local web server and open `index.html` in your browser.

```bash
npm start
```

Then open `http://localhost:3000` (or the port specified by `serve`).

### 2. Standard Streamlit (Local Python)

You can also run the app using standard Streamlit if you have Python installed.

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Project Structure

- `streamlit_app.py`: The Streamlit application code.
- `index.html`: The entry point that loads stlite and runs the app.
- `package.json`: Contains the script to serve the app locally.
- `requirements.txt`: Python dependencies for local development.

---

# stlite プロジェクト

このプロジェクトは、[stlite](https://github.com/whitphx/stlite) を使用してブラウザ上で完全に動作する Streamlit アプリケーションです。

## 実行方法

### 1. ブラウザで実行 (stlite)

ローカルサーバーを起動して `index.html` をブラウザで開きます。

```bash
npm start
```

起動後、`http://localhost:3000`（または表示されたポート）にアクセスしてください。

### 2. 通常の Streamlit で実行 (ローカル Python)

Python がインストールされている環境であれば、通常の Streamlit としても実行可能です。

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
