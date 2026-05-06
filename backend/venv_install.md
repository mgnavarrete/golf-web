# Crea y activa venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

# Actualiza pip:
```bash
pip install --upgrade pip
```

# Instala Django + DRF + extras:
```bash
pip install Django djangorestframework django-cors-headers djangorestframework-simplejwt boto3 Pillow
```

# Driver MySQL para Django:
```bash
pip install mysqlclient
```

# Si mysqlclient falla por dependencias, instala esto y reintenta:
```bash
sudo apt install -y default-libmysqlclient-dev pkg-config
pip install mysqlclient
```