from statetemplates import *
from CONSTANTS import *


class HomelessAI(State):
    def Execute(agent):
        # print('______POP_AI_JOBLESS_____')
        tmp = 0
        for i in agent.cell.get_enterprises():
            # print(i.pop.name, i.pop.size, i.pop.max_size)
            if not i.pop.is_full():
                agent.transfer_size(i.pop, 1)
        army_pop = agent.cell.get_local_army()
        if not army_pop.is_full():
            agent.transfer_size(army_pop, 1)


class BasicPopAI(State):
    def Execute(agent):
        if POP_LOGGING:
            print('POP_AI_____________________________________')
        cell = agent.cell
        currency = agent.currency
        tmp = int(max(agent.size * 1 * agent.needs['food'] - agent.stash.get('food'), 0))
        agent.clear_orders('food', currency)
        agent.buy('food', tmp, min(agent.savings.get(currency), (agent.get_local_market(currency).guess_tag_cost('food', tmp) + 2) * 3) + 10, currency)
        for i in TAGS:
            if i != 'food':
                tmp = int(max(agent.size * 1 * agent.needs[i] - agent.stash.get(i), 0))
                agent.clear_orders(i, currency)
                if tmp > 0:
                    # print(agent.name, 'buy', i, tmp, 'guess_cost', agent.get_local_market(currency).guess_tag_cost(i, tmp), 'savings', agent.savings.get(currency))
                    agent.buy(i, tmp, min(agent.savings.get(currency), max(agent.get_local_market(currency).guess_tag_cost(i, tmp), int(agent.savings.get(currency) * 0.1))), currency)


        # tmp = agent.get_salary()
        # tmp_pop = agent
        # for i in agent.cell.get_enterprises():
        #     tmp2 = i.pop.get_salary()
        #     if tmp2 > tmp and not i.pop.is_full():
        #         tmp = tmp2
        #         tmp_pop = i.pop
        # army_pop = cell.get_local_army()
        # tmp2 = army_pop.get_salary()
        # if tmp2 > tmp and not army_pop.is_full():
        #     tmp = army_pop
        #     tmp_pop = i.pop
        # for i in agent.cell.get_enterprises():
        #     tmp2 = i.calculate_potent_profit_per_worker()
        #     if tmp2 > tmp and not i.pop.is_full:
        #         tmp = tmp2
        #         tmp_pop = i.pop
        # if tmp_pop != agent:
        #     agent.transfer_size(tmp_pop, 1)


# def BasicEnterpriseAI(agent):
#     # print('____________AI LOGGING___________', agent.name)
#     currency = agent.currency
#     for i in agent.input + agent.output:
#         agent.clear_orders(i[0], currency)
#     market = agent.get_local_market(currency)
#
#     agent.salary = int(market.get_average_tag_price('food')) + 2
#     # print('salary', agent.salary)
#
#     if agent.active_workers == 0:
#         agent.set_active_workers(1)
#     for i in agent.output:
#         # market.print_orders()
#         # print(i[0], 'mpmts mtcopgwploe', market.planned_money_to_spent[i[0]], market.get_total_cost_of_placed_goods_with_price_less_or_equal(i[0], agent.price[i[0]]))
#         # print(agent.active_workers, agent.price[i[0]])
#         # print('salary', agent.salary)
#         x = market.planned_money_to_spent[i[0]] - market.get_total_cost_of_placed_goods_with_price_less_or_equal(i[0], agent.price[i[0]]) #market.total_cost_of_placed_goods[i[0]]
#         total_cost_of_goods = (agent.active_workers * agent.throughput * agent.get_output_eff() + agent.stash.get(i[0])) * agent.price[i[0]]
#         # print(x, total_cost_of_goods)
#         # print(agent.salary * 1.2 * agent.active_workers)
#         if x >= total_cost_of_goods or agent.salary * 1.2 * agent.active_workers > total_cost_of_goods:
#             planned_income_growth_from_increasing_price = agent.active_workers
#             planned_income_growth_from_increasing_number_of_active_workers = agent.price[i[0]] - market.check_cost(agent.input) * agent.get_input_eff() - agent.salary
#             # if agent.salary * 1.5 > agent.price[i[0]] * agent.throughput * agent.get_input_eff() * agent.get_output_eff():
#             if agent.salary * 1.2 * agent.active_workers > total_cost_of_goods:
#                 agent.price[i[0]] += 1
#             elif x >= planned_income_growth_from_increasing_price and (planned_income_growth_from_increasing_price >= planned_income_growth_from_increasing_number_of_active_workers or (agent.active_workers + 1) > agent.pop.size):
#                 agent.price[i[0]] += 1
#             elif x >= planned_income_growth_from_increasing_number_of_active_workers > planned_income_growth_from_increasing_price:
#                 agent.set_active_workers(agent.active_workers + 1)
#             # print('pigfip', planned_income_growth_from_increasing_price)
#             # print('pigfinoaw', planned_income_growth_from_increasing_number_of_active_workers)
#             # print('price', agent.price[i[0]])
#         else:
#             #dice = random.randint(0, 1)
#             #if (dice == 0 or agent.active_workers <= 1):
#             agent.price[i[0]] -= 1
#             #else:
#             #    agent.set_active_workers(agent.active_workers - 1)
#         # print('try to sell', i[0], agent.stash.get(i[0]), agent.price[i[0]])
#         agent.clear_orders(i[0], currency)
#         agent.sell(i[0], agent.stash.get(i[0]), agent.price[i[0]], currency)
#     salary = max(agent.salary * agent.active_workers, 100)
#     #if salary == 0:
#     #    salary = int(agent.savings.get() * 0.1)
#     # print('salary', salary)
#     # print('income', agent.get_income())
#     x = market.find_amount_of_goods_for_buying(agent.get_input_needs(), agent.savings.get(currency), agent.input)
#     for i in agent.input:
#         # print('try to buy', i[0], i[1] * x, agent.savings.get())
#         agent.clear_orders(i[0], currency)
#         agent.buy(i[0], i[1] * x, market.guess_tag_cost(i[0], i[1] * x), currency)
#     # print('________________________')
#     agent.savings.transfer(agent.pop.savings, salary, currency)
#     if agent.owner != None:
#         agent.savings.transfer(agent.owner.savings, int(agent.savings.get(currency) * 0.01), currency)



