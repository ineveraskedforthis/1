import time
import random
import pygame
import sys
from pygame.locals import *
from math import *
from AI import *
from statetemplates import *
from CONSTANTS import *

TICK = 0
VILLAGE_ID = 0
# TRADING_FREQ = 30

LAST_ID = 0
FOOD_PRICE = [0] * 500
WHEAT_PRICE = [0] * 500
SERVICES_PRICE = [0] * 500
CLOTH_PRICE = [0] * 500
WOOL_PRICE = [0] * 500
POPULATION = [0] * 500

PRICES = dict()
for i in TAGS:
    PRICES[i] = [0 for i in range(500)]


#money
MONEY = ['barter', 'money1']
MONEY_PRECIOUS_METAL_RATIO = dict()
for i in MONEY:
    MONEY_PRECIOUS_METAL_RATIO[i] = 1
MONEY_PRECIOUS_METAL_RATIO['barter'] = 0

class World():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.agents = list()
        self.map = Map(self)
        self.time = 0

    def update(self):
        print(self.time)
        self.map.update()
        for i in self.agents:
            i.update()
        self.time += 1

    def get_cell(self, x, y):
        return self.map.get_cell(x, y)

    def print_pops(self):
        # self.map.print_pops()
        for i in self.agents:
            i.print_pops()

    def print_all(self):
        for i in self.agents:
            i.print_enterprises()
        # self.print_pops()

    def get_pops_list(self):
        tmp = [['name', 'size', 'savings']]
        for i in self.agents:
            if i.is_pop:
                tmp.append(i.get_list())
        return tmp

    def get_total_money(self):
        global m1
        tmp = 0
        # print('===================================')
        for i in self.agents:
            tmp += i.savings.get('money1')
            # print('{0:40s} {1:20d}'.format(i.name, i.savings.get('money1')))
        tmp += m1.savings.get('money1')
        # print('{0:40s} {1:20d}'.format('market', m1.savings.get('money1')))
        # print('==============',tmp,'=====================')
        return tmp


class Map():
    def __init__(self, world):
        self.world = world
        self.cells = [[Cell(world, self, i, j) for i in range(world.x)] for j in range(world.y)]

    def update(self):
        for i in self.cells:
            for j in i:
                j.update()

    def get_cell(self, x, y):
        return self.cells[x][y]


class Cell():
    def __init__(self, world, map1, i, j, name = None, owner = None):
        if name == None:
            self.name = str(i) + ' ' + str(j)
        else:
            self.name = name
        self.world = world
        self.map = map1
        self.i = i
        self.j = j
        self.markets = set()
        self.enterprises = set()
        self.pop = HomelessHumanBeing(self.world, 0, name = 'homeless_peasants ' + self.name, cell = self)
        self.tiles = []
        self.owner = owner

    def update(self):
        for i in self.markets:
            i.update()
        for i in self.tiles:
            i.update()

    def add_enterprise(self, x, i):
        self.tiles[i].add_enterprise(x)

    def add_market(self, x):
        self.markets.add(x)

    def get_market(self, currency):
        for i in self.markets:
            if i.money_type == currency:
                return i
        return None

    def get_enterprises(self):
        tmp = set()
        for i in self.tiles:
            tmp = tmp.union(i.enterprises)
        return tmp

    def get_population(self):
        tmp = 0
        for i in self.tiles:
            tmp += i.get_population()
        return tmp + self.pop.size

    def add_tile(self, x):
        self.tiles.append(x)

    def get_enterprises_list(self):
        tmp = [['name', 'size', 'workers', 'savings', 'produced', 'price']]
        for i in self.tiles:
            for j in i.enterprises:
                tmp.append(j.get_list())
        return tmp

    def set_owner(self, x):
        self.owner = x

    def get_pops_list(self):
        tmp = [['name', 'size', 'savings']]
        tmp.append(self.pop.get_list())
        for i in self.tiles:
            tmp.append(i.pop.get_list())
            for j in i.enterprises:
                tmp.append(j.pop.get_list())
        return tmp

    def get_local_army(self):
        if self.owner != None:
            return self.owner.offices['soldiers']
        else:
            return None

class Tile():
    def __init__(self, cell, terrain = 'plains', resource = [], owner = None, development = 'vild', housing = 0, housing_price = 1, name = 'Tile'):
        self.savings = Savings()
        self.AI = StateMachine(self, TileIdle)
        self.cell = cell
        self.terrain = terrain
        self.name = name
        self.free_space = TILE_SIZE - housing
        self.resource = resource
        self.owner = owner
        self.development = development
        self.enterprises = set()
        self.pop = NormalHumanBeing(cell.world, 0, parent = cell.pop, cell = cell, free = True, name = self.name + ' burgs', cave = self)
        self.housing = housing
        self.free_space -= housing
        self.housing_price = housing_price
        if self.owner == None:
            self.price = 0
        else:
            self.price = INF

    def update(self):
        self.update_housing()

    def add_enterprise(self, x):
        self.enterprises.add(x)
        self.free_space -= x.get_size()

    def add_housing(self, x):
        self.free_space -= x
        self.housing += x

    def set_pop(self, x):
        self.pop = x

    def get_housing(self):
        return self.housing

    def get_population(self):
        tmp = 0
        for i in self.enterprises:
            tmp += i.pop.size
        return tmp + self.pop.size

    def update_housing(self):
        tmp = self.pop.size - self.get_housing()
        if tmp > 0:
            self.pop.demote(tmp)

    def set_owner(self, x):
        self.owner = x

    def build(self, host, x):
        print(x)
        if x['building']['size'] > self.free_space:
            return
        for i in host.chosen_building['building']['building_cost']:
            host.stash.inc(i[0], -i[1])
        tmp = EnterpriseWithWorkers(self.cell.world,
                                    x['building'],
                                    owner = host,
                                    name = self.name + ' ' + x['building']['name'],
                                    tile = self, size = 100,
                                    cell = self.cell,
                                    starting_pop_size = 0,
                                    starting_money = 0,
                                    currency = host.currency)
        self.add_enterprise(tmp)
        return tmp

    def add_resource(self, x):
        self.resource.append(x)

    def satisfy(self, reqs):
        print('_____SATISFY_____')
        print(reqs, self.resource)
        if self.free_space < 100:
            return False
        for i in reqs:
            if not i in self.resource:
                return False
        return True


