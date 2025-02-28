name: Update M3U8 Link

on:
  schedule:
    - cron: '*/5 * * * *'  # Hər 5 dəqiqədən bir
  workflow_dispatch:  # Manual başlatma üçün əlavə et

jobs:
  update:
    runs-on: ubuntu-latest

    steps:
    - name: Check out code
      uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.x'

    - name: Install dependencies
      run: |
        pip install selenium requests

    - name: Install Chromium and ChromeDriver
      run: |
        sudo apt-get update
        sudo apt-get install -y chromium-browser
        sudo apt-get install -y chromium-chromedriver
        sudo apt-get install -y libnss3 libgdk-pixbuf2.0-0 libxss1 libatk-bridge2.0-0 libatk1.0-0 libgbm-dev
        sudo apt-get install -y libgconf-2-4 || echo "libgconf-2-4 not found"

    - name: Set Chrome options
      run: |
        echo "CHROME_BIN=/usr/bin/chromium-browser" >> $GITHUB_ENV

    - name: Run token update script
      run: |
        python update_token.py
