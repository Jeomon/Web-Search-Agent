from setuptools import setup, find_packages

with open('./docs/README.md') as f:
    long_description = f.read()
setup(
    name='Web-Agent',
    version='0.1',
    description='The web agent is designed to automate the process of gathering information from the internet, such as to navigate websites, perform searches, and retrieve data.',
    author='jeomon',
    author_email='jeogeoalukka@gmail',
    url='https://github.com/Jeomon/Web-Agent',
    packages=find_packages(),
    install_requires=[
        'langgraph',
        'tenacity'
        'requests'
        'playwright'
        'termcolor'
        'python-dotenv'
        'httpx'
        'nest_asyncio'
        'MainContentExtractor'
    ],
    entry_points={
        'console_scripts': [
            'web-agent=main:main'
        ]
    },
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT'
)