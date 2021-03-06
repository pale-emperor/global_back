from django import shortcuts
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
 
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
import json
import random
import math
import logging
import os

logging.basicConfig(filename=os.path.dirname(__file__)+'/app.log', filemode='w', format='%(message)s',level=logging.DEBUG)

# Set parameters of map
tiers = 15
phases = 3
maps = 1
global_id = 0

# Set image size
W = 3840
H = 2160

# Set tier radius
R = min(W, H)/((tiers + 2)*2)
logging.debug(f'Current dir: {os.path.dirname(__file__)}')
logging.debug(f'Set tier radius : {R}')

# Set font
fnt = ImageFont.truetype("/home/wh1te/global_back/global_generator/res/lucon.ttf", 18)
small_fnt = ImageFont.truetype("/home/wh1te/global_back/global_generator/res/lucon.ttf", 12)
big_fnt = ImageFont.truetype("/home/wh1te/global_back/global_generator/res/lucon.ttf", 24)


class Maps:

    def __init__(self):
        self.maps = []

    def add_map(self, map):
        logging.debug(f'Map added {map.id}')
        self.maps.append(map)
        leng = len(self.maps)
        logging.debug(f'Total_maps_count: {leng}')

    def get_maps(self):
        return self.maps

    def get_maps_from_tier(self, tier):
        tier_maps = []
        for map in self.maps:
            if map.tier == tier:
                tier_maps.append(map)
        return tier_maps


class Paths:

    def __init__(self):
        self.paths = []
    
    def add_path(self, path):
        self.paths.append(path)

    def get_paths(self):
        return self.paths


class Path:

    def __init__(self, _map1, _map2, length, hidden=False, shortcut=False):
        self.map1 = _map1
        self.map2 = _map2
        self.length = length
        self.hidden = hidden
        self.shortcut = shortcut

    def get_json_info(self):
        map1_inf = self.map1
        map2_inf = self.map2
        return self.map1.map_info(), self.map2.map_info(), self.length, self.hidden

    def get_maps(self):
        return self.map1, self.map1

    def get_info(self):
        return self.map1, self.map2, self.length, self.hidden


class Map:

    def get_paths(self):
        _paths = []
        for path in self.paths:
            _paths.append(path)
        return _paths

    def map_json_info(self):
        _paths = []
        for path in self.paths:
            _paths.append(path.get_json_info())
        return self.id, self.Coordinates, self.map_tier, self.degree, self.map_level, _paths

    def map_info(self):
        return self.id, self.Coordinates, self.map_tier, self.degree, self.map_level

    def increase_level(self):
        if self.map_level == len(map_color)-1:
            self.unique = True
        else:
            self.map_level += 1

    def check_maxlvl(self):
        pass

    def add_path(self, path:Path):
        self.paths.append(path)

    def __init__(self, _map_id, _map_center, _tier, _degree, _map_level):
        self.paths = []
        self.id = _map_id
        self.Coordinates = _map_center
        self.map_tier = _tier
        self.degree = _degree
        self.map_level = _map_level
        self.tier = _tier
        self.unique = False



class Chains:

    def __init__(self):
        self.chains = {}

    def add_chain(self, chain):
        self.chains[chain.id] = chain

    def get_chains(self):
        _chains = []
        for chain_id in self.chains:
            _chains.append(self.chains[chain_id])
        return _chains

class Chain:
    
    def __init__(self, paths, chain_id):
        logging.debug(f'create_chain {chain_id} with paths: {paths}')    
        self.id = chain_id
        self.paths = []
        for path in paths:
            self.paths.append(path)


    def add_path(self, path : Path):
        self.paths.append(path)


    def get_maps(self):
        _maps = []
        for path in self.paths:
            for map in path.get_maps():
                _maps.append(map)
        return _maps




