import logging.config

# Xml Client config
test = True


class XmlClientConfig(object):

    class Config:

        def __init__(self, _type: str, url: str, https_verify: bool):
            self.type = _type
            self.url = url
            self.https_verify = https_verify

    # instantiate test config and prod config
    test_config = Config(
        _type='test',
        url='invioSS730pTest.sanita.finanze.it',
        https_verify=False
    )

    prod_config = Config(
        _type='prod',
        url='invioSS730p.sanita.finanze.it',
        https_verify=True
    )

    config = (test_config if test else prod_config)

    user = 'A9AZOS61'
    password = 'Salve123'
    pincode = '5485370458'
    (cregione, casl, cssa) = '604-120-010011'.split('-')


# Database config
class DbConfig(object):

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


# Python debug config
__debug_config = ({
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'zeep.transports': {
            'level': 'DEBUG',
            'propagate': True,
            'handlers': ['console'],
        },
    }
})


def set_debug(_debug):
    if _debug:
        logging.config.dictConfig(__debug_config)
