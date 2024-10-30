import subprocess
import sys

# Install project dependencies


packages = [
    "flask", "flask-cors", "requests", "pandas", "pocketbase",
    "python-dotenv", "google-auth-oauthlib", "google-api-python-client",
    "google-generativeai"
]

def install_packages(packages):
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {package}: {str(e)}")

if __name__ == "__main__":
    install_packages(packages)