class Village(Tile):
    def __init__(self, cell, resource = ['soil', 'grass'], owner = None, housing = 100, housing_price = None, name = 'village'):
        global VILLAGE_ID
        VILLAGE_ID += 1
        Tile.__init__(self, cell, terrain = 'plains', resource = resource, owner = owner, development = 'rural', housing = housing, housing_price = housing_price, name = 'village ' + str(VILLAGE_ID))
        farm = Farm(world, name = 'farm ' + self.name, tile = self, size = 100, cell = cell, starting_money = 100000, starting_pop_size = 100)
        self.add_enterprise(farm)

class PasturesTile(Tile):
    def __init__(self, cell, resource = ['grass'], owner = None, housing = 100, housing_price = None):
        global VILLAGE_ID
        VILLAGE_ID += 1
        Tile.__init__(self, cell, terrain = 'plains', resource = resource, owner = owner, development = 'rural', housing = housing, housing_price = housing_price, name = 'village ' + str(VILLAGE_ID))
        pastures = Pastures(world, name = 'pastures ' + self.name, tile = self, size = 100, cell = cell, starting_money = 100000, starting_pop_size = 100)
        self.add_enterprise(pastures)

class SmallTown(Tile):
    def __init__(self, cell, resource = [], owner = None, housing = 100, housing_price = None):
        global VILLAGE_ID
        VILLAGE_ID += 1
        Tile.__init__(self, cell, terrain = 'plains', resource = resource, owner = owner, development = 'rural', housing = housing, housing_price = housing_price, name = 'town ' + str(VILLAGE_ID))
        self.pop.size = 400
        bakery = Bakery(world, name = 'bakery ' + self.name, tile = self, size = 100, cell = cell, starting_money = 100000, starting_pop_size = 400, currency = 'money1')
        weavershop = WeaverShop(world, name = 'weavershop ' + self.name, tile = self, size = 100, cell = cell, starting_money = 100000, starting_pop_size = 200, currency = 'money1')
        self.add_enterprise(bakery)
        self.add_enterprise(weavershop)

class Forest(Tile):
    def __init__(self, cell, owner = None):
        global VILLAGE_ID
        VILLAGE_ID += 1
        Tile.__init__(self, cell, terrain = 'plains', resource = ['forest'], owner = owner, name = 'village ' + str(VILLAGE_ID))
        woodcutter = EnterpriseWithWorkers(world,
                                           attributes = buildings['woodcutter'],
                                           name = self.name + 'woodcutter',
                                           tile = self,
                                           size = 100,
                                           cell = cell,
                                           starting_pop_size = 10,
                                           starting_money = 1000000)
        self.add_enterprise(woodcutter)


class MarketOrder():
    def __init__(self, typ, tag, owner, amount, price):
        self.typ = typ
        self.tag = tag
        self.owner = owner
        self.amount = amount
        self.price = price

    def get_list(self):
        return([self.typ, self.tag, self.owner.get_name(), self.amount, self.price])


