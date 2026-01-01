name: 🎬 TR YouTube Stream Updater

on:
  schedule:
    # Hər 30 dəqiqədə bir yenilə
    - cron: '*/30 * * * *'
  
  workflow_dispatch:
  
  push:
    branches: [ main ]
    paths:
      - '**.json'
      - '**.py'
      - '.github/workflows/**.yml'

permissions:
  contents: write

jobs:
  update:
    runs-on: ubuntu-latest
    
    steps:
      - name: 📥 Repository götür
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: 🐍 Python quraşdır
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: 📦 Paketləri yüklə
        run: |
          python -m pip install --upgrade pip
          pip install yt-dlp
          pip install requests
      
      - name: 🎯 Stream-ləri yenilə
        id: update-streams
        run: |
          echo "🚀 TR YouTube Stream Updater başladı..."
          python main.py
          
          # Nəticəni yoxla
          m3u8_count=$(find TR -name "*.m3u8" 2>/dev/null | wc -l || echo "0")
          echo "m3u8_count=$m3u8_count" >> $GITHUB_OUTPUT
          
          if [ $m3u8_count -gt 0 ]; then
            echo "✅ $m3u8_count stream tapıldı"
            echo "has_streams=true" >> $GITHUB_OUTPUT
          else
            echo "⚠ Heç bir stream tapılmadı"
            echo "has_streams=false" >> $GITHUB_OUTPUT
          fi
      
      - name: 📊 Dəyişiklikləri yoxla
        if: steps.update-streams.outputs.has_streams == 'true'
        id: check-changes
        run: |
          git config --global user.email "github-actions@github.com"
          git config --global user.name "GitHub Actions"
          
          git add TR/ 2>/dev/null || true
          
          if ! git diff --cached --quiet; then
            echo "📬 Yeni dəyişikliklər var"
            echo "changes=true" >> $GITHUB_OUTPUT
            
            # Nə dəyişib göstər
            echo "📋 Dəyişən fayllar:"
            git diff --cached --name-only
          else
            echo "📭 Yeni dəyişiklik yoxdur"
            echo "changes=false" >> $GITHUB_OUTPUT
          fi
      
      - name: 💾 Commit et
        if: steps.update-streams.outputs.has_streams == 'true' && steps.check-changes.outputs.changes == 'true'
        run: |
          git commit -m "🎬 TR Stream-lər yeniləndi (${{ steps.update-streams.outputs.m3u8_count }} stream) - $(date +'%Y-%m-%d %H:%M')"
      
      - name: 🚀 Push et
        if: steps.update-streams.outputs.has_streams == 'true' && steps.check-changes.outputs.changes == 'true'
        run: |
          git push
      
      - name: 📋 Nəticə
        run: |
          echo "========================================"
          echo "🎉 TR YouTube Stream Updater Tamamlandı"
          echo "========================================"
          echo "Tarix: $(date)"
          echo "Stream sayı: ${{ steps.update-streams.outputs.m3u8_count }}"
          echo "Dəyişiklik: ${{ steps.check-changes.outputs.changes }}"
          echo "İş vaxtı: ${{ job.status }}"
          echo "========================================"
