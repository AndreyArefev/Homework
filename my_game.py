import random

class Game:
    def __init__(self):
        self.playersturn = ['good', 'evil'][random.randint(0,1)] #рандомно выбираем игрока начинающего игру
        print (f'Первым ходит: {self.playersturn}', end = '\n\n')
        print("Для осуществления действия (движение, атака, лечение), введите координаты клетки с юнитом, пробел, координаты клетки на которую направлено действие (например: a1 a2)", end = '\n\n')
        print ('Уникальные особенности юнитов:\n\tWizard - дальность атаки - 3 клетки в любом направлении, может лечить союзных юнитов\n\tRogue - урон усилен на 50%, может двигаться на 2 клетки в любом направлении\n\tWarrior - здоровья и выносливости на 50% больше', end = '\n\n')
        self.message = " " #здесь будут выводиться подсказки
        self.gameboard = {} #словарь, в котором ключи - координаты, значения - юниты.
        self.width_board = 10 #задаем ширину поля
        self.hight_board = 10 #задаем высоту поля
        self.positions_units() #расставляем юнитов
        self.print_board() #отрисовка поля
        self.main() #делаем ход
        
    def positions_units(self): 
        # стартовая расстановка персонажей на игровом поле
        defolt_unit_list = [Wizard,None,Rogue,None,Warrior] #дефолтный список юнитов
        unit_list = [defolt_unit_list[i%len(defolt_unit_list)] for i in range(self.hight_board)] #создаем список юнитов в зависимости от размера поля
        for i in range(self.hight_board): #расставляем юнитов на поле (заполняем словарь gameboard)
            if  unit_list[i]:
                self.gameboard[(i,0)] = unit_list[i]('good',DictUnit['good'][unit_list[i]])
                self.gameboard[(i,self.width_board-1)] = unit_list[i]('evil',DictUnit['evil'][unit_list[i]])
        self.print_units()
        
    def print_board(self):
        # отрисовка игрового поля
        print('  ', end ='')
        for j in range(self.width_board): 
            print(f' {j+1} |' if j < 9 else f' {j+1}|', end ='')
        print()
        for i in range(self.hight_board):
            print("-"*self.width_board*4)
            print(chr(i+97),end="|")
            for j in range(self.width_board):
                item = self.gameboard.get((i,j),"  ")
                print(str(item)+' |', end = "")
            print()
        print("-"*self.width_board*4)
    
    def parse_input(self):
        # проверка корректности ввода
        try:
            a,b = input().split()
            a = ((ord(a[0])-97), int(a[1:])-1)
            b = (ord(b[0])-97, int(b[1:])-1)
        except:
            self.message = "Неверный формат входных данных"
            return((-1,-1),(-1,-1))     
        else:    
            if a[0] < self.hight_board and b[0] < self.hight_board and a[1] < self.width_board and b[1] < self.width_board:
                return (a,b)
            else:
                self.message = "Выход за пределы поля"
                return((-1,-1),(-1,-1)) 
        
    def change_side(func): #функция-декоратор, для смены хода после успешного действия
        def _wrapper(self, *args, **kwargs):
            if func(self, *args, **kwargs):
                if self.playersturn == 'evil':
                    self.playersturn = 'good'
                else : self.playersturn = 'evil'
                self.stamina_restore()  #восстановление выносливости
            else:
                print('Данный юнит не может совершить это действие')
        return _wrapper 
    
    @change_side
    def move(self, unit_pos, endpos, startpos):
        if unit_pos.unit_move(endpos, startpos): #проверка может ли выбранный юнит переместиться в указанную точку 
            self.gameboard[endpos] = self.gameboard[startpos] #перемещение
            del self.gameboard[startpos] #освобождение стартовой клетки
            return True

    @change_side
    def attack(self, unit_pos, target, endpos, startpos):
        if unit_pos.unit_attack(endpos, startpos): #проверка может ли выбранный юнит провести атаку по указанной точке и проводит атаку при возможности
            target.unit_taking_damage(unit_pos.damage) #вызов функции по получению урона юнитом который атакован
            self.death() #удаление погибших
            return True

    @change_side
    def health(self, unit_pos, target): 
        if isinstance (unit_pos, Wizard):
            unit_pos.unit_healer(target)
            return True

    def stamina_restore(self): #метод вызывающий функцию для частичного восстановления выносливости всем юнитам в конце хода
        for i in self.gameboard.values():
            i.unit_stamina_restore()

    def death(self): #функция удаления погибших юнитов
        self.gameboard = {i: j for i, j in self.gameboard.items() if j.health > 0}   

    def main(self):#метод реализующий ход игрока
        while True:
            print(self.message)
            if self.is_win(): #проверка на победу
                print ('GAME OVER')
                break
            startpos,endpos = self.parse_input() #проверяем корректность введенных координат 
            if startpos != (-1,-1): #если координаты корректны
                self.print_board() #отрисовка поля
                print(f'Ход {self.playersturn}')
                target = self.gameboard.get(endpos,' ') #определяем клетку на которую направлено наше действие (перемещение, атака. лечение)
                try:
                    unit_pos = self.gameboard[startpos]  #определяем юнита котроым мы будем осуществлять действие
                except:
                    self.message = "Недопустимый ход, повторите ход" #если мы выбрали стартовую клетку без юнита                   
                else:
                    if unit_pos.side != self.playersturn: #проверяет чей сейчас ход
                        self.message = "Ход другого игрока!"
                        continue    
                    if target == ' ': #если конечная точка пустая, то вызывает функцию по перемещению
                        self.move(unit_pos, endpos, startpos)
                    elif target.side != self.playersturn: #если в конечной точке враг, то вызывает функцию по атаке
                        self.attack(unit_pos, target, endpos, startpos)               
                    elif target.side == self.playersturn: #если в конечной точке союзник, то вызывает функцию по лечению
                        self.health(unit_pos, target)                             
                    self.print_units() #печатаем текущие характеристики юнитов
            
    def print_units(self):  #выводим текущие характеристики юнитов
        print ('Текущие характеристики юнитов:')
        for i in self.gameboard.values():
            print (f'{i} {type(i).__name__} {i.side} Здоровье: {i.health}. Выносливость: {i.stamina}')
        print()
  
    def is_win(self): #функция определения победы
        if len(list(filter (lambda j: j.side == 'good', self.gameboard.values()))) == 0:  
            self.message = "EVIL WIN!"
            return True
        elif len(list(filter (lambda j: j.side == 'evil', self.gameboard.values()))) == 0:  
            self.message = "GOOD WIN!"
            return True
        else: return False     
        
