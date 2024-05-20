from PyInstaller.__main__ import run

def package_with_pyinstaller():
    app_name = 'ImageManager'
    output_dir = './app'
    opts = [
        '--onefile',
        f'--name={app_name}',
        '--add-data "settings.json;."',
        '--add-data "default_settings.json;."',
        f'--distpath={output_dir}/dist',
        f'--workpath={output_dir}/build',
        'manager.py'
        ]
    run(opts)

if __name__ == "__main__":
    package_with_pyinstaller()
