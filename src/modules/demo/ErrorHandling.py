from jsonschema import validate
import json

class ErrorHandling:

    @staticmethod
    def check_messsages_correctnes(input_data):


        if input_data['event']['event'] == 'breakdown':
            f = open('./modules/demo/schemas/PS_HP_brokenvehicle.json', )
            json_schema = json.load(f)
            validate(instance=input_data, schema=json_schema)



    '''
    checkCLOs


    checkParcels

    checkMessageStructure

    checkIDs


    checkLocations
    organization:
        -elta
        -ps, hp
    event_type ->
       -border, crossBorder ()
       -brokenVehicle
       -adHock

    parcels -> payweight == 1 :)
    parcels -> destination -> checkiraj latitude longitude
                -> eliti -> latitude/longitude so lahko do his


    slo-cro
        - urban (vozimo do his)
        - backbone (vozimo od post) (crossboarder)-> pase na un file ....
    elta
        - pocekiraj ce je int .. oz number ce je paywight 1
        - urban (vozimo do his)-> ne rabi pasat na lokacije
        - backbone (do post) ->

    Clos neglede na event type vedno ista struktura:
    clos -> state -> parcels (zavrni ce ni parclov) -> list string lahko je empty
                            -> location -> latitude, longitude, pa station

                    -> parcel -> list vseh parcele object preveri lokacije, station pa vse ostalo
                                    -> id stirng
                                    -> source/destination definiran z 4 paramtri:)
                                    -> organization

    clos ->  id string
                info ->organization
            -> location -> country, latitude, longitude, station

            -> organization  in country same :)
            -> Organization isti na parclih ..
            -> remaing plan -> steps notri

    event -> ce je mora imeti event_type

    -> request in organization (pri vseh parclih in clojih)

    TODO FUTURE
    -> event -> backbone, cross


    '''