class Market():
    """Basic trading between cell's agents"""
    def __init__(self, money, owner = None, cell = None):
        self.cell = cell
        self.owner = owner
        self.money_type = money
        self.savings = Savings(False)
        self.stash = Stash()
        self.buy_orders = dict()
        self.sell_orders = dict()
        self.planned_money_to_spent = dict()
        self.total_cost_of_placed_goods = dict()
        self.tmp_planned_money_to_spent = dict()
        self.tmp_total_cost_of_placed_goods = dict()
        self.max_price = dict()
        self.total_sold = dict()
        self.total_sold_cost = dict()
        self.total_sold_new = dict()
        self.total_sold_cost_new = dict()
        self.sells = dict()
        self.tmp_sells = dict()
        self.taxes = dict()
        for tag in TAGS:
            self.taxes[tag] = 0
            self.planned_money_to_spent[tag] = 0
            self.total_cost_of_placed_goods[tag] = 0
            self.tmp_planned_money_to_spent[tag] = 0
            self.tmp_total_cost_of_placed_goods[tag] = 0
            self.sell_orders[tag] = set()
            self.buy_orders[tag] = set()
            self.max_price[tag] = 0
            self.total_sold[tag] = [0] * 30
            self.total_sold_cost[tag] = [0] * 30
            self.total_sold_new[tag] = 0
            self.total_sold_cost_new[tag] = 0
            self.sells[tag] = []
            self.tmp_sells[tag] = []

    def update(self):
        for tag in TAGS:
            #print('______________________________')
            #print(tag)
            #print(self.tmp_planned_money_to_spent[tag])
            #print('______________________________')
            self.planned_money_to_spent[tag] = self.tmp_planned_money_to_spent[tag]
            self.tmp_planned_money_to_spent[tag] = 0
            self.total_cost_of_placed_goods[tag] = self.tmp_total_cost_of_placed_goods[tag]
            self.tmp_total_cost_of_placed_goods[tag] = 0
            self.total_sold[tag] = self.total_sold[tag][1:] + [self.total_sold_new[tag]]
            self.total_sold_new[tag] = 0
            self.total_sold_cost[tag] = self.total_sold_cost[tag][1:] + [self.total_sold_cost_new[tag]]
            self.total_sold_cost_new[tag] = 0
            self.sells[tag] = self.tmp_sells[tag]
            self.tmp_sells[tag] = []

    def set_taxes(self, tag, x):
        self.taxes[tag] = x

    def buy(self, tag, buyer, amount, money):
        if buyer.savings.get(self.money_type) < money:
            money = buyer.savings.get(self.money_type)
        self.tmp_planned_money_to_spent[tag] += money
        # print('money', tag, money, self.guess_tag_cost(tag, amount))
        tmp = []
        for i in self.sell_orders[tag]:
            tmp.append(i)
        tmp.sort(key = lambda x: x.price)
        i = 0
        j = 0
        total_spendings = 0
        y = money
        while i < len(tmp) and amount > 0:
            tmp_amount = 0
            while i < len(tmp) and tmp[i].price == tmp[j].price:
                tmp_amount += tmp[i].amount
                i += 1
            if (money - total_spendings) < amount * tmp[j].price:
                amount = (money - total_spendings) // tmp[j].price
            if tmp_amount <= amount:
                for k in range(j, i):
                    total_spendings += self.execute_sell_order(tmp[k], tmp[k].amount, buyer)
                amount -= tmp_amount
            else:
                u_amount = amount
                for k in range(j, i):
                    amount -= int((tmp[k].amount / tmp_amount) * u_amount)
                    total_spendings += self.execute_sell_order(tmp[k], int((tmp[k].amount / tmp_amount) * u_amount), buyer)
                for k in range(j, i):
                    if tmp[k].amount > 0 and amount > 0:
                        total_spendings += self.execute_sell_order(tmp[k], 1, buyer)
                        amount -= 1
            j = i
        if amount > 0 and money > 0:
            price = (money - total_spendings) // amount
            self.new_order('BUY', tag, amount, price, buyer)
        self.clear_empty_sell_orders(tag)
        return total_spendings

    def sell(self, tag, seller, amount, price):
        if amount > seller.stash.get(tag):
            amount = seller.stash.get(tag)
        self.tmp_total_cost_of_placed_goods[tag] += amount * price
        tmp = []
        for i in self.buy_orders[tag]:
            tmp.append(i)
        tmp.sort(key = lambda x: -x.price)
        i = 0
        j = 0
        while i < len(tmp) and amount > 0 and tmp[i].price >= price:
            tmp_amount = 0
            while i < len(tmp) and tmp[i].price == tmp[j].price:
                tmp_amount += tmp[i].amount
                i += 1
            if tmp_amount <= amount:
                for k in range(j, i):
                    self.execute_buy_order(tmp[k], tmp[k].amount, seller)
                amount -= tmp_amount
            else:
                u_amount = amount
                for k in range(j, i):
                    amount -= int((tmp[k].amount / tmp_amount) * u_amount)
                    self.execute_buy_order(tmp[k], int((tmp[k].amount / tmp_amount) * u_amount), seller)
                for k in range(j, i):
                    if tmp[k].amount > 0 and amount > 0:
                        self.execute_buy_order(tmp[k], 1, seller)
                        amount -= 1
            j = i
        if amount > 0:
            self.new_order('SELL', tag, amount, price, seller)
        self.clear_empty_buy_orders(tag)

    def new_order(self, typ, tag, amount, price, agent):
        if typ == 'SELL':
            tmp = agent.stash.transfer(self.stash, tag, amount)
            self.sell_orders[tag].add(MarketOrder('SELL', tag, agent, tmp, price))

        if typ == 'BUY':
            if price != 0:
                amount = agent.savings.get(agent.currency) // price
                agent.savings.transfer(self.savings, amount * price, self.money_type)
                self.buy_orders[tag].add(MarketOrder('BUY', tag, agent, amount, price))
            else:
                self.buy_orders[tag].add(MarketOrder('BUY', tag, agent, amount, price))

    def execute_buy_order(self, order, amount, seller):
        self.tmp_sells[order.tag].append([amount, order.price])
        order.amount -= amount
        self.savings.transfer(seller.savings, amount * order.price, self.money_type)
        self.savings.transfer(self.owner.savings, amount * self.taxes[order.tag], self.money_type)
        seller.stash.transfer(order.owner.stash, order.tag, amount)
        self.total_sold_new[order.tag] += amount
        self.total_sold_cost_new[order.tag] += amount * order.price
        if LOGGING == True:
            print('buy_order_exe', 'tag', order.tag, 'amount', amount, 'price', order.price, order.owner.name)
        return amount * order.price

    def execute_sell_order(self, order, amount, buyer):
        self.tmp_sells[order.tag].append([amount, order.price])
        order.amount -= amount
        self.stash.transfer(buyer.stash, order.tag, amount)
        buyer.savings.transfer(order.owner.savings, amount * order.price, self.money_type)
        self.savings.transfer(self.owner.savings, amount * self.taxes[order.tag], self.money_type)
        self.total_sold_new[order.tag] += amount
        self.total_sold_cost_new[order.tag] += amount * order.price
        if LOGGING == True:
            print('sell_order_exe', 'tag', order.tag, 'amount', amount, 'price', order.price, order.owner.name)
        return amount * order.price

    def clear_empty_sell_orders(self, tag):
        tmp = set()
        for i in self.sell_orders[tag]:
            if i.amount == 0:
                tmp.add(i)
        for i in tmp:
            self.cancel_sell_order(i)

    def clear_empty_buy_orders(self, tag):
        tmp = set()
        for i in self.buy_orders[tag]:
            if i.amount == 0:
                tmp.add(i)
        for i in tmp:
            self.cancel_buy_order(i)

    def print_orders(self):
        for tag in TAGS:
            for i in self.buy_orders[tag]:
                if i.amount != 0:
                    print(i.get_list())
            for i in self.sell_orders[tag]:
                print(i.get_list())
        print('__________________________________')

    def clear_agent_orders(self, agent, tag):
        self.clear_agent_buy_orders(agent, tag)
        self.clear_agent_sell_orders(agent, tag)

    def clear_agent_sell_orders(self, agent, tag):
        tmp = set()
        for i in self.sell_orders[tag]:
            if i.owner == agent:
                tmp.add(i)
        for i in tmp:
            self.cancel_sell_order(i)

    def clear_agent_buy_orders(self, agent, tag):
        tmp = set()
        for i in self.buy_orders[tag]:
            if i.owner == agent:
                tmp.add(i)
        for i in tmp:
            self.cancel_buy_order(i)

    def get_money_on_hold(self, agent):
        tmp = 0
        for tag in TAGS:
            for i in self.buy_orders[tag]:
                if i.owner == agent:
                    tmp += i.amount * i.price
        return tmp

    def cancel_buy_order(self, order):
        self.savings.transfer(order.owner.savings, order.amount * order.price, self.money_type)
        self.buy_orders[order.tag].discard(order)

    def cancel_sell_order(self, order):
        self.stash.transfer(order.owner.stash, order.tag, order.amount)
        self.sell_orders[order.tag].discard(order)

    def check_cost(self, list_of_goods):
        cost = 0
        for i in list_of_goods:
            cost += self.check_tag_cost(i[0], i[1])
        return cost

    def guess_cost(self, list_of_goods):
        cost = 0
        for i in list_of_goods:
            cost += self.guess_tag_cost(i[0], i[1])
        return cost

    def check_tag_cost(self, tag, amount):
        tmp = []
        for i in self.sell_orders[tag]:
            tmp.append(i)
        tmp.sort(key = lambda x: x.price)
        i = 0
        j = 0
        cost = 0
        for i in tmp:
            if i.amount <= amount:
                cost += i.amount * i.price
                amount -= i.amount
            elif amount > 0:
                cost += amount * i.price
                amount = 0
        if amount > 0:
            return INF
        return cost

    def guess_tag_cost(self, tag, amount):
        tmp = []
        for i in self.sell_orders[tag]:
            tmp.append(i)
        tmp.sort(key = lambda x: x.price)
        i = 0
        j = 0
        cost = 0
        for i in tmp:
            if i.amount <= amount:
                cost += i.amount * i.price
                amount -= i.amount
            elif amount > 0:
                cost += amount * i.price
                amount = 0
        #if amount > 0 and len(tmp) > 0:
        #    cost += tmp[-1].price * amount
        #elif amount > 0 and len(tmp) == 0:
        #    cost += INF
        if amount > 0:
            if sum(self.total_sold[tag]) != 0:
                cost += int(self.get_average_tag_price(tag) * amount)
            else:
                cost += 100
        return cost

    def get_total_cost_of_placed_goods_with_price_less_or_equal(self, tag, x):
        cost = 0
        for i in self.tmp_sells[tag]:
            if i[1] <= x:
                cost += i[0] * i[1]
        for i in self.sell_orders[tag]:
            if i.price <= x:
                cost += i.amount * i.price
        return cost

    def get_average_tag_price(self, tag):
        total_count = sum(self.total_sold[tag])
        total_cost = sum(self.total_sold_cost[tag])
        for i in self.sell_orders[tag]:
            total_count += i.amount
            total_cost += i.price * i.amount
        for i in self.buy_orders[tag]:
            total_count += i.amount
            total_cost += i.price * i.amount
        if total_count != 0:
            return total_cost / total_count
        else:
            # return INF
            return 10000

    def find_amount_of_goods_for_buying(self, max_amount, money, goods):
        l = 0
        r = int(max_amount + 1)
        while l + 1 < r:
            #print('!', l, r)
            m = (l + r) // 2
            list_of_goods = []
            for i in goods:
                list_of_goods.append([i[0], i[1] * m])
            if self.guess_cost(list_of_goods) <= money:
                l = m
            else:
                r = m
        return l

    def get_most_profitable_building(self):
        print('__________GET_MOST_PROFIT______________')
        tmp = dict()
        tmp['cost'] = INF
        tmp['building'] = None
        tmp['pure_income'] = -INF
        tile = None
        for t in buildings:
            print(t)
            for tile in self.cell.tiles:
                i = buildings[t]
                if not tile.satisfy(i['requirements']):
                    continue
                print('continue')
                spendings = self.guess_cost(i['input'] * i['throughput'])
                income = self.guess_cost(i['output'] * i['throughput'])
                cost = self.guess_cost(i['building_cost'])
                print(i, spendings, income, cost)
                if income - spendings > tmp['pure_income']:
                    tmp['pure_income'] = income - spendings
                    tmp['cost'] = cost
                    tmp['building'] = i
        return tmp, tile

    def print_profits_per_chain(self):
        print('__________BUILDING________PROFIT________________')
        for t in buildings:
            i = buildings[t]
            spendings = self.guess_cost(i['input'] * i['throughput'])
            income = self.guess_cost(i['output'] * i['throughput'])
            cost = self.guess_cost(i['building_cost'])
            print(i['name'], 'income_per_worker', income - spendings)
            print('cost', i['building_cost'])
        print('______________________________________________')

    def get_table(self):
        tmp = []
        for tag in TAGS:
            for i in self.buy_orders[tag]:
                tmp.append(i.get_list())
            for i in self.sell_orders[tag]:
                tmp.append(i.get_list())
        return sorted(tmp)

    def set_owner(self, x):
        self.owner = x


