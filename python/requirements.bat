python -m venv ./venv-win
call venv-win\Scripts\activate.bat
pip install --no-cache-dir -r requirements.txt --upgrade
echo "Installation complete"
pause