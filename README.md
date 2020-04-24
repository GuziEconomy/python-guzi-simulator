# python-guzi-simulator
A library to use simulate Guzi interactions

## Install
1. Make a virtual environment with python >= 3.8
2. Install requirements : ```$ pip install -r requirements.txt```

## Run tests

```python
python -m unittest
```

## Usage

```bash
usage: simulator.py [-h] -u USER_COUNT -d DAYS -f FREQUENCY
                    [-x {date,guzis_on_road,average_daily_guzi,user_count}]
                    [-y {date,guzis_on_road,average_daily_guzi,user_count} [{date,guzis_on_road,average_daily_guzi,user_count} ...]]

Simulate Guzi interactions

optional arguments:
  -h, --help            show this help message and exit
  -u USER_COUNT         number of users to simulate
  -d DAYS               number of days simulation should last
  -f FREQUENCY          days between each graph point
  -x {date,guzis_on_road,average_daily_guzi,user_count}
                        x axe
  -y {date,guzis_on_road,average_daily_guzi,user_count} [{date,guzis_on_road,average_daily_guzi,user_count} ...]
                        y axe
```

For example :

```bash
# 
python simulator/simulator.py -u 100 -d 100 -f 10 -x date -y user_count
```
