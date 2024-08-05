# API version
The supported API version is [1.3.0](https://etherpad.org/doc/v2.1.1/index.html#_http_api)

This python api enables easy interaction with the Etherpad API.  Etherpad is a collaborative editor provided by the Etherpad Foundation.  http://etherpad.org

# 1 Installation

```shell
pip install pyetherpadlite
```

# 2 Preparation

If you are using a self hosted Etherpad server, you will need to specify an API Key after installation before using the API.  (See https://github.com/ether/etherpad-lite for installation details).

Your secret api key should be placed in the base installation (etherpad-client folder) in a text file named APIKEY.txt.  Many linux text editors automatically create an extra newline character at the end of the file, so I recommend simply executing the following command to set your api key without a newline character:
    
```shell
echo -n "myapikey" > APIKEY.txt
```

Once you have created the APIKEY.txt file, you will need to edit the py_etherpad.py wrapper to set your API key. Edit the 'apiKey' variable and set it to the same key as defined in your APIKEY.txt file.

# 3 Basic usage

```python
from py_etherpad import EtherpadLiteClient
myPad = EtherpadLiteClient('EtherpadFTW','http://beta.etherpad.org/api')
# Change the text of the etherpad
myPad.setText('testPad','New text from the python wrapper!')
```

# 4 More details

See the `src/py_etherpad/__init__.py` file for further details on the methods and parameters available for the API.
Nearly all calls from the [official API](https://etherpad.org/doc/v2.1.1/]) work as in the official documentation described.

# 5 Test coverage

Actually im writing the tests for each topic.

Already finished:
- Groups
- Pads

Nearly finished:
- Author

# 6 License

Apache License

# 7 Credit
This python API-Wrapper is a Fork from [devjones](https://github.com/devjones/PyEtherpadLite) and is inspired by [TomNomNom's php client](https://github.com/TomNomNom/etherpad-lite-client)