class Stash():
    def __init__(self):
        self.data = dict()
        for i in TAGS:
            self.data[i] = 0

    def inc(self, tag, x):
        if self.data[tag] + x < 0:
            tmp = -self.data[tag]
        else:
            tmp = x
        self.data[tag] += tmp
        return tmp

    def get(self, tag):
        return self.data[tag]

    def transfer(self, target, tag, amount):
        tmp = self.inc(tag, -amount)
        #print(tmp)
        target.inc(tag, -tmp)
        return -tmp

    def print_all(self):
        for i in TAGS:
            print(i, self.get(i))





class Savings():
    def __init__(self, info = True):
        self.data = dict()
        self.data['barter'] = 0
        self.prev_data = dict()
        self.info = info
        self.income = 0
        self.data['money1'] = 0

    def update(self):
        self.prev_income = self.income
        for i in MONEY:
            if i in self.data:
                self.prev_data[i] = self.data[i]
        self.income = 0

    def set(self, x, currency):
        self.data[currency] = x

    def get(self, currency):
        return self.data[currency]

    def get_estimated_income(self):
        tmp = 0
        for i in MONEY:
            if i in self.data:
                if not (i in self.prev_data):
                    self.prev_data[i] = 0
                tmp += (self.data[i] - self.prev_data[i]) * MONEY_PRECIOUS_METAL_RATIO[i]
        return tmp

    # def inc(self, x, money_type):
    #     if not money_type in self.data:
    #         self.data[money_type] = 0
    #     data = self.data[money_type]
    #     if data + x < 0:
    #         tmp = -data
    #     else:
    #         tmp = x
    #     data += tmp
    #     self.data[money_type] = data
    #     if self.info:
    #         if tmp > 0:
    #             self.income += tmp
    #     return tmp

    def inc(self, x, currency):
        x = int(x)
        a = self.get(currency)
        if a + x < 0:
            tmp = a + x
            self.set(0, currency)
        else:
            self.set(a + x, currency)
            tmp = 0
        return tmp

    def get(self, money_type):
        if money_type in self.data:
            return self.data[money_type]
        return 0

    def transfer(self, target, x, currency):
        x = int(x)
        # global world
        # tst = world.get_total_money()
        tmp = 0
        a = self.get(currency)
        b = target.get(currency)
        # print(a, b, x)
        if a - x >= 0 and b + x >= 0:
            self.inc(-x, currency)
            target.inc(x, currency)
        elif a - x < 0 and b + x >= 0:
            tmp = a - x
            self.set(0, currency)
            target.inc(x + tmp, currency)
        # print(self.get(currency), target.get(currency))
        # if tst != world.get_total_money():
        #     while 1 == 1:
        #         print('ERROR', tst, world.get_total_money(), x)
        #         exit()
        return -tmp


