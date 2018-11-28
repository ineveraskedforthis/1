#needs
TAGS = ['food', 'wheat', 'wool', 'regular_cloth', 'services', 'wood', 'stone']
BASIC_NEEDS = dict()
FARM_NEEDS = dict()
BAKERY_NEEDS = dict()
for i in TAGS:
    BASIC_NEEDS[i] = 0
    FARM_NEEDS[i] = 0
    BAKERY_NEEDS[i] = 0
BASIC_NEEDS['food'] = 1
BASIC_NEEDS['services'] = 1
BASIC_NEEDS['regular_cloth'] = 1
BASIC_NEEDS['wool'] = 0.1
BASIC_NEEDS['wheat'] = 0.1

buildings = []
FARM = dict()
FARM['name'] = 'farm'
FARM['input'] = []
FARM['output'] = [['wheat', 1]]
FARM['building_cost'] = [['wood', 10]]
FARM['density'] = 0.1
FARM['throughput'] = 10
FARM['needs'] = []

PASTURES = dict()
PASTURES['name'] = 'pastures'
PASTURES['input'] = []
PASTURES['output'] = [['wool', 1]]
PASTURES['building_cost'] = [['wood', 10]]
PASTURES['density'] = 0.1
PASTURES['throughput'] = 2
PASTURES['needs'] = []

BAKERY = dict()
BAKERY['name'] = 'bakery'
BAKERY['input'] = [['wheat', 1]]
BAKERY['output'] = [['food', 1]]
BAKERY['building_cost'] = [['wood', 10]]
BAKERY['density'] = 0.8
BAKERY['throughput'] = 10
BAKERY['needs'] = []

WEAVERSHOP = dict()
WEAVERSHOP['name'] = 'weavershop'
WEAVERSHOP['input'] = [['wool', 1]]
WEAVERSHOP['output'] = [['regular_cloth', 1]]
WEAVERSHOP['building_cost'] = [['wood', 10]]
WEAVERSHOP['density'] = 0.8
WEAVERSHOP['throughput'] = 8
WEAVERSHOP['needs'] = []

buildings = [FARM, BAKERY, PASTURES, WEAVERSHOP]

LOGGING = True
INF = 99999999999999
