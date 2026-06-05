@echo off
title WC MASTER SYNC PIPELINE

echo ============================
echo STARTING WC MASTER SYNC
echo ============================

cd /d C:\wc_dashboard_sync

echo.
echo ============================
echo STEP 1: ORDER SYNC
echo ============================
python upload_order.py

echo.
echo ============================
echo STEP 2: ENGAGEMENT SYNC
echo ============================
python upload_engagement.py

echo.
echo ============================
echo STEP 3: ALL SHEETS SYNC
echo ============================
python sync_all_sheets.py

echo.
echo ============================
echo ALL PROCESSES COMPLETE
echo ============================

pause