class Agent():
    def __init__(self, world, name = 'agent', cell = None, starting_money = 0, currency = 'money1'):
        if cell != None:
            self.x, self.y = cell.i, cell.j
        else:
            self.x = None
            self.y = None
        self.world = world
        world.agents.append(self)
        self.stash = Stash()
        self.savings = Savings()
        self.cell = cell
        self.name = name
        self.currency = currency
        self.savings.set(starting_money, currency)
        self.is_pop = False
        self.tiles = []

    def update(self):
        # print('update', self.name)
        self.savings.update()
        self.prev_true_savings = self.get_true_savings()
        if self.savings.get('money1') is float:
            print('!!!!!!!!!!!!!!!!!', self.name)
    def buy(self, tag, amount, money, money_type):
        if LOGGING:
            print(self.name, 'try_to_buy', tag, 'amount', amount, 'money', money)
        self.get_local_market(money_type).buy(tag, self, amount, money)

    def sell(self, tag, amount, price, money_type):
        self.get_local_market(money_type).sell(tag, self, amount, price)

    def clear_orders(self, tag, currency):
        if self.get_local_market(currency) != None:
            self.get_local_market(currency).clear_agent_orders(self, tag)

    def get_local_market(self, money):
        if self.cell == None:
            return None
        for i in self.cell.markets:
            if i.money_type == money:
                return i
        return None

    # def get_income(self):
        # return self.savings.get_income()

    def get_estimated_income(self):
        return self.savings.get_estimated_income()

    def get_money_on_market(self):
        if self.cell != None and self.get_local_market(self.currency) != None:
            return self.get_local_market(self.currency).get_money_on_hold(self)
        return 0

    def get_name(self):
        return self.name

    def get_savings(self, curr = 'money1'):
        return self.savings.get(curr)

    def print_pops(self):
        pass

    def print_enterprises(self):
        pass

    def get_true_savings(self):
        return self.savings.get(self.currency) + self.get_money_on_market()

    def buy_tile(self, tile):
        if tile.owner == self:
            return
        if tile.owner == None:
            self.tiles.append(tile)
            tile.set_owner(self)
        else:
            self.savings.transfer(tile.owner.savings, tile.price, self.currency)
            self.tiles.append(tile)
            tile.owner.del_tile(tile)
            tile.set_owner(tile)

    def del_tile(self, tile):
        tmp = []
        for i in self.tiles:
            if tile != i:
                tmp.append(i)
        self.tiles = tmp

class Consumer(Agent):
    def __init__(self, world, needs, size, name = 'consumer', cell = None, starting_money = 0, currency = 'money1', cave = None):
        Agent.__init__(self, world, name = name, cell = cell, starting_money = starting_money, currency = currency)
        self.needs = needs
        self.size = size
        self.cave = cave

    def change_size(self, x):
        self.size = x

    def consume_update(self):
        for i in self.needs:
            self.consume(i)

    def consume(self, tag):
        self.stash.inc(tag, -self.needs[tag] * self.size)

    def update(self):
        Agent.update(self)
        self.consume_update()

    def housing_pay(self):
        if self.cave != None and self.cave.housing_price != None:
            self.savings.transfer(self.cave.savings, self.size * self.cave.housing_price, self.currency)


class Pop(Consumer):
    def __init__(self, world, needs, size, parent = None, AI = BasicPopAI, name = 'pop', cell = None, max_size = None, starting_money = 0, currency = 'money1', cave = None):
        Consumer.__init__(self, world, needs, size, name = name, cell = cell, starting_money = starting_money, currency = currency, cave = cave)
        self.parent = parent
        self.AI = StateMachine(self, AI)
        self.growth_mod = 0
        self.is_pop = True
        self.max_size = max_size

    def update(self):
        if self.size == 0:
            return
        Consumer.update(self)
        if TICK == 0:
            self.growth_update()
            self.growth_mod = 0
        self.AI.update()
        self.housing_pay()

    def set_max_size(self, x):
        self.max_size = x
        if self.max_size <= self.size:
            if self.parent == None:
                self.size = self.max_size
            else:
                self.demote(self.size - self.max_size)

    def consume(self, tag):
        if self.size == 0:
            return
        total_need = int(self.needs[tag] * self.size)
        in_stash = min(self.stash.get(tag), total_need)
        if total_need == 0:
            return
        if tag == 'food':
            self.growth_mod += (in_stash / total_need - 0.5) * 0.04 / 30
        if tag == 'services':
            self.growth_mod += (in_stash / total_need) * 0.01
        Consumer.consume(self, tag)

    def growth_update(self):
        # if self.growth_mod < 0 or self.parent == None:
        self.size = int(self.size * (1 + self.growth_mod))
        # else:
            # self.parent.size += int(self.size * self.growth_mod)

    # def get_savings_per_capita(self):
    #     if self.savings.get() == 0:
    #         return 0
    #     if self.size == 0:
    #         return INF
    #     return self.savings.get() / self.size

    def get_estimated_savings_per_capita(self):
        tmp = 0
        for i in MONEY:
            tmp += (self.get_true_savings()) * MONEY_PRECIOUS_METAL_RATIO[i]
        if self.size == 0:
            return INF
        return tmp // self.size

    def transfer_size(self, target, x):
        x = min(x, self.size)
        self.size -= x
        target.size += x
        # print('transfer ', x, ' from ', self.name, ' to ', target.name)

    def demote(self, x):
        self.transfer_size(self.parent, x)

    def print_to_console(self):
        if self.size != 0:
            print('___________' + self.name + '___________')
            print('size', self.size)
            print('savings', self.savings.get('money1'))
            print('true_savings', self.savings.get(self.currency) + self.get_money_on_market())
            # self.stash.print_all()
            # print('income', self.get_estimated_income())
            # print('growth', self.growth_mod)
            # print('spc', self.get_estimated_savings_per_capita())

    def print_pops(self):
        self.print_to_console()

    def is_full(self):
        if self.max_size == None:
            return False
        return self.size >= self.max_size

    def get_list(self):
        return([self.name, self.size, self.get_true_savings()])

    def get_salary(self):
        return (self.get_true_savings() - self.prev_true_savings) // self.size

class HomelessHumanBeing(Pop):
    def __init__(self, world, size, parent = None, name = 'peasants', cell = None):
        Pop.__init__(self, world, BASIC_NEEDS, size, parent, name = name, cell = cell, AI = HomelessAI)

    def get_salary(self):
        return 0


