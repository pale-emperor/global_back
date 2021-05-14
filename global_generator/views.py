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

# Create picture
# im = Image.new('RGB', (W, H), (0, 0, 0))
# draw = ImageDraw.Draw(im)

# Set font
fnt = ImageFont.truetype("/home/wh1te/global_back/global_generator/res/lucon.ttf", 18)
small_fnt = ImageFont.truetype("/home/wh1te/global_back/global_generator/res/lucon.ttf", 12)
big_fnt = ImageFont.truetype("/home/wh1te/global_back/global_generator/res/lucon.ttf", 24)




# Empty map list
map_dict = {}

####################################



####################################


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
    7 : (255, 215, 0)
    }


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


def maps_info(map_dict):
    for tier in range(tiers):
        logging.debug(f'Tier: {tier}')
        for _map in (map_dict[tier]):
            logging.debug(_map)


def get_map_with_coords(map_dict):
    coords_id = []
    for tier in range(tiers):
        # logging.debug(f'Tier:  {tier}')
        for _map in (map_dict[tier]):
            # logging.debug(_map[0]['Coordinates'])
            coords_id.append((_map[0]['Coordinates'],_map[0]['id']))
    return coords_id
    logging.debug(coords)


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


def calculate_paths(_map_dict):
    paths = []
    logging.debug(f'============================= Calculate paths =============================')
    # Run for all maps
    for _map in get_map_with_coords(_map_dict):
        for __map in get_map_with_coords(_map_dict):
            _len = get_length(_map[0],__map[0])
            if (_len) <= 100 and (_map[1] != __map[1]):
                logging.debug(f'Length between {_map[1]} and {__map[1]} is {_len}')
                paths.append( 
                        (
                        {
                        'map1':{'id':_map[1], 'coords':_map[0]}, 
                        'map2':{'id':__map[1], 'coords':__map[0]},
                        'length':_len
                        }
                        )
                    )
    return paths


def print_paths(draw, _paths):
    logging.debug(f'Drawing paths\n=========================================================')
    logging.debug(f'{_paths}')

    for _path in _paths:
        logging.debug(f'Path:{_path}')
        print(_path.keys())
        map1_coords = _path['map1']['coords']
        map2_coords = _path['map2']['coords']

        logging.debug(f'map1_coords:{map1_coords}')
        logging.debug(f'map2_coords:{map2_coords}')
        logging.debug(f'{map1_coords},{map1_coords}, {map2_coords},{map2_coords}')
        draw.line((map1_coords[0],map1_coords[1], map2_coords[0],map2_coords[1]), fill=(255,255,255), width=2)


def print_maps(draw, _map_dict, _size=15, draw_id=False):
    logging.debug(f'============================= Starting drawing maps =============================')
    for _tiers in _map_dict.keys():
        for _map in _map_dict[_tiers]:
            logging.debug(f'Drawing map : {_map}')
            # Drawing map
            try:
                if _map[0]['unique'] == True:
                    logging.debug(f'Map UNIQUE!!! : {_map}')
                    draw.ellipse(
                            (
                            int(_map[0]['Coordinates'][0]-_size),
                            int(_map[0]['Coordinates'][1]-_size),
                            int(_map[0]['Coordinates'][0]+_size),
                            int(_map[0]['Coordinates'][1]+_size)
                            ),
                            fill=(0,0,0),
                            # fill=map_color[_map[0]['map_level']],
                            outline=(255, 255, 255), width=2)
                else:
                    draw.ellipse(
                        (
                        int(_map[0]['Coordinates'][0]-_size),
                        int(_map[0]['Coordinates'][1]-_size),
                        int(_map[0]['Coordinates'][0]+_size),
                        int(_map[0]['Coordinates'][1]+_size)
                        ),
                        fill=map_color[_map[0]['map_level']],
                        outline=(255, 255, 255), width=4)
            except:
                draw.ellipse(
                        (
                        int(_map[0]['Coordinates'][0]-_size),
                        int(_map[0]['Coordinates'][1]-_size),
                        int(_map[0]['Coordinates'][0]+_size),
                        int(_map[0]['Coordinates'][1]+_size)
                        ),
                        fill=map_color[_map[0]['map_level']],
                        outline=(255, 255, 255), width=2)
            
            # Drawing ID
            if draw_id:
                id_offset = 0
                if len(str(_map[0]['id'])) == 1:
                    id_offset = 6
                elif len(str(_map[0]['id'])) == 2:
                    id_offset = 11
                elif len(str(_map[0]['id'])) == 3:
                    id_offset = 16
                draw.text(
                            (_map[0]['Coordinates'][0]-id_offset,
                            _map[0]['Coordinates'][1]-10),
                            str(_map[0]['id']),
                            font=fnt,
                            fill=(0,0,0,128))


