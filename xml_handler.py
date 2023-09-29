from time import sleep
from typing import Any
from xmlschema import XMLSchema

from cipher import Cipher
from resources.paths import schema730
from resources.config import XmlClientConfig, set_debug
from xml_type import RootType, ComplexType
from SOAP import Client

set_debug(True)


class XMLHandler(object):

    # inizializza cifrario
    cipher = Cipher()

    def __init__(self, db_row: dict):
        crypter = XMLHandler.cipher.b64encrypt

        # define variables from db_row
        cf_proprietario = db_row['cf-proprietario']
        p_iva = db_row['p-iva']
        datafatt = db_row['datafatt']
        ndoc = db_row['ndoc']
        cf = db_row['cf']
        text_pag_tracciato = "SI" if db_row['pag-tracciato'] == 1 else "NO"
        grantot = db_row['grantot']
        iva1 = db_row['iva1']
        totc = db_row['totc']
        iva_cassa = db_row['iva-cassa']

        # generate xml
        self.xml = RootType(
            'precompilata',
            schema730,
            proprietario=ComplexType(
                cfProprietario=crypter(cf_proprietario)
            ),
            documentoSpesa=[
                ComplexType(
                    idSpesa=ComplexType(
                        pIva=p_iva,
                        dataEmissione=datafatt,
                        numDocumentoFiscale=ComplexType(
                            dispositivo=1,
                            numDocumento=ndoc
                        )
                    ),
                    dataPagamento=datafatt,
                    flagOperazione='I',
                    cfCittadino=crypter(cf),
                    pagamentoTracciato=text_pag_tracciato,
                    tipoDocumento='F',
                    flagOpposizione=0,
                    voceSpesa=[
                        ComplexType(
                            tipoSpesa='SP',
                            importo=grantot,
                            naturaIVA=iva1
                        ),
                        ComplexType(
                            tipoSpesa='SP',
                            importo=totc,
                            naturaIVA=iva_cassa
                        )
                    ]
                )
            ]
        )

        # print xml to console
        # print(xml)

        self.cf_proprietario = cf_proprietario

    def generate_xml(self):
        self.xml.write_to_file('output.xml')

    def validate_xml(self):
        # validate xml
        print("Validating XML...", end='')
        print("Error:", XMLSchema(schema730).validate(str(self.xml)))

    @staticmethod
    def print_esito(info):
        (nInviati, nAccolti, nWarnings, nErrori) = info
        print()
        print('Inviati: ' + str(nInviati))
        print('Accolti: ' + str(nAccolti))
        print('Warnings: ' + str(nWarnings))
        print('Errori: ' + str(nErrori))

    @staticmethod
    def write_file(path: str, data: Any):
        mode = 'wb' if isinstance(data, bytes) else 'wt'

        with open(path, mode) as f:
            f.write(data)

    # send to server
    def send_xml(self):
        crypter = XMLHandler.cipher.b64encrypt

        client = Client(
            user=XmlClientConfig.user,
            password=XmlClientConfig.password,
            config=XmlClientConfig.config
        )

        success, extra = client.send_file(
            cregione=XmlClientConfig.cregione,
            casl=XmlClientConfig.casl,
            cssa=XmlClientConfig.cssa,
            cf_proprietario=self.cf_proprietario,
            pincode_inviante_cifrato=crypter(XmlClientConfig.pincode),
            xml=str(self.xml)
        )

        if success:
            # attende elaborazione
            print('\nWaiting results', end='')
            while not client.is_elaboration_done(extra):
                print('.', end='', flush=True)
                sleep(5)

            # mostra esito
            self.print_esito(client.get_info_esito(extra))

            protocollo = client.get_protocollo(extra)

            print('\nWriting results')

            # ottiene il dettagli degli errori
            csv = client.get_errori_csv(extra)
            if csv is not None:
                csv_path = 'ricevute/errori_' + protocollo + '.csv'
                print('Scrivo errori nel file: ' + csv_path)
                self.write_file(csv_path, csv)

            # ottiene la ricevuta in pdf
            pdf = client.get_ricevuta_pdf(extra)
            if pdf is not None:
                pdf_path = 'ricevute/ricevuta_' + protocollo + '.pdf'
                print('Scrivo ricevuta nel file: ' + pdf_path)
                self.write_file(pdf_path, pdf)

        else:
            print(f"ERROR: {extra}")


if __name__ == '__main__':
    # try with test data
    xml_handler = XMLHandler({
        'cf-proprietario': "PROVAX00X00X000Y",
        'p-iva': '01718520768',
        'datafatt': '2022-01-05',
        'ndoc': 3,
        'cf': "CSNNNA66H45L219N",
        'pag-tracciato': 1,
        'grantot': '28.85',
        'iva1': 'N4',
        'totc': '1.15',
        'iva-cassa': 'N4'
    })

    xml_handler.generate_xml()
    xml_handler.validate_xml()
    xml_handler.send_xml()