class NormalHumanBeing(Pop):
    def __init__(self, world, size, parent = None, name = 'burgs', cell = None, free = False, cave = None):
        Pop.__init__(self, world, BASIC_NEEDS, size, parent, name = name, cell = cell, cave = cave)
        self.free = free

    def update(self):
        if self.free:
            self.clear_orders('services', self.currency)
            self.stash.inc('services', -self.stash.get('services'))
            self.stash.inc('services', self.size)
            self.sell('services', self.size, self.get_local_market(self.currency).get_average_tag_price('food') * 1.5, self.currency)
        Pop.update(self)


class Enterprise(Consumer):
    def __init__(self, world, attributes, pop = None, size = 0, owner = None, ai_state = AI_Enterprise, name = 'enterprise', tile = None, cell = None, starting_money = 0, currency = 'money1'):
        Consumer.__init__(self, world, attributes['needs'], size, name = name, cell = cell)
        self.tile = tile
        self.input = attributes['input']
        self.output = attributes['output']
        self.throughput = attributes['throughput']
        self.input_eff = 1.1
        self.output_eff = 0.9
        self.pop = pop
        self.pop.savings.set(starting_money, currency)
        self.pop.max_size = self.size
        self.attr = attributes
        if owner == None:
            self.owner = pop
        else:
            self.owner = owner
        self.pop.enterprise = self
        self.AI = StateMachine(self, ai_state)
        self.active_workers = self.pop.size
        self.price = dict()
        self.salary = 10
        self.density =  attributes['density']
        self.savings.set(starting_money, currency)
        self.salary_coeff = 0
        self.total_sold = 0
        self.total_produced = 0
        self.housing_price = 10
        pure_income = 0

        for i in TAGS:
            self.price[i] = 10

    def update(self):
        self.total_produced = 0
        self.update_housing()
        self.set_active_workers(self.active_workers)
        Consumer.update(self)
        self.AI.update()
        self.produce()
        self.potent_profit = self.calculate_potent_profit_per_worker()

    def calculate_potent_profit_per_worker(self):
        tmp = 0
        for i in self.input:
            tmp -= self.get_local_market(self.currency).get_average_tag_price(i[0]) * self.throughput / self.get_input_eff()
        for i in self.output:
            tmp += self.get_local_market(self.currency).get_average_tag_price(i[0]) * self.throughput * self.get_output_eff()
        tmp -= self.salary
        return tmp

    def produce(self):

        production_amount = self.get_production_amount()
        for i in self.input:
            if i[1] != 0:
                production_amount = min(production_amount, self.stash.get(i[0]) / (i[1] * self.get_input_eff()))
        # print(self.name, 'production_amount', production_amount)
        if len(self.input) > 0 :
            print(self.input[0][0], self.stash.get(self.input[0][0]))
        for i in self.input:
            self.stash.inc(i[0], -int(production_amount * i[1] * self.get_input_eff()))
        for i in self.output:
            self.total_produced += int(production_amount * i[1] * self.get_output_eff())
            self.stash.inc(i[0], int(production_amount * i[1] * self.get_output_eff()))
            if LOGGING:
                print(self.name, 'produced', int(production_amount * i[1] * self.get_output_eff()), i[0])

    def get_input_eff(self):
        return self.input_eff

    def get_output_eff(self):
        return self.output_eff

    def set_active_workers(self, x):
        self.active_workers = max(min(self.pop.size, x), 0)

    def get_input_needs(self):
        return self.active_workers * self.get_input_consumption_per_worker()

    def get_input_consumption_per_worker(self):
        return self.throughput / self.get_input_eff()

    def get_production_amount(self):
        return self.active_workers * self.throughput

    def get_production_per_worker(self):
        return self.throughput * self.output_eff

    def print_pops(self):
        pass

    def print_enterprises(self):
        print('___________' + self.name + '___________')
        print('size', self.size)
        print('active_workers', self.active_workers)
        print('savings', self.savings.get('money1'))
        print('true_savings', self.savings.get(self.currency) + self.get_money_on_market())
        print('produced', self.total_produced)
        self.stash.print_all()

    def get_list(self):
        return [self.name, self.size, self.active_workers, self.savings.get(self.currency) + self.get_money_on_market(), self.total_produced, self.price[self.output[0][0]]]

    def get_size(self):
        return self.size

    def get_housing(self):
        return int(self.size * self.density)

    def update_housing(self):
        tmp = self.pop.size - self.get_housing()
        if tmp > 0:
            self.pop.demote(tmp)

class EnterpriseWithWorkers(Enterprise):
    def __init__(self, world, attributes, owner = None, name = 'enterprise', tile = None, size = 0, cell = None, starting_pop_size = 0, starting_money = 0, currency = 'money1'):
        pop = NormalHumanBeing(world, starting_pop_size,
                      parent = tile.pop,
                      name = name + ' workers',
                      cell = cell)
        Enterprise.__init__(self, world, attributes = attributes,
                            pop = pop,
                            owner = owner,
                            name = name,
                            tile = tile,
                            size = size,
                            cell = cell,
                            starting_money = starting_money,
                            currency = currency)
        pop.cave = self

class Farm(Enterprise):
    def __init__(self, world, owner = None, name = 'farm', tile = None, size = 0, cell = None, starting_pop_size = 0, starting_money = 0, currency = 'money1'):
        pop = NormalHumanBeing(world, starting_pop_size,
                      parent = tile.pop,
                      name = name + ' workers',
                      cell = cell)
        Enterprise.__init__(self, world, attributes = FARM,
                            pop = pop,
                            owner = owner,
                            name = name,
                            tile = tile,
                            size = size,
                            cell = cell,
                            starting_money = starting_money,
                            currency = currency)
        pop.cave = self

class Pastures(Enterprise):
    def __init__(self, world, owner = None, name = 'farm', tile = None, size = 0, cell = None, starting_pop_size = 0, starting_money = 0, currency = 'money1'):
        pop = NormalHumanBeing(world, starting_pop_size,
                      parent = tile.pop,
                      name = name + ' workers',
                      cell = cell)
        Enterprise.__init__(self, world, attributes = PASTURES,
                            pop = pop,
                            owner = owner,
                            name = name,
                            tile = tile,
                            size = size,
                            cell = cell,
                            starting_money = starting_money,
                            currency = currency)
        pop.cave = self

