import pandas as pd
from tabulate import tabulate

df = pd.read_csv("offerte.csv", sep=";", )
df.insert(0, 'ID', range(len(df)))
print("Ecco qui la tabella di input con le offerte dell'asta BOT:", "\n", df.head(30))

BOTrichiesti = sum(df['Quantità'])

BOTofferti = 7000
DurataBOT= 360
BOTassegnati = BOTofferti

#ordina prezzo in modo decrescente
df.sort_values(by=['Prezzo Domandato'], ascending = False, inplace = True)

#seleziona solo le offerte cumulate che arrivano a 7000
threshold = BOTofferti
sum = 0
cum_sum = []

for i, item in df.iterrows():
    if sum < threshold:
        if item['Quantità'] < threshold-sum:
            cum_sum.append(item['Quantità'])
            sum += item['Quantità']
        else:
            cum_sum.append(threshold-sum)
            sum += threshold-sum

    else:
        cum_sum.append(0)

#seleziona la prima e seconda metà dei 7000
first_half = []
sum = 0

for i, item in df.iterrows():
    if sum < threshold//2:
        if item['Quantità'] < threshold//2-sum:
            first_half.append(item['Quantità'])
            sum += item['Quantità']
        else:
            first_half.append(threshold//2-sum)
            sum += threshold-sum

    else:
        first_half.append(0)

df['Somma Cumulata'] = cum_sum
df['Prima Metà'] = first_half
df['Seconda Metà'] = df['Somma Cumulata'] - df['Prima Metà']
print(df.head(15))

#calcola variabili per trovare il PMA
PMP = ((df['Seconda Metà'] [3])*(df['Prezzo Domandato'] [3]) + (df['Seconda Metà'] [4])*(df['Prezzo Domandato'] [4]) + (df['Seconda Metà'] [5])*(df['Prezzo Domandato'] [5]) + (df['Seconda Metà'] [6])*(df['Prezzo Domandato'] [6]))/(threshold//2)
print("\nPMP:", PMP)

RL = (100-PMP)/PMP
print("\nRL:", RL)

Rendimento = RL - 0.0025
print("\nRendimento:", Rendimento)

PMA = 100/(1+Rendimento)
print("\nPMA:", PMA)

#escludi prezzi superiori al PMA
newdf = df[['ID', 'Operatore', 'Richiesta', 'Quantità','Prezzo Domandato', 'Somma Cumulata']].copy()

low_pma = []
for i, item in newdf.iterrows():
    if item['Prezzo Domandato'] < PMA:
        low_pma.append(item['Prezzo Domandato'])
    else:
        low_pma.append(0)

newdf['Prezzi inferiore al PMA'] = low_pma

newdf.drop(newdf.index[newdf['Prezzi inferiore al PMA'] == 0], inplace = True)
print("The new database without the 1st offer (Price > PMA) is the following:", "\n", newdf.head(15))

#seleziona la prima e seconda metà senza il prezzo superiore al PMA
first_half_2 = []
sum = 0

for i, item in newdf.iterrows():
    if sum < threshold//2:
        if item['Somma Cumulata'] < threshold//2-sum:
            first_half_2.append(item['Somma Cumulata'])
            sum += item['Somma Cumulata']
        else:
            first_half_2.append(threshold//2-sum)
            sum += threshold-sum

    else:
        first_half_2.append(0)
newdf['Nuova Prima Metà'] = first_half_2
newdf['Nuova Seconda Metà'] = newdf['Somma Cumulata'] - newdf['Nuova Prima Metà']
#print(newdf.head(15))

#calcola nuove variabili senza il prezzo superiore al PMA
PMP2 = ((newdf['Nuova Prima Metà'] [1])*(newdf['Prezzo Domandato'] [1]) + (newdf['Nuova Prima Metà'] [2])*(newdf['Prezzo Domandato'] [2]) + (newdf['Nuova Prima Metà'] [3])*(newdf['Prezzo Domandato'] [3])) / (threshold//2)
print("\nPMP_2:", PMP2)

RL2 = (100-PMP2)/PMP2
print("\nRL_2:", RL2)

Rendimento2 = RL2 + 0.01
print("\nRendimento_2:", Rendimento2)

PE = 100/(1+Rendimento2)
print("\nPE:", PE)

#elimina offerte con prezzi inferiori al PE
newdf.drop(newdf.index[newdf['Prezzo Domandato'] < PE], inplace = True)
df.drop(df.index[df['Prezzo Domandato'] < PE], inplace = True)

#trova % di riparto
dom_offerta = (df['Quantità'] [0:6].sum())
print("\nOfferta parziale:", dom_offerta)

PrezzoMinimo = (df['Prezzo Domandato'][6])
print("\nPrezzo Minimo Aggiudicatorio:", PrezzoMinimo)

QuantitàMancanti = BOTofferti - dom_offerta

#loop per vedere la quantità offerta al prezzo minimo aggiudicabile di 95.82
sum_2 = 0
for i, item in df.iterrows():
    if item['Prezzo Domandato'] == PrezzoMinimo:
        sum_2 += item['Quantità']

PercentualeRiparto = QuantitàMancanti / sum_2
print("\n% di Riparto:", PercentualeRiparto)

NewQuant_A = (df['Quantità'][6]) * PercentualeRiparto
NewQuant_B = (df['Quantità'][7]) * PercentualeRiparto

PrezzoMassimo = (newdf['Prezzo Domandato'][1])
Rendimento_3 = (100-PrezzoMassimo)/PrezzoMassimo
R = Rendimento_3 - 0.001

Prezzo = 100/(1+R)
if Prezzo < PMA:
    print("\nPrezzo è minore del PMA e sarà il prezzo richiesto all'operatore A:", Prezzo)

#elabora tabella finale dei risultati
finaldf = df[['ID', 'Operatore', 'Richiesta', 'Quantità', 'Prezzo Domandato']].copy()

#aggiorna la tabella con i nuovi valori
finaldf.at[0, 'Prezzo Domandato'] = Prezzo
finaldf.at[6, 'Quantità'] = NewQuant_A
finaldf.at[7, 'Quantità'] = NewQuant_B

#pulisci ed elimina le offerte in avanzo
finaldf.drop(finaldf.index[df['Prezzo Domandato'] < PrezzoMinimo], inplace = True)
print(finaldf.head(15))

#calcola prezzo medio ponderato
df_by_price = finaldf.groupby(['Prezzo Domandato'],as_index=False)[['Quantità']].sum()
index = pd.MultiIndex.from_arrays([finaldf['Prezzo Domandato'], finaldf['Operatore']], names=('Prezzo Domandato', 'Operatore'))
ser = pd.Series(finaldf['Quantità'].values, index=index, name="Quantità").to_frame()
df_by_price.sort_values(by=['Prezzo Domandato'], ascending = False, inplace = True)

print(ser)
ser.to_csv ('assegnazioni.csv')

PrezzoMedioPonderato = (((df_by_price['Prezzo Domandato'] [4])*(df_by_price['Quantità'] [4])) + ((df_by_price['Prezzo Domandato'] [3])*(df_by_price['Quantità'] [3])) + ((df_by_price['Prezzo Domandato'] [2])*(df_by_price['Quantità'] [2])) + ((df_by_price['Prezzo Domandato'] [1])*(df_by_price['Quantità'] [1])) + ((df_by_price['Prezzo Domandato'] [0])*(df_by_price['Quantità'] [0]))) / (BOTassegnati - df_by_price['Quantità'] [5] )

#crea tabella risultati finali
data = {'Variables': ['Durata BOT', 'BOT offerti', 'BOT richiesti', 'BOT assegnati', 'Prezzo medio ponderato', 'Rendimento lordo', 'Prezzo massimo accolto in asta', 'Prezzo minimo', 'Riparto prezzo minimo', 'Prezzo di esclusione', 'Prezzo massimo accoglibile'],
        'Values': [DurataBOT, BOTofferti, BOTrichiesti, BOTassegnati, PrezzoMedioPonderato, RL2, PrezzoMassimo, PrezzoMinimo, PercentualeRiparto, PE, PMA]}

tableresults= pd.DataFrame(data)
print(tabulate(tableresults, showindex=False, headers=tableresults.columns))
tableresults.to_csv ('finalresults.csv')
