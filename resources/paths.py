wsdl_info = {
    'invio': 'resources/wsdl/WS_AsincronoInvioDati730/InvioTelematicoSpeseSanitarie730p.wsdl',
    'esito': 'resources/wsdl/WS_Ricevute/EsitoInvio/EsitoInvioDatiSpesa730Service.wsdl',
    'errore': 'resources/wsdl/WS_Ricevute/DettaglioErrori-CSV/DettaglioErrori730Service.wsdl',
    'ricevuta': 'resources/wsdl/WS_Ricevute/RicevutoPDF/RicevutaPdf730Service.wsdl'
}

schema730 = "resources/schema/730_precompilata.xsd"

crt = "resources/crt/SanitelCF.cer"


def get_wsdl_schema(key):
    schema_path = f"{wsdl_info[key].split('.')[0]}_schema.xsd"
    schema_path_alt = f"{wsdl_info[key].split('.')[0]}_schema1.xsd"

    try:
        with open(schema_path):
            return schema_path
    except FileNotFoundError:
        try:
            with open(schema_path_alt):
                return schema_path_alt
        except FileNotFoundError:
            raise FileNotFoundError("Could not find schema at expected location!")
