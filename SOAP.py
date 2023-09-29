from io import BytesIO
from requests import Session
from requests.auth import HTTPBasicAuth
from urllib.parse import urlparse
from zeep import Client as zeepClient
from zeep.transports import Transport as zeepTransport
from zipfile import ZipFile, ZIP_DEFLATED

from resources.config import Config
from resources.paths import wsdl_info


def zip_data(filename: str, data: str):
    zip_stream = BytesIO()
    with ZipFile(zip_stream, mode='w', compression=ZIP_DEFLATED) as z:
        z.writestr(f"{filename}.xml", bytes(data, 'ascii'))

    return zip_stream.getvalue()


def zip_to_csv(data: bytes):
    zip_stream = BytesIO()
    zip_stream.write(data)
    with ZipFile(zip_stream, mode='r', compression=ZIP_DEFLATED) as z:
        data = z.read(z.namelist()[0])

    return data.decode('ascii')


class Client:

    def __init__(self, user, password, config: Config):
        self._domain = config.url
        session = Session()
        session.verify = config.https_verify
        session.auth = HTTPBasicAuth(user, password)
        self._transport = zeepTransport(session=session)
        self.invio = self.__create_service__(wsdl_info['invio'])
        self.esito = self.__create_service__(wsdl_info['esito'])
        self.errore = self.__create_service__(wsdl_info['errore'])
        self.ricevuta = self.__create_service__(wsdl_info['ricevuta'])

    def __create_service__(self, wsdl):
        client = zeepClient(wsdl=wsdl, transport=self._transport)
        endpoint = f"https://{self._domain}{urlparse(client.service._binding_options['address']).path}"

        return client.create_service(
            client.service._binding.name.text,
            endpoint
        )

    def send_file(self, cregione, casl, cssa, cf_proprietario, pincode_inviante_cifrato, xml):
        file_name = 'file' # xml and zip file name must be the same (file.xml --> file.zip)

        # se va in errore qui, aggiorna zeep
        res_invio = self.invio.inviaFileMtom(
            nomeFileAllegato=f"{file_name}.zip",
            pincodeInvianteCifrato=pincode_inviante_cifrato,
            datiProprietario={
                'codiceRegione': cregione,
                'codiceAsl': casl,
                'codiceSSA': cssa,
                'cfProprietario': cf_proprietario
            },
            documento=zip_data(file_name, xml)
        )

        #print(resInvio)

        if res_invio['codiceEsito'] == '000':
            return True, {
                'pinCode': pincode_inviante_cifrato,
                'protocollo': res_invio['protocollo']
            }
        else:
            return False, res_invio['descrizioneEsito']

    def __get_esito(self, dati_richiesta):
        return self.esito.EsitoInvii(DatiInputRichiesta=dati_richiesta)

    def get_info_esito(self, dati_richiesta):
        res_esito = self.__get_esito(dati_richiesta)
        e = res_esito['esitiPositivi']['dettagliEsito'][0]
        return e['nInviati'], e['nAccolti'], e['nWarnings'], e['nErrori']

    def is_elaboration_done(self, dati_richiesta):
        res_esito = self.__get_esito(dati_richiesta)
        stato = res_esito['esitiPositivi']['dettagliEsito'][0]['stato']
        return False if stato == 0 or stato == 1 else True

    @staticmethod
    def get_protocollo(dati_richiesta):
        return dati_richiesta['protocollo']

    def get_errori_csv(self, dati_richiesta):
        res_errore = self.errore.DettaglioErrori(DatiInputRichiesta=dati_richiesta)
        #print(resErrore)
        if res_errore['esitoChiamata'] == '0':
            file_zip = res_errore['esitiPositivi']['dettagliEsito']['csv']
            csv = zip_to_csv(file_zip)
            return csv
        else:
            return None

    def get_ricevuta_pdf(self, dati_richiesta):
        res_ricevuta = self.ricevuta.RicevutaPdf(DatiInputRichiesta=dati_richiesta)
        #print(resRicevuta)
        if res_ricevuta['esitoChiamata'] == '0':
            pdf = res_ricevuta['esitiPositivi']['dettagliEsito']['pdf']
            return pdf
        else:
            return None
