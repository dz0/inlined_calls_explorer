# data  fragments from interim/2017/05/tab.csv

csv = """
	Год / Year	Кварталы / Quarters			
		I	II	III	IV
1. Сводные показатели / Aggregated indicators					
1.1. Валовой внутренний продукт1) / Gross domestic product1)					
Объем ВВП, млрд.рублей /GDP, bln rubles					
20152)	83233	18568	19858	21967	22840
20162)	86044	18816	20430	22721	24077
2017		200913)			

Год / Year	Кварталы / Quarters	Янв. Jan.	Фев. Feb.	Март Mar.	Апр. Apr.	Май May	Июнь June	Июль July	Август Aug.	Сент. Sept.	Окт. Oct.	Нояб. Nov.	Дек. Dec.			
		I	II	III	IV												
1.2. Индекс промышленного производства1) / Industrial Production index1)																	
Индекс промышленного производства, 
в % к соответствующему периоду предыдущего года / percent of corresponding period of previous year																	
2015	99,2	99,9	98,3	99,5	99,1	100,0	98,2	101,2	98,2	97,6	99,1	98,5	100,2	99,7	98,4	101,0	98,1
2016	101,3	101,1	101,5	101,0	101,7	99,2	103,8	100,3	101,0	101,5	102,0	101,4	101,5	100,1	101,6	103,4	100,2
2017		100,1				102,3	97,3	100,8	102,3	105,6							
в % к предыдущему периоду / percent of previous period																	
2015		82,8	102,6	103,9	112,3	73,9	99,8	112,5	95,6	97,6	103,2	100,5	101,4	103,1	105,0	101,9	109,1
2016		84,4	103,1	103,3	113,1	74,7	104,4	108,8	96,3	98,1	103,8	99,9	101,5	101,7	106,6	103,6	105,8
2017		83,1				76,2	99,4	112,7	97,7	101,2							
период с начала отчетного года в % к соответствующему периоду предыдущего года / period from beginning of reporting year as percent of corresponding period of previous year																	
2015						100,0	99,1	99,9	99,4	99,1	99,1	99,0	99,1	99,2	99,1	99,3	99,2
2016						99,2	101,5	101,1	101,1	101,1	101,3	101,3	101,3	101,2	101,2	101,4	101,3
2017						102,3	99,7	100,1	100,7	101,7							
	Янв. Jan.	Фев. Feb.	Март Mar.	Апр. Apr.	Май May	Июнь June	Июль July	Август Aug.	Сент. Sept.	Окт. Oct.	Нояб. Nov.	Дек. Dec.
1.2.1. Индексы производства по видам деятельности1) (без исключения сезонности и фактора времени) / Industrial Production indices by Industry (without seasonal and time factor adjustment)												
"""

import pandas as pd

from csv2df.specification import Definition, Specification, SPEC
from csv2df.reader import Reader, open_csv
from csv2df.parser import extract_tables
from csv2df.emitter import Emitter

def get_dataframes(csvfile, spec=SPEC):
    tables = [t for csv_segment, pdef in Reader(csvfile, spec).items()
              for t in extract_tables(csv_segment, pdef)]
    # print(list(tables))
    
    emitter = Emitter(tables)
    dfa = emitter.get_dataframe(freq='a')
    dfq = emitter.get_dataframe(freq='q')
    dfm = emitter.get_dataframe(freq='m')
    return dfa, dfq, dfm

main = Definition(units={
                        'млрд.рублей': 'bln_rub', 
                        'период с начала отчетного года в % к соответствующему периоду предыдущего года': 'ytd',
                        'в % к соответствующему периоду предыдущего года': 'yoy',
                        'в % к предыдущему периоду': 'rog'
                        })

main.append(varname='GDP',
            text='Объем ВВП',
            required_units=['bln_rub'])

main.append(varname="INDPRO",
            text="Индекс промышленного производства",
            required_units=["yoy", "rog"],
            desc="Промышленное производство")


spec1 = Specification(default=main)

import io
csvfile1 = io.StringIO(csv )

def test():
    dfa1, dfq1, dfm1 = get_dataframes(csvfile1, spec1)
    return dfa1, dfq1, dfm1 
