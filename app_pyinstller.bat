
python -m PyInstaller --onedir --noconsole --icon=Icon_v5.ico --name ImageManager --add-data "settings.json;." --add-data "default_settings.json;." --distpath ./app/dist --workpath ./app/build manager.py
