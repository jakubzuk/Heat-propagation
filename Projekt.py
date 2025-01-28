import numpy as np
import matplotlib.pyplot as plt
import csv

# Temperatury w Jekaterynburgu
# warm: 17.04.2024
# cold: 27.02.2024
# colder: 17.02.2024

ht = 0.5
hx = 0.5

air_density = 1.2  # kg/m^3
spec_heat = 1005    # J/(kg * K)
power = 1200   
diff_coeff = 0.025

heat = power / (air_density * spec_heat * 0.25)

def matrix(n):
    matrix = np.zeros((n, n))
    matrix[0, 0] = -2
    matrix[0, 1] = 1
    matrix[n - 1, n - 1] = -2
    matrix[n - 1, n - 2] = 1
    for i in range(1, n - 1):
        matrix[i, i - 1] = 1
        matrix[i, i] = -2
        matrix[i, i + 1] = 1
    return matrix

def diff_matrix(N, M):
    dX = matrix(N)
    dY = matrix(M)
    L = np.kron(np.eye(M), dX)
    R = np.kron(dY, np.eye(N))
    return L + R

class Room:
    def __init__(self, N, M, times, initial_temperature, time = 0):
        self.N = N
        self.M = M
        self.k = len(times)
        self.t = time
        self.x = np.linspace(0, N, N + 1)
        self.y = np.linspace(0, M, M + 1)
        self.x, self.y = np.meshgrid(self.x, self.y)
        self.u = np.zeros((self.k, N * M))
        self.u[0, :] += initial_temperature
        self.Mat = diff_matrix(self.N, self.M)
        IB1 = [i for i in range(N * M) if i % N == 0]
        IB2 = [i for i in range(N * M) if (i + 1) % N == 0]
        IB3 = [i for i in range(N * M) if i < N]
        IB4 = [i for i in range(N * M) if N * M - N <= i]
        self.walls = list(set(IB1 + IB2 + IB3 + IB4))
        self.interior = [i for i in range(N * M) if i not in self.walls]

        IB1N = [i for i in range(N * M) if (i - 1) % N == 0 and (i not in self.walls)]
        IB2N = [i for i in range(N * M) if (i + 2) % N == 0 and (i not in self.walls)]
        IB3N = [i for i in range(N * M) if i >= N and i < (2 * N) and (i not in self.walls)]
        IB4N = [i for i in range(N * M) if (N * M - 2 * N) <= i and i < (N * M - N) and (i not in self.walls)]
        self.neighbors = list(set(IB1N + IB2N + IB3N + IB4N))
    
    def step(self):
        self.t += 1
        self.u[self.t, :] = self.u[self.t - 1, :] + (ht * diff_coeff) / hx**2 * np.matmul(self.Mat, self.u[self.t - 1, :])
        # self.u[self.t, self.walls] = self.u[self.t, self.neighbors]
        # for i in self.walls:
        #     if (i + 1) in self.neighbors:
        #         self.u[self.t, i] = self.u[self.t, i + 1]
        #     elif (i - 1) in self.neighbors:
        #         self.u[self.t, i] = self.u[self.t, i - 1]
        #     elif (i - self.N) in self.neighbors:
        #         self.u[self.t, i] = self.u[self.t, i - self.N]
        #     elif (i + self.N) in self.neighbors:
        #         self.u[self.t, i] = self.u[self.t, i + self.N]
        #     else:
        #         if (i + 1) in self.interior:
        #             self.u[self.t, i] = self.u[self.t, i + 1]
        #         elif (i - 1) in self.interior:
        #             self.u[self.t, i] = self.u[self.t, i - 1]
        #         elif (i - self.N) in self.interior:
        #             self.u[self.t, i] = self.u[self.t, i - self.N]
        #         elif (i + self.N) in self.interior:
        #             self.u[self.t, i] = self.u[self.t, i + self.N]
        for i in self.walls:
            if (i + 1) in self.neighbors:
                self.u[self.t, i] = self.u[self.t, i + 1]
            elif (i - 1) in self.neighbors:
                self.u[self.t, i] = self.u[self.t, i - 1]
            elif (i - self.N) in self.neighbors:
                self.u[self.t, i] = self.u[self.t, i - self.N]
            elif (i + self.N) in self.neighbors:
                self.u[self.t, i] = self.u[self.t, i + self.N]

        for i in [0, self.N - 1, self.N * (self.M - 1), self.N * self.M - 1]:
            if i == 0:  # Lewy dolny róg
                self.u[self.t, i] = self.u[self.t, i + 1]  
            elif i == self.N - 1:  # Prawy dolny róg
                self.u[self.t, i] = self.u[self.t, i - 1]  
            elif i == (self.N * (self.M - 1)):  # Lewy górny róg
                self.u[self.t, i] = self.u[self.t, i + 1] 
            elif i == (self.N * self.M - 1):  # Prawy górny róg
                self.u[self.t, i] = self.u[self.t, i - 1]  

    def average_temperature(self):
        return np.sum(self.u[self.t, self.interior]) / ((self.N - 2) * (self.M - 2)) 
    
    def show_room(self):
        plt.figure()
        plt.pcolormesh(self.x, self.y, self.u[200, :].reshape(self.M, self.N), shading='auto')
        plt.colorbar(label="Temperatura")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.title("Rozkład temperatury w czasie końcowym")
        plt.show()
        
       
