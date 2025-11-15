name: جلب عناوين فيديوهات Google Drive

on:
  workflow_dispatch:  # لتشغيله يدويًا من GitHub

jobs:
  fetch-titles:
    runs-on: ubuntu-latest

    env:
      SERVICE_ACCOUNT_JSON_B64: ${{ secrets.SERVICE_ACCOUNT_JSON_B64 }}  # ضع Base64 هنا

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: تثبيت Python و Pip
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: تثبيت المتطلبات
        run: |
          python -m pip install --upgrade pip
          pip install --no-cache-dir google-api-python-client google-auth

      - name: تشغيل السكربت
        run: |
          python main.py
