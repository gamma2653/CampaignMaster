# Calls npm to build the web app
import subprocess


def initialize_web_app():
    """
    Initializes the web app by removing react-scripts and adding rsbuild.
    """
    subprocess.run(['npm', 'remove', 'react-scripts'], check=True, shell=True)
    subprocess.run(['npm', 'add', '@rsbuild/core', '@rsbuild/plugin-react', '-D'], check=True, shell=True)
    subprocess.run(['npm', 'add', '@rsbuild/plugin-less', '-D'], check=True, shell=True)
    build_web_app()

def build_web_app():
    """
    Builds the web app by installing dependencies and running the build script.
    """
    subprocess.run(['npm', 'install'], check=True, shell=True)
    subprocess.run(['npm', 'run', 'build'], check=True, shell=True)
    print("Web app built successfully.")