phase_color = {
    0 : (255, 255, 255),
    1 : (0, 255, 0),   
    2 : (255, 255, 0),
    3 : (0, 0, 255),
    4 : (255, 0, 0),
    5 : (255, 0, 255),
    6 : (0, 255, 255),
    7 : (255, 215, 0)
}

map_color = {
    0 : (255, 255, 255),
    1 : (0, 255, 0),   
    2 : (255, 255, 0),
    3 : (0, 0, 255),
    4 : (255, 0, 0),
    5 : (255, 0, 255),
    6 : (0, 255, 255),
    7 : (255, 140, 0)
    }


def get_maps_in_radius(map, r):
    global maps_obj


def check_chains_for_map(chains : Chains, maps):
    debug = chains.get_chains()

    for chain in chains.get_chains():
        for map in chain.get_maps():
            for _map in maps:
                if map.id == _map.id:
                    logging.debug(f'Found_map_id: {_map.id} in chain: {chain.id} with map {map.id}')
                    return chain
    logging.debug(f'not_found_maps: {maps} in any chain')
    return None


def increase_maps(_maps, tier):
    _maps = (tier * 7)
    return _maps


def print_on_start(draw):
    global map_color
    offset = 20
    for map_level in map_color.keys():
        R, G, B = map_color[map_level][0], map_color[map_level][1], map_color[map_level][2]
        draw.text((W - 160, offset), 'Map LVL: ' + str(map_level), font=big_fnt, fill=(R,G,B,128))
        offset += 50

debug = False

# Get image center
center = (W/2, W/2, H/2, H/2)


def get_shortcut_maps(maps_obj, obj, tier_min_diff, tier_max_diff, N=0):
    if tier_max_diff < 1:
        return None
    logging.debug(f'calculate_shortcuts for{obj.id}')
    def takelen(elem):
        return elem[0]

    _maps = []
    for map in maps_obj:
        # Get N closest maps
        # If map argument passed check if map not the same
        if type(obj) == Map:
            if map.tier - obj.tier > tier_min_diff and \
                abs(map.tier - obj.tier) <= tier_max_diff and \
                abs(map.degree - obj.degree) > 15 and \
                len(map.get_paths()) == 1:
                if (map.unique or obj.unique) == False:
                    _maps.append((get_length(obj.Coordinates, map.Coordinates), map.id, map))
    _maps.sort(key=takelen)
    
    if N == 0:
        return _maps
    else:
        return _maps[0:N]


def get_closest_maps(maps_obj, obj, N=0):
    
    def takelen(elem):
        return elem[0]

    _maps = []
    for map in maps_obj:
        # Get N closest maps
        # If map argument passed check if map not the same
        if type(obj) == Map:
            if obj.id != map.id:
                _maps.append((get_length(obj.Coordinates, map.Coordinates), map.id, map))
    _maps.sort(key=takelen)
    
    if N == 0:
        return _maps
    else:
        return _maps[0:N]


def get_length(_coords1, _coords2):
    _length = math.sqrt( math.pow(_coords1[0]-_coords2[0], 2)  +  math.pow(_coords1[1]-_coords2[1], 2))
    return _length

def draw_tier(draw, _tier):
    global R
    global phases
    _size = (_tier + 1)*R
    phase = _tier//phases
    logging.debug(f'Drawing {_tier} with size: {_size}')
    draw.ellipse((W/2-_size, H/2-_size, W/2+_size, H/2+_size), fill=None, outline=(phase_color[phase]), width=1)


def calculate_paths(maps, max_len):
    logging.debug(f'\n\n============================= Calculate paths =============================')
    paths = Paths()
    for map_obj in maps.get_maps():
        for map_obj1 in maps.get_maps():
            _len = get_length(map_obj.Coordinates, map_obj1.Coordinates)
            # Typical path
            if (_len) <= max_len and \
                (map_obj.id != map_obj1.id) and \
                (map_obj.unique == False) and \
                (map_obj1.unique == False):
                logging.debug(f'typical_path: Length between {map_obj.id} and {map_obj1.id} is {_len}')
                # Make path
                new_path = Path(map_obj, 
                    map_obj1, 
                    _len)
                # Add path to Paths object    
                paths.add_path(new_path)
                # Attach path to map
                map_obj.add_path(new_path)
                
            # Hidden path
            # if map_obj.degree == map_obj1.degree:
            #     logging.debug(f'hidden_path: between {map_obj.id} and {map_obj1.id} is {_len}')
            #     paths.add_path(
            #         Path(
            #             map_obj,
            #             map_obj1,
            #             _len,
            #             hidden=True)
            #             )
    
    return paths


