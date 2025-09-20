from setuptools import setup, find_packages

setup(
    name="text-to-speech-automation",
    version="1.0.0",
    description="Text-to-Speech Automation Tool with document processing",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask==2.3.3",
        "Werkzeug==2.3.7",
        "pyttsx3>=2.90",
        "PyPDF2>=3.0.1",
        "python-docx>=0.8.11",
        "python-pptx>=0.6.21",
        "chardet>=5.0.0",
        "beautifulsoup4>=4.11.1",
        "requests>=2.28.1",
        "python-dotenv>=1.0.0"
    ],
    python_requires=">=3.9",
    entry_points={
        'console_scripts': [
            'tts-webapp=run_webapp:main',
        ],
    },
)