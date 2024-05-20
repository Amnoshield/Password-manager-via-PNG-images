import subprocess

def package_with_pyinstaller():
    app_name = 'ImageManager'
    output_dir = './app'
    #python -m
    pyinstaller_cmd = [
        'PyInstaller',
        '--onefile',
        f'--name {app_name}',
        f'--distpath {output_dir}/dist',
        f'--workpath {output_dir}/build',
        'manager.py'
    ]
    subprocess.run(pyinstaller_cmd)

# Usage example
if __name__ == "__main__":
    package_with_pyinstaller()