def add_hidden_paths(normal_paths, maps_obj:Maps, hidden_count, sc_count):
    all_maps = maps_obj.get_maps()
    for map in all_maps:
        if len(map.get_paths()) == 0:
            logging.debug(f'{map.id} calculate_additional_paths')
            # Get closest maps
            closest_maps = get_closest_maps(all_maps, map, hidden_count)
            logging.debug(f'{map.id} closest_maps: {closest_maps}')
            # Hiddent paths
            for _map in closest_maps:
                # Create path
                hidden_path = Path(map, _map[2], _map[0], hidden=True)
                map.add_path(hidden_path)
                normal_paths.add_path(hidden_path)

            # Get shortcuts
            # shortcuts = get_shortcut_maps(all_maps, map, 2, map.tier-4, sc_count)
            # for _map in shortcuts:
            #     # Create path
            #     short_path = Path(map, _map[2], _map[0], hidden=True, shortcut=True)
            #     map.add_path(short_path)
            #     normal_paths.add_path(short_path)
                


            


def print_paths(draw, _paths):
    logging.debug(f'\n\n============================= Drawing paths =============================')
    logging.debug(f'{_paths}')

    for _path in _paths:
        logging.debug(f'Path:{_path}')
        map1_coords = _path.map1.Coordinates
        map2_coords = _path.map2.Coordinates

        logging.debug(f'map1_coords:{map1_coords}')
        logging.debug(f'map2_coords:{map2_coords}')
        logging.debug(f'{map1_coords},{map1_coords}, {map2_coords},{map2_coords}')
        if _path.hidden == False:
            draw.line((map1_coords[0],map1_coords[1], map2_coords[0],map2_coords[1]), fill=(255,255,255), width=2)
        elif _path.hidden == True and _path.shortcut == False:
            draw.line((map1_coords[0],map1_coords[1], map2_coords[0],map2_coords[1]), fill=(128, 70, 0), width=2)
        elif _path.hidden == True and _path.shortcut == True:
            draw.line((map1_coords[0],map1_coords[1], map2_coords[0],map2_coords[1]), fill=(204,204,0), width=2)


def draw_map_obj(draw, map_objs, _size=15, draw_id=False):
    logging.debug(f'============================= Starting drawing maps =============================')
    for map_obj in map_objs:
        logging.debug(f'Drawing map : {map_obj}')
        logging.debug(f'Drawing map : {map_obj.Coordinates}')
        # Drawing map
        try:
            if map_obj.unique == True:
                logging.debug(f'Map UNIQUE!!! : {map_obj}')
                draw.ellipse(
                        (
                        int(map_obj.Coordinates[0]-_size),
                        int(map_obj.Coordinates[1]-_size),
                        int(map_obj.Coordinates[0]+_size),
                        int(map_obj.Coordinates[1]+_size)
                        ),
                        fill=(0,0,0),
                        # fill=map_color[map_obj.map_level],
                        outline=(255, 255, 255), width=2)
            else:
                draw.ellipse(
                    (
                    int(map_obj.Coordinates[0]-_size),
                    int(map_obj.Coordinates[1]-_size),
                    int(map_obj.Coordinates[0]+_size),
                    int(map_obj.Coordinates[1]+_size)
                    ),
                    fill=map_color[map_obj.map_level],
                    outline=(255, 255, 255), width=4)
        except:
            draw.ellipse(
                    (
                    int(map_obj.Coordinates[0]-_size),
                    int(map_obj.Coordinates[1]-_size),
                    int(map_obj.Coordinates[0]+_size),
                    int(map_obj.Coordinates[1]+_size)
                    ),
                    fill=map_color[map_obj.map_level],
                    outline=(255, 255, 255), width=2)
        
        # Drawing ID
        if draw_id:
            id_offset = 0
            if len(str(map_obj.id)) == 1:
                id_offset = 6
            elif len(str(map_obj.id)) == 2:
                id_offset = 11
            elif len(str(map_obj.id)) == 3:
                id_offset = 16
            if map_obj.unique == True:
                fill = (255,255,255,128)
            else:
                fill = (0,0,0,128)
            draw.text(
                        (map_obj.Coordinates[0]-id_offset,
                        map_obj.Coordinates[1]-10),
                        str(map_obj.id),
                        font=fnt,
                        fill=fill)


