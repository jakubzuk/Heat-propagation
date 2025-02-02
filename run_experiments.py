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


for position in ["far", "close", "work"]:
    for temp_list in [warm, cold, colder]:
        for i in range(4):
            print("Rozważamy temperatury " + f"{temp_list[0]}" + " i tryb " + f"{i} i ustawienie {position}")
            house = House(19, temp_list, position, i)
            house.draw_house(f"{position}")
            house.main()
            house.draw_to_gif(f"{temp_list[0]}_{i}")
            house.plot_all_day(f"all_{temp_list[0]}_{i}")
            house.plot_results(f"plot_{temp_list[0]}_{i}")