class Unit:
    def __init__(self, side, name):
        self.side = side #сторона добро/зло
        self.name = name 
        self.max_health = 100 
        self.max_stamina = 100
        self.health = self.max_health
        self.stamina = self.max_stamina
        self.damage = 10 #наносимый урон
        self.mobility = 1 #дальность перемещения за один ход
        self.range_attack = 1 #дальность атаки за один ход
   
    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name

    def unit_move (self, x, y): #метод определяет как ходит юнит
        if x != y and abs(y[0] - x[0]) <= self.mobility and abs(y[1] - x[1]) <= self.mobility and self.stamina >= 10:
            self.stamina -= 10
            return True
        else: return False

    def unit_attack (self, x, y): #метод определяет как юнит атакует
        if x != y and abs(y[0] - x[0]) <= self.range_attack and abs(y[1] - x[1]) <= self.range_attack and self.stamina >= 20:
            self.stamina -= 20
            return True
        else: return False 

    def unit_taking_damage (self, damage): #метод определяет как юнит получает урон
        self.health -= damage

    def unit_stamina_restore (self): #метод определяет как юнит восстанавливает выносливость каждый ход
        if self.stamina <= self.max_stamina-2:
            self.stamina += 2 

class Wizard(Unit): 
    def __init__(self, side, name):
        super().__init__(side, name)
        self.range_attack = 3
    
    def unit_healer (self, frendly_unit): #уникальный метод мага позволяющий лечить союзников
        if self.stamina <= self.max_stamina-10:
            frendly_unit.health += 10
            self.stamina -= 20
        
class Rogue(Unit):
     def __init__(self, side, name):
        super().__init__(side, name)
        self.damage = 15
        self.mobility = 2
        
class Warrior(Unit):
     def __init__(self, side, name):
        super().__init__(side, name)
        self.max_health = 150
        self.max_stamina = 150
        self.health = self.max_health
        self.stamina = self.max_stamina

DictUnit = {'good' : {Wizard : "🧙", Rogue : "🏹", Warrior : "🗡 "}, 'evil' : {Wizard : "🧛", Rogue : "🪓", Warrior : "🛡 "}} #словарь обозначений юнитов        
Game()