# Create global_chains object
global_chains = Chains()


def generate_global(request):
    # Maps container
    maps_obj = Maps()
    global global_id
    global tiers
    global phases

    global_id += 1
    logging.debug(f'\n\n\n\n\n============================= Generation started, global_id: {global_id} =============================')
    ##############

    im = Image.new('RGB', (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(im)
    # print forest
    forest_im = Image.open(os.path.dirname(__file__)+'/res/forest.png').resize((50,50))
    im.paste(forest_im, (500,500), mask=forest_im)

    vulkan_im = Image.open(os.path.dirname(__file__)+'/res/vulkan.png').resize((50,50))
    im.paste(vulkan_im, (500,550), mask=vulkan_im)

    rock_im = Image.open(os.path.dirname(__file__)+'/res/rock.png').resize((50,50))
    im.paste(rock_im, (500,600), mask=rock_im)

    water_im = Image.open(os.path.dirname(__file__)+'/res/water.png').resize((50,50))
    im.paste(water_im, (500,650), mask=water_im)

    unique_im = Image.open(os.path.dirname(__file__)+'/res/unique.png').resize((50,50))
    im.paste(unique_im, (500,850), mask=unique_im)

    ################

    print_on_start(draw)

    map_id = 0

    def define_map(_R, _tier, _size, maps_obj, degree_collision=20, draw_id=False):
        global R
        nonlocal map_id
        # map_level = 0

        draw_now = False

        map_size = 30
        degree = random.randint(0,360)
        # logging.debug(f'map_id: {map_id}')
        # logging.debug(f'degree: {degree}, collision: {degree_collision}')

        tier_maps = maps_obj.get_maps_from_tier(_tier)
        for map_obj in tier_maps:
            inf = map_obj.map_info()
            logging.debug(f'Map_obj loops: {inf}')

            logging.debug(f'Collision: map degree:{map_obj.degree}, generated degree: {degree}')

            if ((degree) <= (map_obj.degree)+degree_collision and (degree) >= (map_obj.degree)-degree_collision) or \
                ((degree+360) <= (map_obj.degree)+degree_collision and (degree+360) >= (map_obj.degree)-degree_collision) or \
                ((degree-360) <= (map_obj.degree)+degree_collision and (degree-360) >= (map_obj.degree)-degree_collision):
                # Check map_level is valid
                logging.debug(f'Collision detected! {map_obj.id}')
                old_lvl = map_obj.map_level
                if map_obj.unique != True:
                    map_obj.increase_level()
                else:
                    # If map on maximum level generate another
                    logging.debug(f'Map_already_unique map id:{map_obj.id} map_lvl:{map_obj.map_level}')
                    define_map(R, _tier, _size, maps_obj, degree_collision=degree_collision, draw_id=True)

                id_offset = 0
                if len(str(map_obj.id)) == 1:
                    id_offset = 6
                elif len(str(map_obj.id)) == 2:
                    id_offset = 11
                elif len(str(map_obj.id)) == 3:
                    id_offset = 16

                logging.debug(f'== OLD Map_defined! ==\nmap_id:{map_obj.id}\nmap_lvl:{map_obj.map_level}\nold_lvl:{old_lvl}')

                return None

        x_offset = _R * _tier * math.cos(math.radians(degree))
        y_offset = _R * _tier * math.sin(math.radians(degree)) * -1

        map_center = W/2+x_offset,H/2+y_offset
        
        logging.debug(f'offsets: {x_offset} {y_offset}')

        # (x_offset,y_offset)
        # logging.debug(_R, math.sqrt(x_offset*x_offset + y_offset*y_offset), rads)
        map_draw_coords = (W/2+x_offset-_size,H/2+y_offset-_size, W/2+x_offset+_size,H/2+y_offset+_size)

        map_id += 1

        map_obj = Map(map_id, map_center, _tier, degree, 0)

        tier_maps1.append(map_obj)
        maps_obj.add_map(map_obj)
        
        
        if draw_now:
            draw.ellipse(map_draw_coords, fill=(255,255,255), outline=(255, 255, 255), width=2)
        if debug:
            draw.line((W/2,H/2,map_center),fill=255)
            draw.text((map_center[0]+10,map_center[1]+10), str(int(degree)), font=fnt, fill=(255,0,0,128))
            draw.text((map_center[0]+25,map_center[1]+30), str(int(x_offset)) + ',' + str(int(y_offset)), font=small_fnt, fill=(255,0,0,128))
            draw.text((map_center[0]+25,map_center[1]+40), str(math.cos(degree)) + ',' + str(math.sin(degree)), font=small_fnt, fill=(255,0,0,128))
        id_offset = len(str(map_id))*5
        if draw_id:
            draw.text((map_center[0]-id_offset,map_center[1]-10), str(map_id), font=fnt, fill=(0,0,0,128))
        logging.debug(f'== NEW Map_defined! ==\nmap_id:{map_obj.id}\nmap_lvl:{map_obj.map_level}')

    for tier in range(tiers+1):
        
        tier_maps1 = []
        maps = tier * 7 + tier
        if tier == 0:
            logging.debug(f'Tier: {tier} Village')
            draw_tier(draw, tier)
        else:
            logging.debug(f'Tier: {tier}')
            draw_tier(draw, tier)
        logging.debug(f'Maps: {maps}')
        logging.debug(f'=================')
        # Define map with drawing size
        for map in range(maps):
            define_map(R, tier+1, 15, maps_obj, degree_collision=(30 - tier*1.5),draw_id=True)
    logging.debug(f'\n\n============================= Generation complete =============================')
    print('Generation completed')
    all_maps = maps_obj.get_maps()

    # Generating paths
    paths = calculate_paths(maps_obj, 120)
    add_hidden_paths(paths, maps_obj, 2, 1)

    print_paths(draw, paths.get_paths())
    draw_map_obj(draw, maps_obj.get_maps(),draw_id=True)
    
    logging.debug(f'Save jpg to: {settings.MEDIA_DIR}/global_out.jpg')
    # Out image
    im.save(settings.MEDIA_DIR+'/global_out.jpg', quality=100)

    # Remove old json
    os.remove(settings.MEDIA_DIR+"/map.json")

    # Create dict for json
    _json = {}
    for map_obj in maps_obj.get_maps():
        
        _map = map_obj.map_json_info()
        _json[_map[0]] = {'map':_map[0:-1],'paths':_map[-1]}

    # Save to json
    map_file = open(settings.MEDIA_DIR+"/map.json", "w")
    map_file.writelines(json.dumps(_json) + '\n')

    map_file.close()

    return render(request, 'map/index.html')

def index(request):
    return render(request, 'map/index.html')

def outjson(request):
    map_file = open(settings.MEDIA_DIR+"/map.json", "r")
    content = map_file.read()

    context = {'map_info':content}
    return render(request, 'map/json.html', context)