class Bakery(Enterprise):
    def __init__(self, world, owner = None, name = 'bakery', tile = None, size = 0, cell = None, starting_pop_size = 0, starting_money = 0, currency = 'money1'):
        pop = NormalHumanBeing(world, starting_pop_size,
                      parent = tile.pop,
                      name = name + ' workers',
                      cell = cell)
        Enterprise.__init__(self, world, attributes = BAKERY,
                            pop = pop,
                            owner = owner,
                            name = name,
                            tile = tile,
                            size = size,
                            cell = cell,
                            starting_money = starting_money,
                            currency = currency)
        pop.cave = self

class WeaverShop(Enterprise):
    def __init__(self, world, owner = None, name = 'bakery', tile = None, size = 0, cell = None, starting_pop_size = 0, starting_money = 0, currency = 'money1'):
        pop = NormalHumanBeing(world, starting_pop_size,
                      parent = tile.pop,
                      name = name + ' workers',
                      cell = cell)
        Enterprise.__init__(self, world, attributes = WEAVERSHOP,
                            pop = pop,
                            owner = owner,
                            name = name,
                            tile = tile,
                            size = size,
                            cell = cell,
                            starting_money = starting_money,
                            currency = currency)
        pop.cave = self


class Office():
    def __init__(self, org, tag):
        self.org = org
        self.tag = tag

class Human(Consumer):
    def __init__(self, world, owner = None, name = None, cell = None, tile = None, gender = None, age_tick = 0, role = 'capitalist'):
        Consumer.__init__(self, world, BASIC_NEEDS, 1, name = name, cell = cell)
        self.tile = tile
        self.gender = gender
        self.age_tick = age_tick
        self.chosen_building = None
        self.offices = []
        self.role = role
        self.AI = dict()
        self.AI['leader'] = StateMachine(self, LeaderIdle)
        self.AI['captain'] = StateMachine(self, CaptainIdle)
        self.AI['capitalist'] = StateMachine(self, AgentSaveMoney)
    def update(self):
        self.age_tick += 1
        Consumer.update(self)
        self.AI[self.role].update()

    def build(self, starting_savings = 0):
        currency = self.currency
        market = self.get_local_market(currency)
        for i in self.chosen_building['building']['building_cost']:
            self.clear_orders(i[0], currency)
        cell = self.cell
        if self.chosen_building == None:
            return
        for i in self.chosen_building['building']['building_cost']:
            if self.stash.get(i[0]) < i[1]:
                self.buy(i[0], i[1] - self.stash.get(i[0]), market.guess_tag_cost(i[0], i[1] - self.stash.get(i[0])), currency)
        for i in self.chosen_building['building']['building_cost']:
            if self.stash.get(i[0]) < i[1]:
                return 'not_enough_resourses'
        tmp = self.chosen_tile.build(self, self.chosen_building)
        # self.savings.transfer(tmp.savings, starting_savings, self.currency)
        return 'ok!'

    def add_office(self, office):
        self.offices.append(office)

class MilitarySquad(Pop):
    def __init__(self, world, size, parent = None, AI = BasicPopAI, name = 'army', cell = None, max_size = None, starting_money = 0, currency = 'money1', town = None):
        Pop.__init__(self, world, BASIC_NEEDS, size, AI = AI, parent = parent, name = name, cell = cell, max_size = max_size, starting_money = starting_money, currency = currency)
        self.ArmyAI = StateMachine(self, ArmyIdleAI)
        self.town = town

    def update(self):
        Pop.update(self)
        self.ArmyAI.update()

    def get_salary(self):
        return self.town.salary['soldiers']

class Town(Agent):
    def __init__(self, world, cell, name = 'Town', starting_money = 0, currency = 'money1'):
        Agent.__init__(self, world, name = 'agent', cell = cell, starting_money = starting_money, currency = currency)
        self.cell = cell
        self.cells = []
        self.taxes = dict()
        for i in TAGS:
            self.taxes[i] = 0
        self.offices_tag = ['leader', 'captain', 'soldiers']
        self.offices = dict()
        self.salary = dict()
        for i in self.offices_tag:
            self.offices[i] = None
            self.salary[i] = 0
        self.markets = set()
        self.offices['soldiers'] = MilitarySquad(self.world, size = 50, max_size = 100, currency = currency, town = self, cell = cell)
        self.salary['soldiers'] = 50

    def add_cell(self, cell):
        self.cells.append(cell)
        cell.set_owner(self)
        cell.get_market(self.currency).set_owner(self)
        self.markets.add(cell.get_market(self.currency))


    def update(self):
        self.pay_wages()
        # if self.offices['leader'] != None:
        #     self.offices['leader'].AI['leader'].update()
        # if self.offices['captain'] != None:
        #     self.offices['captain'].AI['captain'].update()


    def pay_wages(self):
        for tag in self.offices_tag:
            if self.offices[tag] != None:
                self.savings.transfer(self.offices[tag].savings, self.salary[tag] * self.offices[tag].size, self.currency)

    def pay(self, tag, amount):
        if self.offices[tag] != None:
            self.savings.transfer(self.offices[tag].savings, amount, self.currency)

    def set_office(self, office, x):
        self.offices[office] = x
        x.add_office(Office(self, office))

    def set_market_tax(self, tag, x, currency):
        self.taxes[tag] = x
        for market in self.markets:
            market.set_taxes(tag, x)

    def change_salary(self, tag, x):
        self.salary[tag] += x



world = World(1, 1)
print('world inited')
x, y = 0, 0
cell = world.get_cell(x, y)

m1 = Market('money1', cell = cell)
cell.add_market(m1)

susek = Human(world, cell = cell, name = 'susek', gender = 'male', age_tick = 9000, role = 'leader')
peter = Human(world, cell = cell, name = 'peter', gender = 'male', age_tick = 8000, role = 'capitalist')
pidar = Human(world, cell = cell, name = 'pidar', gender = 'male', age_tick = 10000, role = 'captain')
peter.stash.inc('wood', 400)
peter.savings.inc(1000000, 'money1')


Hehusgrad = Town(world, cell = cell, name = 'Hehusgrad', starting_money = 10000)
Hehusgrad.add_cell(cell)
Hehusgrad.set_office('leader', susek)
Hehusgrad.set_office('captain', pidar)
Hehusgrad.set_market_tax('food', 1, 'money1')
Hehusgrad.set_market_tax('regular_cloth', 10, 'money1')