class Window:
    def __init__(self, room, cords):
        self.room = room
        self.cords = cords

class Heater:
    def __init__(self, room, cords, mode = 3):#, power, max_temperature):
        self.room = room
        self.cords = cords
        # self.power = power
        self.mode = mode
        self.modes_temperatures = [7, 12, 15, 19, 23, 28]
        self.max_temperature = self.modes_temperatures[mode]
        # self.heat = self.power / (air_density * spec_heat * 0.25) # Uzupełnić

    def set_mode(self, new_mode):
        if new_mode in [0, 1, 2, 3, 4, 5]:
            self.mode = new_mode 
            self.max_temperature = self.modes_temperatures[self.mode]   
    

class Door:
    def __init__(self, room_1, room_2, cords_1, cords_2):
        self.room_1 = room_1
        self.room_2 = room_2
        self.cords_1 = cords_1
        self.cords_2 = cords_2

class House:
    def __init__(self, initial_temperature, outside_temperatures, heaters_mode, heaters_during_work = 3):
        self.windows = []
        self.heaters = []
        self.initial_temperature = initial_temperature
        self.times = np.arange(0, 86400, ht) 
        # self.times = np.arange(0, 10000, ht)
        self.temperatures = outside_temperatures
        self.heaters_during_work_mode = heaters_during_work
        self.outside_temp_num = 0
        self.energy_used = 0

        room_1 = Room(25, 20, self.times, self.initial_temperature)
        room_2 = Room(15, 20, self.times, self.initial_temperature)
        room_3 = Room(40, 10, self.times, self.initial_temperature)
        self.rooms = [room_1, room_2, room_3]

        window_1_1 = Window(room_1, [300, 325, 350, 375])
        window_1_2 = Window(room_1, [484, 485, 486])
        window_1_3 = Window(room_1, [490, 491, 492, 493])
        window_2_1 = Window(room_2, [289, 290, 291, 292])
        window_2_2 = Window(room_2, [239, 254])
        window_2_3 = Window(room_2, [74, 89, 104, 119, 134])
        self.windows = [window_1_1, window_1_2, window_1_3, window_2_1, window_2_2, window_2_3]

        if heaters_mode == 'close':
            heater_1_1 = Heater(room_1, [301, 326, 351])
            heater_1_2 = Heater(room_1, [459, 460, 461, 462])
            heater_1_3 = Heater(room_1, [466, 467])
            heater_2_1 = Heater(room_2, [274, 275, 276])
            heater_2_2 = Heater(room_2, [73, 88, 103, 118])
            heater_3_1 = Heater(room_3, [61, 62, 63, 64, 65])

        elif heaters_mode == 'far':
            heater_1_1 = Heater(room_1, [323, 348, 373])
            heater_1_2 = Heater(room_1, [48, 73, 98, 123])
            heater_1_3 = Heater(room_1, [198, 223])
            heater_2_1 = Heater(room_2, [46, 61, 76])
            heater_2_2 = Heater(room_2, [17, 18, 19])
            heater_3_1 = Heater(room_3, [61, 62, 63, 64, 65])

        self.heaters = [heater_1_1, heater_1_2, heater_1_3, heater_2_1, heater_2_2, heater_3_1]

        if outside_temperatures[0] < 0:
            for heater in self.heaters:
                heater.set_mode(4)

        if outside_temperatures[0] < -10:
            old_russian_heater_1 = Heater(room_1, [119, 120])
            old_russian_heater_2 = Heater(room_2, [238, 253])
            self.heaters.append(old_russian_heater_1)
            self.heaters.append(old_russian_heater_2)
            for heater in self.heaters:
                heater.set_mode(5)

        door_1 = Door(room_1, room_2, [399, 424], [240, 225]) 
        door_2 = Door(room_1, room_3, [3, 4], [363, 364])
        door_3 = Door(room_2, room_3, [6, 7], [391, 392])

        self.doors = [door_1, door_2, door_3]


    def main(self):
        checking_temp = True
        for t in range(1, len(self.times)):   
            for room in self.rooms:
                # room.t += 1
                room.step()
    
            for window in self.windows:
                window.room.u[t, window.cords] = self.temperatures[self.outside_temp_num]

            if t % 7200 == 0:
                    self.outside_temp_num += 1

            for heater in self.heaters:
                if t == 50400:
                    heater.set_mode(self.heaters_during_work_mode)
                elif t == 122400:
                    heater.set_mode(3)
                if heater.room.average_temperature() <= heater.max_temperature: # Do wymiany
                    heater.room.u[t, heater.cords] += ht * heat
                    self.energy_used += len(heater.cords) * heat
                # heater.room.u[t, heater.cords] = 10000

            for door in self.doors:
                avg_temp = (np.sum(door.room_1.u[t, door.cords_1]) + np.sum(door.room_2.u[t, door.cords_2])) / 4
                door.room_1.u[t, door.cords_1] = avg_temp
                door.room_2.u[t, door.cords_2] = avg_temp
                # door.room_1.u[t, door.cords_1] = 10000
                # door.room_2.u[t, door.cords_2] = 10000
            # for room in self.rooms:
            #     room.u[t, room.walls] = 0
            #     room.u[t, room.interior] = 1000
            #     room.u[t, room.neighbors] = 10000
            # for room in self.rooms:
                # room.u[t, 0] = 10000
                # room.u[t, room.N - 1] = 10000
                # room.u[t, room.N * (room.M - 1)] = 10000
                # room.u[t, room.N * room.M - 1] = 10000
            if t == 50400:
                sum_of_temp = 0
                for room in self.rooms:
                    sum_of_temp += np.sum(room.u[t, :])
                    avg = sum_of_temp / 1200
            if t > 122400 and checking_temp == True:
                sum_of_temp = 0
                for room in self.rooms:
                    sum_of_temp += np.sum(room.u[t, :])
                avg = sum_of_temp / 1200
                if t == 160000:
                    pass
                if avg > 19:
                    print(t - 122400)
                    checking_temp = False
                    # self.show_house_at_time(int(t / 2))


    # def show_house(self):
    #     for room in self.rooms:
    #         room.show_room()
        # self.rooms[0].show_room()
    def show_house(self):
        full_map = self.merge_rooms()
        plt.figure()
        plt.pcolormesh(full_map, shading='auto')
        plt.colorbar(label="Temperatura")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.title("Rozkład temperatury w całym mieszkaniu")
        plt.show()

    def show_house_at_time(self, time):
        time_idx = int(time / ht)  # Przeliczenie czasu na indeks w tablicy danych

        for room in self.rooms:
            room.t = time_idx  # Ustawienie kroku czasowego dla każdego pokoju

        full_map = self.merge_rooms()  # Połączenie map temperatur z poszczególnych pokoi

        plt.figure(figsize=(8, 6))
        plt.pcolormesh(full_map, shading='auto', cmap='inferno')
        plt.colorbar(label="Temperatura [°C]")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.title(f"Rozkład temperatury w całym mieszkaniu (t = {time / 3600} h)")
        plt.show()

    def merge_rooms(self):
        m0 = self.rooms[0].u  
        m1 = self.rooms[1].u  
        m2 = self.rooms[2].u  

        m0_rows, m0_cols = self.rooms[0].M, self.rooms[0].N
        m1_rows, m1_cols = self.rooms[1].M, self.rooms[1].N
        m2_rows, m2_cols = self.rooms[2].M, self.rooms[2].N

        result = np.full((m2_rows + m0_rows, m2_cols), np.nan)

        result[:m2_rows, :] = m2[self.rooms[2].t].reshape(m2_rows, m2_cols)

        result[m2_rows:, :m0_cols] = m0[self.rooms[0].t].reshape(m0_rows, m0_cols)
        result[m2_rows:, m0_cols:] = m1[self.rooms[1].t].reshape(m1_rows, m1_cols)

        return result
    
    def plot_all_day(self):
        fig, axes = plt.subplots(4, 6, figsize=(18, 12))  
        axes = axes.flatten()  

        time_indices = [int(hour * 3600 / ht) for hour in range(24)]  

        for i, time_index in enumerate(time_indices):
            for room in self.rooms:
                room.t = time_index  
            
            full_map = self.merge_rooms()
            im = axes[i].pcolormesh(full_map, shading='auto', cmap='plasma')
            axes[i].set_title(f"{i}:00 h")

        fig.colorbar(im, ax=axes, orientation='horizontal', fraction=0.02, pad=0.05)
        plt.tight_layout()
        plt.show()


    # def merge_rooms(self):
    #     m0 = self.rooms[0].u
    #     m1 = self.rooms[1].u
    #     m2 = self.rooms[2].u

    #     m0_rows, m0_cols = m0.shape
    #     m1_rows, m1_cols = m1.shape
    #     m2_rows, m2_cols = m2.shape

    #     result = np.full((m1_rows + m2_rows, m2_cols), None, dtype=object)


    #     return result

