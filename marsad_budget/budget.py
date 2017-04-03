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
            tmp_dict["budget"] = row[2].value
            To_return.append(tmp_dict)
            tmp_dict = {}
    return To_return

if __name__ == "__main__":
    unit_of_work(load_spreedsheet("LF2017.xlsx"))