cell.pop.change_size(200)
cell.add_tile(Village(cell, owner = Hehusgrad))
cell.add_tile(Village(cell, owner = Hehusgrad))
cell.add_tile(PasturesTile(cell, owner = Hehusgrad))
cell.add_tile(PasturesTile(cell, owner = Hehusgrad))
cell.add_tile(SmallTown(cell, owner = Hehusgrad))
cell.add_tile(SmallTown(cell, owner = Hehusgrad))
cell.add_tile(Forest(cell, owner = Hehusgrad))
print('tiles inited')



pygame.init()
pygame.display.set_caption('gsg')
DISPLAYSURF = pygame.display.set_mode((1600, 900), 0, 32)
DISPLAYSURF.fill((255, 255, 255))
pygame.font.init()
myfont = pygame.font.SysFont('timesnewroman', 12)

def draw():
    surface = pygame.PixelArray(DISPLAYSURF)
    z = 0
    color = (0, 0, 0)
    color2 = (255, 0, 0)
    for z in range(0, 500):
        for tag in TAGS:
            if 499 >= PRICES[tag][z]:
                surface[z][499 - int(PRICES[tag][z])] = COLOR[tag]
        surface[z][499] = color
        surface[z][400 - POPULATION[z] // 20] = color
        surface[z][400] = color
    del surface



class UpdatingLabel():
    def __init__(self, x, y, f, color = (255, 0 ,0)):
        self.x = x
        self.y = y
        self.text_f = f
        self.color = color
        text = myfont.render(str(self.text_f()), True, self.color)
        self.rect = Rect(self.x, self.y, text.get_bounding_rect().w, text.get_bounding_rect().h)

    def draw(self, dx = 0, dy = 0):
        text = myfont.render(str(self.text_f()), True, self.color)
        rect = Rect(self.x + dx, self.y + dy, text.get_bounding_rect().w, text.get_bounding_rect().h)
        self.text = text
        self.rect = rect
        DISPLAYSURF.blit(text, rect)




class UpdatingGrid():
    def __init__(self, x, y, f, color = (255, 0, 0), spacing = [100] * 100):
        self.x = x
        self.y = y
        self.table_f = f
        self.text_color = color
        self.spacing = spacing
        self.update()

    def draw(self):
        tmp = self.data
        for i in range(len(tmp)):
            for j in range(len(tmp[i])):
                self.data[i][j].draw()

    def tmp_func(self, i, j):
        return str(self.table_f()[i][j])

    def update(self):
        tmp = self.table_f()
        # print('____________')
        # print(len(tmp))
        # print(len(tmp[0]))
        # for i in tmp:
        #     print(tmp)
        self.data = [['???' for i in range(len(tmp[j]))] for j in range(len(tmp))]
        for i in range(len(tmp)):
            for j in range(len(tmp[i])):
                # print(i, j)
                # print(len(self.data))
                # print(len(self.data[i]))
                # print(len(self.spacing))
                self.data[i][j] = UpdatingLabel(self.x + self.spacing[j], self.y + i * 18, lambda i = i, j = j: self.tmp_func(i, j), color = self.text_color)

PopulationLable = UpdatingLabel(30, 30, lambda x = x: 'population: ' + str(cell.get_population()))
HehusgradMoneyLable = UpdatingLabel(30, 60, lambda x = x: 'Hehusgrad savings ' + str(Hehusgrad.get_savings('money1')))
MarketGrid = UpdatingGrid(500, 0, m1.get_table, spacing = [0, 40, 120, 260, 340, 440, 300])
EnterpriseGrid = UpdatingGrid(0, 500, cell.get_enterprises_list, spacing = [0, 100, 140, 190, 240, 280, 300])
PopulationGrid = UpdatingGrid(900, 0, world.get_pops_list, spacing = [0, 150, 200, 250, 240, 280, 300])
peterLabel = UpdatingLabel(30, 90, lambda x = x: 'peter savings ' + str(peter.get_true_savings()))
moneyLabel = UpdatingLabel(30, 120, lambda x = x: str(world.get_total_money()))
market_savings = UpdatingLabel(30, 150, lambda x = x: str(m1.savings.get('money1')))

while 1 == 1:
    PopulationLable.draw()
    world.update()

    world.print_all()
    for i in cell.markets:
        i.print_orders()
        for j in TAGS:
            print(j)
            print('total_sold', i.total_sold[j][-1])
            print('total_sold_cost', i.total_sold_cost[j][-1])
    print('_____________')
    for tag in TAGS:
        PRICES[tag] = PRICES[tag][1:] + [min(m1.get_average_tag_price(tag), 499)]
        print(tag, m1.get_average_tag_price(tag))
    # FOOD_PRICE = FOOD_PRICE[1:] + [m1.get_average_tag_price('food')]
    # # print('food', FOOD_PRICE[-1])
    # WHEAT_PRICE = WHEAT_PRICE[1:] + [m1.get_average_tag_price('wheat')]
    # # print('wheat', WHEAT_PRICE[-1])
    # SERVICES_PRICE = SERVICES_PRICE[1:] + [m1.get_average_tag_price('services')]
    # # print('services', SERVICES_PRICE[-1])
    # WOOL_PRICE = SERVICES_PRICE[1:] + [m1.get_average_tag_price('wool')]
    # # print('wool', SERVICES_PRICE[-1])
    # CLOTH_PRICE = SERVICES_PRICE[1:] + [m1.get_average_tag_price('regular_cloth')]
    # # print('cloth', CLOTH_PRICE[-1])
    m1.print_profits_per_chain()
    if TICK == 0:
        POPULATION = POPULATION[1:] + [cell.get_population()]

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    try:
        DISPLAYSURF.fill((255, 255, 255))
        PopulationLable.draw()
        HehusgradMoneyLable.draw()
        MarketGrid.update()
        MarketGrid.draw()
        EnterpriseGrid.update()
        EnterpriseGrid.draw()
        PopulationGrid.update()
        PopulationGrid.draw()
        peterLabel.draw()
        moneyLabel.draw()
        market_savings.draw()
        draw()
    except:
        raise sys.exc_info()[0]
    pygame.display.update()
    # print('bakery')
    # print(bakery.pop.savings.get())
    # print(bakery.savings.get())
    # print('farm')
    # print(farm.pop.savings.get())
    # print(farm.savings.get())
    TICK = (TICK + 1) % 30
    pygame.time.delay(1)
    # input()
    # time.sleep(0.001)