with open("data.csv", 'r') as file:
    temp_csv_reader = csv.DictReader(file)
    warm = []
    cold = []
    colder = []
    for col in temp_csv_reader:
        warm.append(int(col['warm']))
        cold.append(int(col['cold']))
        colder.append(int(col['colder']))

house = House(0, warm, 'close', 0)
house.main()
# house.show_house()
house.plot_all_day()

# house.show_house_at_time(2)
# house.show_house_at_time(3600 * 7)
# house.show_house_at_time(3600 * 10)
# house.show_house_at_time(3600 * 14)
# house.show_house_at_time(3600 * 17)

import matplotlib.animation as animation

def animate_house(house):
    fig, ax = plt.subplots()
    
    full_map = house.merge_rooms()
    heatmap = ax.pcolormesh(full_map, shading='auto', cmap='inferno')
    plt.colorbar(heatmap, label="Temperatura")
    ax.set_title("Rozkład temperatury w całym mieszkaniu")
    
    def update(frame):
        for room in house.rooms:
            room.t = frame  
        full_map = house.merge_rooms()
        heatmap.set_array(full_map.ravel())
        ax.set_title(f"Rozkład temperatury - krok {frame}")

    ani = animation.FuncAnimation(fig, update, frames=len(house.times), interval=0.02, repeat=False)
    plt.show()

animate_house(house)
