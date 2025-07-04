# modbus-bridge
Modbus TCP to serial

## Installation

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv supervisor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt 
sudo cp modbus.conf /etc/supervisor/conf.d/modbus.conf
sudo supervisorctl reload
sudo supervisorctl restart modbus
```

