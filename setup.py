from setuptools import setup

setup(
  name = 'hcrawler',
  version = '0.1',
  author = 'Ha Hoang Hao',
  packages = ['hcrawler'],
  description = 'Crawl Tiki web data using selenium',
  install_requires = ['pandas', 'numpy', 'selenium', 're', 'ast', 'pickle']
)