class AI_Enterprise(State):
    def Execute(agent):
        flag = False
        if flag:
            print('_______AI_LOGGING', agent.name, '_________')
        currency = agent.currency
        market = agent.get_local_market(currency)
        for i in agent.input + agent.output:
            agent.clear_orders(i[0], currency)
        agent.salary = market.get_average_tag_price('food') * agent.salary_coeff
        for i in agent.output:
            tag = i[0]
            amount = i[1]
            tmp_pure_income = None
            tdworkers = 0
            tdprice = dict()
            tdprice[tag] = 0
            i = 0
            t_x = 0
            t_planned_spendings = 0
            while i < pow(3, len(agent.output)):
                tmp = i
                if flag:
                    print(i, '_______')
                dprice = dict()
                no_profit = False
                for j in range(len(agent.output)):
                    tag = agent.output[j][0]
                    dprice[tag] = (tmp % 3 - 1)
                    tmp = tmp // 3
                    if agent.price[tag] + dprice[tag] <= 0:
                        no_profit = True
                if no_profit:
                    i += 1
                    continue
                if flag:
                    print(dprice)
                for dworkers in [0, 1]:
                    if agent.active_workers + dworkers > agent.pop.size or agent.active_workers + dworkers <= 0:
                        continue
                    planned_workers = agent.active_workers + dworkers
                    expected_income = dict()
                    for z in agent.output:
                        planned_price = dict()
                        max_income = dict()
                        tag = z[0]
                        expected_income[tag] = 0
                        planned_price[tag] = agent.price[tag] + dprice[tag]
                        if flag:
                            print(planned_price)
                        total_cost_of_produced_goods = planned_workers * agent.get_production_per_worker() * planned_price[tag]
                        total_cost_of_goods = (planned_workers * agent.get_production_per_worker() + agent.stash.get(tag)) * planned_price[tag]
                        max_income[tag] = market.planned_money_to_spent[tag] - market.get_total_cost_of_placed_goods_with_price_less_or_equal(tag, planned_price[tag] + market.taxes[tag])
                        expected_income[tag] = min(max_income[tag], total_cost_of_goods)
                        if flag:
                            print('planned_money_to_spend', market.planned_money_to_spent[tag])
                            print(market.get_total_cost_of_placed_goods_with_price_less_or_equal(tag, planned_price[tag]))
                            print(max_income, total_cost_of_goods)
                            print('expected_income', expected_income)
                    total_income = 0
                    for z in agent.output:
                        total_income += expected_income[z[0]]
                    if flag:
                        print('planned_workers', planned_workers, agent.get_input_consumption_per_worker())
                    x = market.find_amount_of_goods_for_buying(planned_workers * agent.get_input_consumption_per_worker(), agent.savings.get(currency) // 2, agent.input)
                    if flag:
                        print('x =', x)
                    inputs_cost = 0
                    tmp_list = []
                    for z in agent.input:
                        tmp_list.append([z[0], z[1] * x])
                    inputs_cost += market.guess_cost(tmp_list)
                    salary_spendings = agent.active_workers * agent.salary
                    planned_income = total_income
                    planned_spendings = planned_workers * agent.salary + inputs_cost
                    planned_pure_income = planned_income - planned_spendings
                    if flag:
                        print(planned_income, planned_spendings)
                    if tmp_pure_income == None or tmp_pure_income < planned_pure_income and planned_price:
                        t_x = x
                        tdprice = dprice
                        tdworkers = dworkers
                        tmp_pure_income = planned_pure_income
                        t_planned_spendings = planned_spendings
                        if flag:
                            print('update_answer_with', 'x =', t_x, 'dprice =', dprice, 'dworkers =', dworkers)
                            print('planned_income', planned_income, 'planned_spendings', planned_spendings)
                i += 1
            for i in agent.output:
                tag = i[0]
                agent.price[tag] += tdprice[tag]
            for i in agent.output:
                agent.sell(i[0], agent.stash.get(i[0]), agent.price[i[0]] + market.taxes[tag], currency)
            agent.set_active_workers(agent.active_workers + tdworkers)
            for i in agent.input:
                if flag:
                    print(tmp)
                    print(i, t_x)
                agent.buy(i[0], i[1] * t_x, market.guess_tag_cost(i[0], i[1] * t_x) * 2, currency)
        agent.savings.transfer(agent.pop.savings, min(agent.salary * agent.active_workers + 1, agent.savings.get(currency) - t_planned_spendings), currency)
        # if agent.owner != None:
        agent.savings.transfer(agent.owner.savings, int(agent.savings.get(currency) * 0.01), currency)

        if flag:
            print('_________________________________')


# basic ai for agents who build buildings and make profit from them

class AgentSaveMoney(State):
    def Execute(agent):
        print('_________AGENTAI__________')
        currency = agent.currency
        market = agent.get_local_market(currency)
        most_profitable_building, chosen_tile = market.get_most_profitable_building()
        print(most_profitable_building, chosen_tile)
        if agent.savings.get(currency) > most_profitable_building['cost'] * 1.5 + chosen_tile.price + 100000:
            agent.chosen_building = most_profitable_building
            agent.chosen_tile = chosen_tile
            agent.AI['capitalist'].change_state(AgentBuyClay)
        print(most_profitable_building, chosen_tile)

class AgentBuyClay(State):
    def Execute(agent):
        currency = agent.currency
        if agent.savings.get(currency) > agent.chosen_tile.price:
            agent.buy_tile(agent.chosen_tile)
            agent.AI['capitalist'].change_state(AgentBuildBuilding)
        else:
            agent.AI['capitalist'].change_state(AgentSaveMoney)

class AgentBuildBuilding(State):
    def Execute(agent):
        currency = agent.currency
        market = agent.get_local_market(currency)
        if agent.chosen_building['cost'] + 100000 < agent.savings.get(currency):
            agent.build(starting_savings = 100000)
        else:
            agent.AI['capitalist'].change_state(AgentSaveMoney)


class ArmyIdleAI(State):
    def Execute(agent):
        pass

class LeaderIdle(State):
    def Execute(agent):
        off = agent.offices
        town = off[0].org
        if town.offices['soldiers'].size < 100:
            agent.AI['leader'].change_state(LeaderGatherArmy)

class LeaderGatherArmy(State):
    def Execute(agent):
        off = agent.offices
        town = off[0].org
        town.offices['soldiers'].set_max_size(200)
        # if town.savings.get(agent.currency) > 1000 and town.offices['soldiers'].savings.get(agent.currency) < 1000:
        #     town.pay('soldiers', 1000)
        # if town.offices['soldiers'].size <= 100:
        #     town.change_salary('soldiers', 1)


class CaptainIdle(State):
    def Execute(agent):
        pass



class TileIdle(State):
    def Execute(agent):
        agent.savings.transfer(agent.owner.savings, agent.savings.get(agent.currency))
