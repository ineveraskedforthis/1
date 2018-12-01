#needs
TAGS = ['food', 'wheat', 'wool', 'regular_cloth', 'services', 'wood', 'stone']
BASIC_NEEDS = dict()
BASIC_ARMY_NEEDS = dict()
FARM_NEEDS = dict()
BAKERY_NEEDS = dict()
for i in TAGS:
    BASIC_NEEDS[i] = 0
    BASIC_ARMY_NEEDS[i] = 0
    FARM_NEEDS[i] = 0
    BAKERY_NEEDS[i] = 0
BASIC_NEEDS['food'] = 1
BASIC_NEEDS['services'] = 1
BASIC_NEEDS['regular_cloth'] = 1
BASIC_NEEDS['wool'] = 0.1
BASIC_NEEDS['wheat'] = 0.1
BASIC_NEEDS['wood'] = 0.1


FARM = dict()
FARM['name'] = 'farm'
FARM['input'] = []
FARM['output'] = [['wheat', 1]]
FARM['building_cost'] = [['wood', 100]]
FARM['density'] = 0.1
FARM['throughput'] = 10
FARM['needs'] = []
FARM['requirements'] = ['soil']
FARM['size'] = 100

PASTURES = dict()
PASTURES['name'] = 'pastures'
PASTURES['input'] = []
PASTURES['output'] = [['wool', 1]]
PASTURES['building_cost'] = [['wood', 100]]
PASTURES['density'] = 0.1
PASTURES['throughput'] = 2
PASTURES['needs'] = []
PASTURES['requirements'] = []
PASTURES['size'] = 100

BAKERY = dict()
BAKERY['name'] = 'bakery'
BAKERY['input'] = [['wheat', 1]]
BAKERY['output'] = [['food', 1]]
BAKERY['building_cost'] = [['wood', 100]]
BAKERY['density'] = 0.8
BAKERY['throughput'] = 10
BAKERY['needs'] = []
BAKERY['requirements'] = []

WEAVERSHOP = dict()
WEAVERSHOP['name'] = 'weavershop'
WEAVERSHOP['input'] = [['wool', 1]]
WEAVERSHOP['output'] = [['regular_cloth', 1]]
WEAVERSHOP['building_cost'] = [['wood', 100]]
WEAVERSHOP['density'] = 0.8
WEAVERSHOP['throughput'] = 8
WEAVERSHOP['needs'] = []
WEAVERSHOP['requirements'] = []

WOODCUTTER = dict()
WOODCUTTER['name'] = 'woodcutter'
WOODCUTTER['input'] = []
WOODCUTTER['output'] = [['wood', 1]]
WOODCUTTER['building_cost'] = [['wood', 100]]
WOODCUTTER['density'] = 0.1
WOODCUTTER['throughput'] = 2
WOODCUTTER['needs'] = []
WOODCUTTER['requirements'] = ['forest']

BUILDINGS = dict()
BUILDINGS['farm'] = FARM
BUILDINGS['bakery'] = BAKERY
BUILDINGS['pastures'] = PASTURES
BUILDINGS['weavershop'] = WEAVERSHOP
BUILDINGS['woodcutter'] = WOODCUTTER
buildings = BUILDINGS

for i in buildings:
    buildings[i]['size'] = 100


TILE_SIZE = 500

LOGGING = False
POP_LOGGING = False
INF = 99999999999999
