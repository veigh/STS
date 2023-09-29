# Script for Creation of XML files for STSClient

A collection of python scripts to create and send an
XML by reading from a database
(currently in development).

High level summary / steps:
1. Read unprocessed rows from a mysql db
2. Create an XML file based on the info of each row
  and send it against `invioSS730p.sanita.finanze.it`
3. Mark the rows as 'processed' in the db
4. Repeat

## Setup

### Required python packages

Make sure you have installed all the pip packages
listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

### Running a database

You need a running instance of a mysql database.
If you don't have one, please make sure you have
a proper db setup prior to running this script.

If you just want to test things out, you can use this
command (you need a working installation of docker
for this). This should be done only for testing purposes.

```bash
docker run \
  --rm -it -d \
  --name some-mysql \
  -e MYSQL_ROOT_PASSWORD=my-secret-pw \
  -e MYSQL_DATABASE=your_database \
  -e MYSQL_USER=your_username \
  -e MYSQL_PASSWORD=your_password \
  -p 3306:3306 \
  mysql
```

### Configuration

It's critical to review all the settings in
[resources/config.py](resources/config.py).

The important parts are the `XmlClientConfig` and
the `DbConfig` classes.

```python
# in XmlClientConfig
user = 'A9AZOS61'
password = 'Salve123'
pincode = '5485370458'
(cregione, casl, cssa) = '604-120-010011'.split('-')

# in DbConfig
connect_config = {
    'user': 'your_username',
    'password': 'your_password',
    'host': '127.0.0.1',
    'database': 'your_database',
    'raise_on_warnings': True
}

table_name = 'your_table'
status_field = '`flag`'
status_message_field = '`status-message`'
```

Please update the values according to your situation.

### Running

If everything is set up, run the script by
starting the main.py:

```bash
python main.py
```

This will run in an endless loop, so it needs to
interrupted / stopped from outside.

## Documentation on Specific Code Parts

### Defining the XML structure

Define your XML structure by importing 
`RootType` and `ComplexType` in python
and building up the structure like this:

```python3
from xml_type import RootType, ComplexType

xml = RootType(
    'precompilata',
    '730_precompilata.xsd',
    proprietario=ComplexType(
        cfProprietario="..."
    ),
    documentoSpesa=[
        ComplexType(
            idSpesa=ComplexType(
                pIva='011852076',
                dataEmissione='2022-11-30',
                numDocumentoFiscale=ComplexType(
                    dispositivo=1,
                    numDocumento=999
                )
            ),
            dataPagamento='2022-11-30',
            flagOperazione='I',
            cfCittadino="...",
            pagamentoTracciato='SI',
            tipoDocumento='F',
            flagOpposizione=0,
            voceSpesa=[
                ComplexType(
                    tipoSpesa='SP',
                    importo='28.85',
                    naturaIVA='N4'
                ),
                ComplexType(
                    tipoSpesa='SP',
                    importo='1.15',
                    naturaIVA='N4'
                )
            ]
        )
    ]
)
```

Don't forget to name the variables exactly like the 
XML tags you want to get.

### View the result

After defining the structure, you can view the generated 
XML file like this:

```python3
# xml = ...

print(xml)
```

### Output to file

You can write the XML file to filesystem like this:

```python3
# xml = ...

xml.write_to_file('output.xml')
```

This will generate the `output.xml` in the current
working directory.

### Encryption

You can encrypt strings with the public key included
in `resources/crt/SanitelCF.cer`. To do this, simply
import the `Cipher` class and create the cipher instance.
Then, encrpyt and encode the encrypted bytes with base64:

```python3
from cipher import Cipher

cipher = Cipher("resources/crt/SanitelCF.cer")
cipher.b64encrypt("S3cReT_StR1N5")
```

### XML Validation

You can validate the generated XML against any 
schema. For convenience, the `730_precompilata.xsd`
schema is accessible as `schema730` via `resources.paths`.
So just import XMLSchema and validate like this:

```python3
from xmlschema import XMLSchema

from resources.paths import schema730

# xml = ...

XMLSchema(schema730).validate(str(xml))
```

### Sending the XML

Sending is done by instantiating a Client
and using the `client.send_file` method.
The constructor of the client takes a `config`
parameter, which can be obtained by importing
one of the predefined configs in `resources/config`.

```python3
from resources.config import XmlClientConfig
from SOAP import Client

client = Client(
    user=...,
    password=...,
    config=XmlClientConfig.test_config  # examplary
)

client.send_file(
    ...
)
```

### Debug Mode

To enable more verbose output by zeep - the SOAP client
used in this project - set the debug mode.

```python3
from resources.config import set_debug

set_debug(True)
```
