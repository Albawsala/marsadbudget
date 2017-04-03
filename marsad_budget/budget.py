from openpyxl import load_workbook, Workbook

def load_spreedsheet(filename):
    filepath =  ("/tmp/" + filename)
    return  load_workbook(filepath, data_only=True, read_only=True)

def unit_of_work(spreedsheet):
#_______________varibales init____________
    To_return = [] # Table To return
    tmp_dict = {}
#________________Loading first Sheet____________________
    sheet = spreedsheet.get_sheet_by_name(spreedsheet.get_sheet_names()[0])
    data = enumerate(list(sheet.rows)[2:])
    for i,row in data:
        if ( row[0].value and  row[1].value and row[2].value ) :
            print row[0].value
            tmp_dict["ar"] = row[0].value
            tmp_dict["fr"] = row[1].value
            tmp_dict["budget"] = int(row[2].value)
            #gestion
            if (row[3].value) :
                 tmp_dict["remunerations_publique"] =  int(row[3].value)
            else:
                 tmp_dict["remunerations_publique"] =  0


            if (row[4].value) :
                 tmp_dict["moyens_des_services"] =  int(row[4].value)
            else:
                 tmp_dict["moyens_des_services"] =  0

            if (row[5].value) :
                 tmp_dict["interventions_publiques"] =  int(row[5].value)
            else:
                 tmp_dict["interventions_publiques"] =  0

            if (row[6].value) :
                 tmp_dict["disposition_urgence"] =  int(row[6].value)
            else:
                 tmp_dict["disposition_urgence"] =  0


            if (row[7].value) :
                 tmp_dict["Avantages_dette_publique"] =  int(row[7].value)
            else:
                 tmp_dict["Avantages_dette_publique"] =  0


            if (row[8].value) :
                 tmp_dict["gestion"] =  int(row[8].value)
            else:
                 tmp_dict["gestion"] =  0


            if (row[9].value) :
                 tmp_dict["Investissements_direct"] =  int(row[9].value)
            else:
                 tmp_dict["Investissements_direct"] =  0


            if (row[10].value) :
                 tmp_dict["financement_public"] =  int(row[10].value)
            else:
                 tmp_dict["financement_public"] =  0


            if (row[11].value) :
                 tmp_dict["Depenses_developpement_urgence"] =  int(row[11].value)
            else:
                 tmp_dict["Depenses_developpement_urgence"] =  0


            if (row[12].value) :
                 tmp_dict["ressources_exterieures_affectees"] =  int(row[12].value)
            else:
                 tmp_dict["ressources_exterieures_affectees"] =  0


            if (row[13].value) :
                 tmp_dict["Remboursement_dette_publique"] =  int(row[13].value)
            else:
                 tmp_dict["Remboursement_dette_publique"] =  0
            if (row[14].value) :
                 tmp_dict["developpement"] =  int(row[14].value)
            else:
                 tmp_dict["developpement"] =  0

            To_return.append(tmp_dict)
            tmp_dict = {}
    return To_return

if __name__ == "__main__":
    unit_of_work(load_spreedsheet("LF2017.xlsx"))
