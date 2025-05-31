name: KoboToolbox Sync

on:
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install requests

      - name: Run KoboToolbox Sync (Debug)
        env:
          KOBO_API_TOKEN: ${{ secrets.KOBO_API_TOKEN }}
        run: python kobo_sync.py

      - name: Debug - List all files
        run: |
          ls -la
          echo "CSV files:"
          ls *.csv || echo "No CSV files found"

      - name: Commit and push changes
        if: success()
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "Automated sync: ${{ github.run_number }}"
          branch: main

          token: ${{ secrets.GH_PAT }}
