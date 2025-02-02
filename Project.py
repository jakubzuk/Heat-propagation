import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
import json

def load_constants(file_path="physical_and_numerical_data.json"):
    with open(file_path, "r") as file:
        constants = json.load(file)
    return constants

constants = load_constants()

ht = constants["ht"]
hx = constants["hx"]
air_density = constants["air_density"]
spec_heat = constants["spec_heat"]
power = constants["power"]  
diff_coeff = constants["diff_coeff"]

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
            if i == 0:  
                self.u[self.t, i] = self.u[self.t, i + 1]  
            elif i == self.N - 1:  
                self.u[self.t, i] = self.u[self.t, i - 1]  
            elif i == (self.N * (self.M - 1)):  
                self.u[self.t, i] = self.u[self.t, i + 1] 
            elif i == (self.N * self.M - 1):  
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
    def __init__(self, room, cords, mode=5):
        self.room = room
        self.cords = cords 
        self.mode = mode
        self.modes_temperatures = [7, 12, 15, 19, 24, 28]
        self.max_temperature = self.modes_temperatures[mode]
        self.surroundings = self.get_surroundings()
        self.on = True

    def set_mode(self, new_mode):
        if new_mode in [0, 1, 2, 3, 4, 5]:
            self.mode = new_mode 
            self.max_temperature = self.modes_temperatures[self.mode]   

    def get_surroundings(self):
        surroundings = []
        for cord in self.cords:
            if ((cord + 1) in self.room.interior) and ((cord + 1) not in self.cords):
                surroundings.append(cord + 1)
            if ((cord - 1) in self.room.interior) and ((cord - 1) not in self.cords):
                surroundings.append(cord - 1)
            if ((cord + self.room.N) in self.room.interior) and ((cord + self.room.N) not in self.cords):
                surroundings.append(cord + self.room.N)
            if ((cord - self.room.N) in self.room.interior) and ((cord - self.room.N) not in self.cords):
                surroundings.append(cord - self.room.N)
        return surroundings

    def get_neighboring_temperature(self, t):       
        return np.mean(self.room.u[t, self.surroundings])
    

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
        self.ind = 0
        self.temperatures = outside_temperatures
        self.heaters_during_work_mode = heaters_during_work
        self.outside_temp_num = 0
        self.energy_used = []
        self.average_temperatures = []

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
        window_3_1 = Window(room_3, [22, 23])
        self.windows = [window_1_1, window_1_2, window_1_3, window_2_1, window_2_2, window_2_3, window_3_1]

        if heaters_mode == 'close':
            heater_1_1 = Heater(room_1, [301, 326, 351])
            heater_1_2 = Heater(room_1, [459, 460, 461])
            heater_1_3 = Heater(room_1, [468, 469])
            heater_2_1 = Heater(room_2, [275, 276])
            heater_2_2 = Heater(room_2, [88, 103, 118, 133])
            heater_2_3 = Heater(room_2, [238, 253, 268])
            heater_3_1 = Heater(room_3, [61, 62, 63, 64, 65])
            self.heaters = [heater_1_1, heater_1_2, heater_1_3, heater_2_1, heater_2_2, heater_2_3, heater_3_1]

        elif heaters_mode == 'far':
            heater_1_1 = Heater(room_1, [323, 348])
            heater_1_2 = Heater(room_1, [48, 73, 98])
            heater_1_3 = Heater(room_1, [32, 33, 34, 35, 36])
            heater_2_1 = Heater(room_2, [76, 91])
            heater_2_2 = Heater(room_2, [27, 28, 29])
            heater_2_2 = Heater(room_2, [136, 151, 166, 181])
            heater_2_3 = Heater(room_2, [24, 25, 26])
            heater_3_1 = Heater(room_3, [41, 42, 43, 44, 45])
            self.heaters = [heater_1_1, heater_1_2, heater_1_3, heater_2_1, heater_2_2, heater_2_3, heater_3_1]

        elif heaters_mode == 'work':
            heater_1_1 = Heater(room_1, [298, 323, 348])
            heater_1_2 = Heater(room_1, [459, 460, 461])
            heater_1_3 = Heater(room_1, [101, 126, 151])
            heater_1_4 = Heater(room_1, [401, 426, 451])
            heater_1_4 = Heater(room_1, [35, 36])
            heater_2_1 = Heater(room_2, [106, 121])
            heater_2_2 = Heater(room_2, [27, 28])
            heater_2_3 = Heater(room_2, [277, 278, 279])
            heater_2_4 = Heater(room_2, [163])
            heater_3_1 = Heater(room_3, [53, 54, 55, 56, 57])
            heater_3_2 = Heater(room_3, [75, 76])
            heater_3_3 = Heater(room_3, [346, 347])
            self.heaters = [heater_1_1, heater_1_2, heater_1_3, heater_1_4, heater_2_1, heater_2_2, heater_2_3, heater_2_4, heater_3_1, heater_3_2, heater_3_3]

        door_1 = Door(room_1, room_2, [399, 424], [240, 225]) 
        door_2 = Door(room_1, room_3, [3, 4], [363, 364])
        door_3 = Door(room_2, room_3, [6, 7], [391, 392])

        self.doors = [door_1, door_2, door_3]


    def main(self):
        checking_temp = True
        heat_generated = 0
        for t in range(1, len(self.times)):   
            for room in self.rooms:
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
                for heater in self.heaters:
                    if heater.get_neighboring_temperature(t) >= heater.max_temperature:
                        heater.on = False
                        heater.time = 0
                    elif heater.get_neighboring_temperature(t) <= heater.max_temperature - 1: 
                        heater.on = True
                    if heater.on:
                        heater.room.u[t, heater.cords] += ht * heat
                        heat_generated += len(heater.cords) * heat
                                   
            self.energy_used.append(heat_generated)

            for door in self.doors:
                avg_temp = (np.sum(door.room_1.u[t, door.cords_1]) + np.sum(door.room_2.u[t, door.cords_2])) / 4
                door.room_1.u[t, door.cords_1] = avg_temp
                door.room_2.u[t, door.cords_2] = avg_temp
            sum_of_temp = 0
            for room in self.rooms:
                sum_of_temp += np.sum(room.u[t, :])
            avg = sum_of_temp / 1200
            if t == 50400:
                print("temperatura przed wyjściem: " + f"{avg}")
            if t >= 122400 and checking_temp == True:
                if t == 122400:
                    print("temperatura po powrocie: " + f"{avg}")
                m = [room.average_temperature() for room in self.rooms]
                if all([m[0] >= 19, m[1] >= 19, m[2] >= 19]) and avg > 18:
                    print(t - 122400)
                    checking_temp = False
            self.average_temperatures.append(avg)

    def draw_house(self, name):
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_xlim(0, 40)
        ax.set_ylim(0, 30)
        ax.set_xticks(np.arange(41))
        ax.set_yticks(np.arange(31))
        ax.grid(True, which='both', color='gray', linestyle='--', linewidth=0.5)
        ax.set_aspect('equal')
        
        for i, room in enumerate(self.rooms):
            for wall in room.walls:
                if room == self.rooms[1]:
                    x = wall % room.N + 25
                else:
                    x = wall % room.N
                if room == self.rooms[2]:
                    y = wall // room.N
                else:
                    y = wall // room.N + 10 
                ax.add_patch(patches.Rectangle((x, y), 1, 1, color='black'))
                
        for window in self.windows:
            for cord in window.cords:
                if window.room == self.rooms[1]:
                    x = cord % window.room.N + 25
                else:
                    x = cord % window.room.N
                y = cord // window.room.N + 10
                if window.room == self.rooms[2]:
                    y = cord // window.room.N
                else:
                    y = cord // window.room.N + 10
                ax.add_patch(patches.Rectangle((x, y), 1, 1, color='blue'))
                
        for heater in self.heaters:
            for cord in heater.cords:
                if heater.room == self.rooms[1]:
                    x = cord % heater.room.N + 25
                else:
                    x = cord % heater.room.N
                if heater.room == self.rooms[2]:
                    y = cord // heater.room.N 
                else:
                    y = cord // heater.room.N + 10
                ax.add_patch(patches.Rectangle((x, y), 1, 1, color='orange'))

        for door in self.doors:
            for cord in door.cords_1:
                if door.room_1 == self.rooms[1]:
                    x = cord % door.room_1.N + 25
                else:
                    x = cord % door.room_1.N
                if door.room_1 == self.rooms[2]:
                    y = cord // door.room_1.N
                else:
                    y = cord // door.room_1.N + 10
                ax.add_patch(patches.Rectangle((x, y), 1, 1, color='white'))

            for cord in door.cords_2:
                if door.room_2 == self.rooms[1]:
                    x = cord % door.room_2.N + 25
                else:
                    x = cord % door.room_2.N
                if door.room_2 == self.rooms[2]:
                    y = cord // door.room_2.N
                else:
                    y = cord // door.room_2.N + 10
                ax.add_patch(patches.Rectangle((x, y), 1, 1, color='white'))
            
                
        ax.text(12, 20, 'Pokój 1', fontsize=12, fontweight='bold', color='black', ha='center')
        ax.text(32, 20, 'Pokój 2', fontsize=12, fontweight='bold', color='black', ha='center')
        ax.text(20, 5, 'Pokój 3', fontsize=12, fontweight='bold', color='black', ha='center')
        
        plt.savefig(f"{name}_house.png", bbox_inches='tight')
        plt.close()


    def show_house_at_time(self, time, name):
        time_idx = int(time / ht)  

        for room in self.rooms:
            room.t = time_idx  

        full_map = self.merge_rooms()  

        plt.figure(figsize=(8, 6))
        plt.pcolormesh(full_map, shading='auto', cmap='plasma', vmin=min(self.temperatures), vmax=35)
        plt.colorbar(label="Temperatura [°C]")
        plt.xlabel("x")
        plt.ylabel("y")
        # plt.title(f"Rozkład temperatury w całym mieszkaniu (t = {time / 3600} h)")
        # plt.show()
        plt.savefig(f"{name}_{time}.png")
        plt.close()

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
    
    def plot_all_day(self, name):
        fig, axes = plt.subplots(3, 4, figsize=(18, 12))
        # fig, axes = plt.subplots(4, 6, figsize=(18, 12))  
        axes = axes.flatten()  

        time_indices = [int(hour * 7200 / ht) for hour in range(12)]  

        for i, time_index in enumerate(time_indices):
            for room in self.rooms:
                room.t = time_index  
            
            full_map = self.merge_rooms()
            im = axes[i].pcolormesh(full_map, shading='auto', cmap='plasma', vmin=-5, vmax=35)
            axes[i].set_title(f"{2 * i}:00 h")

        bar = fig.colorbar(im, ax=axes, orientation='horizontal', fraction=0.03, pad=0.05)
        bar.set_label('Temperatura (°C)')
        plt.savefig(f"{name}.png")
        plt.close()
        print("Energia: " + f"{self.energy_used[-1]}")

    def plot_results(self, name):
        time_hours = self.times[:len(self.energy_used)] / 3600

        fig, ax1 = plt.subplots(figsize=(10, 5))

        ax1.set_xlabel('Czas (h)')
        ax1.set_ylabel('Ciepło oddane (J)', color='red')
        ax1.plot(time_hours, self.energy_used, color='red', label="Oddane ciepło")
        ax1.tick_params(axis='y', labelcolor='red')

        ax2 = ax1.twinx()
        ax2.set_ylabel('Średnia temperatura (°C)', color='blue')
        ax2.plot(time_hours, self.average_temperatures, color='blue', label="Średnia temperatura")
        ax2.tick_params(axis='y', labelcolor='blue')

        fig.tight_layout()
        plt.title("Oddane ciepło i średnia temperatura w czasie")
        plt.grid()
        plt.savefig(f"{name}.png", bbox_inches='tight')
        plt.close()

    def draw_to_gif(self, name):
        for time in range(13):
            self.show_house_at_time(3600 * (7 + time / 12), name)
            self.show_house_at_time(3600 * (17 + time / 12), name)


    def animate_house(self):
        fig, ax = plt.subplots()
        
        full_map = self.merge_rooms()
        heatmap = ax.pcolormesh(full_map, shading='auto', cmap='plasma', vmin=min(self.temperatures), vmax=35)
        plt.colorbar(heatmap, label="Temperatura")
        ax.set_title("Rozkład temperatury w całym mieszkaniu")
        
        def update(frame):
            for room in self.rooms:
                room.t = frame  
            full_map = self.merge_rooms()
            heatmap.set_array(full_map.ravel())
            ax.set_title(f"Rozkład temperatury - krok {frame}")

        ani = animation.FuncAnimation(fig, update, frames=len(self.times), interval=0.005, repeat=False)
        plt.show()