def generate_global(request):

    global global_id
    global tiers
    global phases

    global_id += 1
    logging.debug(f'\n\n\n\n\n=========================================================\nGeneration started, global_id: {global_id} \n=========================================================')
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

    def define_map(_R, _tier, _size, tier_maps, degree_collision=20, draw_id=False):
        global R
        nonlocal map_id
        # map_level = 0

        draw_now = False

        map_size = 30
        degree = random.randint(0,360)
        logging.debug(f'map_id: {map_id}')
        logging.debug(f'degree: {degree}, collision: {degree_collision}')
        for _map in tier_maps:
            # logging.debug('Map loops:',_map)
            if ((degree) <= (_map[0]['degree'])+degree_collision and (degree) >= (_map[0]['degree'])-degree_collision) or \
                ((degree+360) <= (_map[0]['degree'])+degree_collision and (degree+360) >= (_map[0]['degree'])-degree_collision):
                # Check map_level is valid
                if _map[0]['map_level'] == len(map_color)-1:
                    logging.debug(f'Map on maximum level, set map : {_map[0]} to unique')
                    _map[0]['unique'] = True
                else:
                    _map[0]['unique'] = False
                    _map[0]['map_level'] += 1

                id_offset = 0
                if len(str(_map[0]['id'])) == 1:
                    id_offset = 6
                elif len(str(_map[0]['id'])) == 2:
                    id_offset = 11
                elif len(str(_map[0]['id'])) == 3:
                    id_offset = 16

                return None

        x_offset = _R * _tier * math.cos(math.radians(degree))
        y_offset = _R * _tier * math.sin(math.radians(degree)) * -1

        map_center = W/2+x_offset,H/2+y_offset
        
        logging.debug(f'offsets: {x_offset} {y_offset}')

        # (x_offset,y_offset)
        # logging.debug(_R, math.sqrt(x_offset*x_offset + y_offset*y_offset), rads)
        map_draw_coords = (W/2+x_offset-_size,H/2+y_offset-_size, W/2+x_offset+_size,H/2+y_offset+_size)

        map_id += 1
        map_info = [{'id': map_id, 'Coordinates' : map_center, 'map_tier': _tier, 'degree' : degree, 'map_level' : 0}]
        tier_maps.append(map_info)
        
        
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


    for tier in range(tiers+1):
        tier_maps = []
        maps = tier * 7
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
            define_map(R, tier+1, 15, tier_maps, degree_collision=(30 - tier*1.5),draw_id=True)
        map_dict.update({tier : tier_maps})
    logging.debug(f'Generation complete\n=========================================================')

    logging.debug(maps_info(map_dict))

    paths = calculate_paths(map_dict)

    print_paths(draw, paths)
    print_maps(draw, map_dict,draw_id=True)
    
    logging.debug(f'Save jpg to: {settings.MEDIA_DIR}/global_out.jpg')
    # Out image
    im.save(settings.MEDIA_DIR+'/global_out.jpg', quality=100)
    # Save to json
    map_file = open(settings.MEDIA_DIR+"/map.json", "w")
    map_file.writelines(str(json.dumps(map_dict)))
    map_file.close()

    return render(request, 'map/index.html')

def index(request):
    return render(request, 'map/index.html')

def outjson(request):
    map_file = open(settings.MEDIA_DIR+"/map.json", "r")
    # print(settings.MEDIA_DIR+"/map.json")
    content = map_file.read()
    print(content[1])
    context = {'map_info':content}
    print(context)
    return render(request, 'map/json.html', context)