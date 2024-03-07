# Information
This package to connect TradOvate API
## Installation
```bash

# Create an isolated Python virtual environment
pip3 install virtualenv
virtualenv ./virtualenv --python=$(which python3)

# Activate the virtualenv
# IMPORTANT: it needs to be activated every time before you run
. virtualenv/bin/activate

# Install Python requirements
pip install -r requirements.txt

# Starting with Python 3.12 you may need to run
pip install --upgrade setuptools
# run test
python -m test

# run test bot trading demo
python -m es5m_test

# Demo logic on Trading View
Please refer to repo https://github.com/dearvn/trading-futures-tradingview-script to view my logic to trade Futures on Tradovate
