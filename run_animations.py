import csv
from Project import House

with open("data.csv", 'r') as file:
    temp_csv_reader = csv.DictReader(file)
    warm = []
    cold = []
    colder = []
    for col in temp_csv_reader:
        warm.append(int(col['warm']))
        cold.append(int(col['cold']))
        colder.append(int(col['colder']))

# W celu uruchomienia animacji dla innych warunków (układu grzejników, temperatur zewnętrznych) należy zdefiniować 
# obiekt house (instancję klasy House) w analogiczny sposób:
# house = House(lista_temperatur[0], lista_temperatur, "ustawienie grzejników", pokretlo_gdy_poza_domem)
# gdzie listy temperatur: warm, cold, colder
# ustawienia grzejników: "work", "far", "close"
# pokretlo_gdy_poza_domem: 0, 1, 2, 3, 4, 5

house = House(19, warm, "work", 0)
house.draw_house("work_anim")
house.main()
house.animate_house()

