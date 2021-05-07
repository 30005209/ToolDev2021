#!/usr/bin/env python3

import pygame, touchgui, touchguipalate, touchguiconf, math, os
from pygame.locals import *
from array2d import array2d

#Screen / System  Info

#display_width, display_height = 800, 600
display_width, display_height = 1920, 1080
full_screen = False
#full_screen = True
toggle_delay = 250
xoffset = 0
yoffset = 0
xborder = 120  # pixels from the edge
yborder = 120  # pixels from the edge
current_map_name = "tiny.map" #static new file map name

#Colours
black = (0,0,0)
black_alt = (47,54,64)

white = (255, 255, 255)
white_alt = (245, 246, 250)

grey = (127, 143, 166)
grey_alt = (113, 128, 147)
grey_alt1 = (53, 59, 72)

red = (194, 54, 22)
red_alt = (232, 65, 24)

green = (76, 209, 55)
green_alt = ( 68, 189, 50)

blue = (0, 151, 230)
blue_alt = (0, 168, 255)

yellow = (251, 197, 49)
yello_alt = (255, 177, 44)

#Cell Info
cell_size = 100
cell_array = array2d (0, 0, " ")   #  the contents will be written to the file and is the complete 2D map

#Button Info
button_array = array2d (0, 0, [None])  #  contains just the 2D array of cells (buttons) visible on the tablet

#Enumerated Types - though python doesn't support enums, lists are functionaly equivilent for the purposes of this program
blank_t, wall_t, door_t, spawn_t, hell_t, tick_t, room_t, delete_t, ammo_s, ammo_r = list(range(10))

#Asset Info
asset_list = [] #Assets
asset_desc = {} #Dictionary of asset descriptions
asset_count = {} #Current count per asset
wall_image_name = "city2_1"
door_image_name = "adoor"

#Room Info
rooms_available = [] #any room number which was deleted is placed here
next_room = 1 #the next available room number to be used

#Tile Info
next_tile = wall_t
last_pos = [] #last saved position
start_coordinate = None

#Pallets
# preset to ensure conformity between glyph and button varients
# would have prefered to have varient constructors where a pallet could have been given
pal_spawn = green, green_alt, red, black
pal_room = blue, blue_alt, red, black

#Two preset text_tiles seperated for ease of addition in main()
# colour order is default_colour, activated_colour, pressed_colour, frozen_colour
def glyphs ():
    return [touchgui.text_tile (pal_spawn[0], pal_spawn[1], pal_spawn[2], pal_spawn[3],
                                'S', touchgui.unitY (0.05),
                                touchgui.posX (0.5), touchgui.posY (1.0),
                                100, 100, worldspawn, "worldspawn"),
            touchgui.text_tile (pal_room[0], pal_room[1], pal_room[2], pal_room[3],
                                "room", touchgui.unitY (0.05),
                                touchgui.posX (0.45), touchgui.posY (1.0),
                                100, 100, myroom, "room")]
#Wall Defs

#Save previous location of wall position
def save_wall_pos (x,y):
    global last_pos
    last_pos = (x,y)

#Queue next tile to be wall_t - chosen to remain same next_tile as it is likely when placing walls
# that multiple will be wanted
def mywall (name, tap):
    global next_tile
    pygame.display.update()
    next_tile = wall_t

#Changes tiles from empty tiles into wall tiles
def change_tile_wall (x,y):
    global cell_array, button_array, start_coordinate
    ch = cell_array.get (x + xoffset, y + yoffset)
    if ch == " ":
        cell_array.set_contents (x+ xoffset, y + yoffset, "#")
        button = button_array.get (x + xoffset, y + yoffset)
        button.to_wall ()

#Alters tiles into wall tiles along an axis
#  only effects tiles effected by change_tile_wall function - intended to be empty
def fill_wall(x,y):
	#if the x is the starting coord...
    if x == start_coordinate[0]:
	#...treat y as the min and max based on the y above (iterate over y)
        y0 = min (y, start_coordinate[1])
        y1 = max (y, start_coordinate[1])

	#...iterate through y0 up to the tile following y1
        for j in range(y0, y1+1):
	    #change tiles to walls as appropriate
            change_tile_wall (x, j)

	#If x is not the starting coord & y is at it's start coord...
    elif y == start_coordinate[1]:
	#...treat x as the min and max based on the x above
        x0 = min (x, start_coordinate[0])
        x1 = max (x, start_coordinate[0])

	#...iterate through x0 up to the tile following x1
        for i in range (x0, x1+1):
	    #change tiles to walls as appropriate
            change_tile_wall(i,y)

#Set the current contents of a given button to a wall
def create_wall (button, x, y, tap):
    global next_tile, cell_array, start_coordinate
    button.to_wall ()
    cell_array.set_contents (x + xoffset, y + yoffset, "#")
    next_tile = wall_t
    #If the tile has been double tapped 
    if tap == 2:
	#set the start coordinate
        start_coordinate = [x,y]
    #If the start_coordinate has been set
    if start_coordinate != None:
	#fill all blank spaces between there and the new pos with walls
        fill_wall(x,y)

def match_line (x, y):
    return (last_pos != []) and ((last_pos[0] == x) or (last_pos[1] == y))

#Button Defs

class button:
    #constructor that defines x,y pos and size
    def __init__ (self, x, y, size):
        self._x = x
        self._y = y
        self._size = size
        #create a tile at given location - target by default (acts as pseudo cursor)
        self._tile = touchgui.image_tile (blank_list("targ", size),
                                          x, y,
                                          size, size, cellback)

    #can be altered to following buttons as described by def title
    def to_blank (self):
        self._tile.set_images (blank_list ("targ", cell_size))
    def to_wall (self):
        self._tile.set_images (wall_list (wall_image_name, cell_size))
    def to_door (self):
        self._tile.set_images (door_list (door_image_name, cell_size))
    def to_hell (self):
        self._tile.set_images (image_list ("hellknight"))
    def to_tick (self):
        self._tile.set_images (image_list ("tick"))
    def to_ammo_s (self):
        self._tile.set_images (image_list ("ammo_s"))
    def to_ammo_r (self):
        self._tile.set_images (image_list ("ammo_r"))
    #def to_rocketL (self):
    #    self._tile.set_images (image_list ("rocketL"))
    def to_room (self, room):
        self._tile = touchgui.text_tile (pal_room[0], pal_room[1], pal_room[2], pal_room[3],
                                         room, self._size,
                                         self._x, self._y,
                                         self._size, self._size, delroom, "room")
    def to_spawn (self):
        self._tile = touchgui.text_tile (pal_spawn[0], pal_spawn[1], pal_spawn[2], pal_spawn[3],
                                         'S', self._size,
                                         self._x, self._y,
                                         self._size, self._size, worldspawn, "worldspawn")
    def spawn_to_blank (self):
        self._tile = touchgui.image_tile (blank_list ("wallv", self._size),
                                          self._x, self._y,
                                          self._size, self._size, cellback)
	#Return a given tile
    def get_tile (self):
        return self._tile

#Remake the button array using array2d
def recreate_button_grid ():
    global button_array
    button_array = array2d (0, 0, [None])


#Define the given buttons
#  constructor layout: image_list, x, y, width, height, action (defaults to None)
def buttons ():
    return [touchgui.image_tile (button_list ("power"),
                                 touchgui.posX (0.95), touchgui.posY (1.0),
                                 100, 100, myquit),
            touchgui.image_tile (button_list ("export"),
                                 touchgui.posX (0.0), touchgui.posY (1.0),
                                 100, 100, myexport),
            touchgui.image_tile (button_list ("buttonStart"),
                                 touchgui.posX (0.05), touchgui.posY (1.0),
                                 100, 100, mydoom3),
            touchgui.image_tile (button_list ("smaller"),
                                 touchgui.posX (0.0), touchgui.posY (0.10),
                                 100, 100, myzoom, True),
            touchgui.image_tile (button_list ("larger"),
                                 touchgui.posX (0.95), touchgui.posY (0.10),
                                 100, 100, myzoom, False)]

#  get_button - returns an existing cell if it exists, or create a new blank button.
def get_button (i, j, x, y, size):
    global cell_array, button_array
    if cell_array.inRange (xoffset + i, yoffset + j):
        if button_array.inRange (xoffset + i, yoffset + j):
            b = button_array.get (xoffset + i, yoffset + j)
            if b != None:
                return b
        content = cell_array.get (xoffset + i, yoffset + j)
        b = button (x, y, size)
	#Convert as appropriate
        if content == "v":
            b.to_wall ()
	#Convert as appropriate
        elif content == "|":
            b.to_door ()
        button_array.set_contents (xoffset + i, yoffset + j, [b])
        return b
    b = button (x, y, size)
    b.to_blank ()
    cell_array.set_contents (xoffset + i, yoffset + j, " ")
    button_array.set_contents (xoffset + i, yoffset + j, [b])
    return b


def finished ():
    return clicked


def button_grid (size):
    global clicked
    clicked = False
    b = []
    for i, x in enumerate (range (xborder, display_width-xborder, size)):
        for j, y in enumerate (range (yborder, display_height-yborder, size)):
            c = get_button (i, j, x, y, size)
            assert (c != None)
            b += [c.get_tile ()]
    return b

#Room Defs

#Room deletion definition
def delroom (param, tap):
    global clicked, cell_array, button_array, double_tapped_cell, rooms_available
	#flag mouse click as true
    clicked = True
	#get current pos of mouse
    mouse = pygame.mouse.get_pos()
	#covert the raw position of the mouse to one bound by cells
    x, y = get_cell (mouse)
	#take into account any offsets in x and y
    button = button_array.get (x + xoffset, y + yoffset)
	#return the tile to a blank tile
    button.spawn_to_blank ()
	#add the current number back into the pool of available numbers
    rooms_available += [cell_array.get (x + xoffset, y + yoffset)]
	#set the other bookept varient to match
    cell_array.set_contents (x + xoffset, y + yoffset, " ")

#Room definition
def myroom (name, tap):
    global next_tile
    pygame.display.update()
	#keep the next click to also be a room_tile - chosen as labelling of rooms is likely to be done at the end
    if tap == 1:
        next_tile = room_t

#get the next avaiable room number
def get_next_room():
    global rooms_available, next_room
	#if available is blank...
    if rooms_available == []:
	#set the room to a character variant
        room = chr (next_room + ord ("0"))
	#increment the room
        next_room +=1
    else:
	#set room to first element in list and rooms_available as remainder
        room, rooms_available = car_cdr (rooms_available)
    return room

#create a room
def create_room(button, x,y, tap):
    global next_tile, cell_array
	#find appropriate information of room based on get_next_room func
    room = get_next_room()
	#convert the button into a room
    button.to_room(room)
	#set the contents of the cell array (double bookeeping)
    cell_array.set_contents (x + xoffset, y + yoffset, room)
	#include in thelist of assets
    include_asset (room, "room "+room)
	#keep the next click to also be a room_tile - chosen as labelling of rooms is likely to be done at the end
    next_tile = room_t

#Spawn Defs
#Removes the spawn
def delspawn (param, tap):
    global clicked, cell_array, button_array, double_tapped_cell
    clicked = True
	#get mouse pos
    mouse = pygame.mouse.get_pos()
	#covert the raw position of the mouse to one bound by cells
    x, y = get_cell (mouse)
	#take into account any offsets in x and y
    button = button_array.get (x + xoffset, y + yoffset)
	#place a blank in place
    button.spawn_to_blank ()

#Prep world spawn
def worldspawn (name, tap):
    global next_tile
	#Refresh the scene via update
    pygame.display.update ()
    if tap == 1:
	#Change next tile to be a spawn
        next_tile = spawn_t

#Create world spawn
def create_spawn (button, x, y, tap):
    global next_tile, cell_array
	#convert to spawn button
    button.to_spawn ()
	#taking into account offsets
    cell_array.set_contents (x + xoffset, y + yoffset, "s")
	#list it in the includes
    include_asset ('s', "worldspawn")
	#Set the next to a blank - plays should have only added one spawn and it
	# is unlikely to be a correct guess if a random tile is chosen to be next - blank is safest
    next_tile = blank_t

#System Defs

def event_test (event):
	#Should a keydown be present and the escape key be one of them
    if (event.type == KEYDOWN) and (event.key == K_ESCAPE):
	#quit
        myquit (None)
	#If any other user event is done add it
    if event.type == USEREVENT+1:
        reduceSignal ()

def myquit (name = None, tap = 1):
	#Complete a final update of screen
    pygame.display.update ()
	#Delay for a moment - this is to show feedback to the player rather than just closing instantly
    pygame.time.delay (toggle_delay * 2)
	#quit program
    pygame.quit ()
    quit ()

#File Defs

#Run the d3 shell script
#	due to the engine from ID we are also able to queue commands such as launching the tiny.map
#	also triggers the launching of chisel
def dmap():
    #Make it run initially as a shell then a as a bash
    os.system('/bin/bash -c "d3 +dmap tiny.map +quit"')

#Run doom3 and tiny.map within it
def exec_doom_map():
    #Make it run initially as a shell then a as a bash
    os.system('/bin/bash -c "d3 +map tiny.map"')

def mydoom3 (param, tap):
    pygame.display.update() #flush all changes
    pygame.time.delay(toggle_delay * 2) #pause
    try_export(os.getcwd(), current_map_name) #export a test.txt file
    pygame.quit() #shutdown pygame
    dmap() #run chisel and dmap doom3 compile
    exec_doom_map() #now run doom3
    quit() #quit python

#Check to see the extremites based on finding non blanks
# return this as a couple (left then right)
def determine_range ():
    left = -1
    x, y = cell_array.high ()
    right = x
    for j in range (y):
        for i in range (x):
            if cell_array.get (i, j) != " ":
                if (left == -1) or (i < left):
                    left = i
                if i > right:
                    right = i
    return left, right

#Write a map
def write_map (f):
	#determine extremities
    left, right =determine_range ()
	#create a blank string (to act as the file)
    m=""
	#dictionary used
    mdict = {"v":"#", "h":"#", "-":".", "|":".", " ":" ","H":"H", "s":"s", "T":"T"}
    x, y = cell_array.high ()
	#iterate over x and y
    for j in range (y):
        for i in range (left, right+1):
		#should the cell in the array be in the dictionary
            if cell_array.get (i, j) in mdict:
		#add it to the file
                m+=mdict[cell_array.get (i, j)]
            else:
                m+=cell_array.get (i, j)
            #skip blank lines
        m=m.rstrip ()
	# if the length of m is non 0
        if len (m) > 0:
		#create a new line as it means there was items present on the current line
            m+="\n"
	#write a file using the created string
    f.write (m)
    return f

def write_asset (f, asset):
    #Write string
    #Asset into first %s
    #Asset_desc into second %s
    s = "define %s %s\n" % (asset, asset_desc[asset])
    #Write file
    f.write(s)
    #Return the modified file
    return f

def write_assets(f):
    #For the list of assets...
    for asset in asset_list:
        #...write each asset
        f = write_asset (f, asset)
    #Return the modified file
    return f

#Open a fil
def load_map (name):
	#open the file with read priviliges
    f=open (name, "r")
	#read the map
    f=read_map (f)
	#close the file
    f.close ()

#Import last created file
def importLast(tap):
	myimport(current_map_name, tap)


#Import a given file
def myimport (name, tap):
    global clicked
    pygame.display.update ()
    load_map (name)
    clicked = True
    pygame.display.update ()

#Read the entirity of the floor of the given lines
def read_floor (lines):
    seen_start = False
    y=0
    ypos = 0
	#iterate over the lines
    for line in lines:
	#if the line is greater than 0...
        if len (line) > 0:
		#..and if if the line when split is > 0
            if len (line.split ("#")) > 0:
		# you have found the start of the line
                seen_start = True
		#If you have found the start of the line
            if seen_start:
		#add a line of buttons
                add_xaxis (line, y, ypos)
		#increment the number of rows
                y+=1
		#increment the cell_size based on ypos
                ypos += cell_size

#From a given file read the lines assests and floor
def read_map (f):
	#The lines are set to the lines from the file
    lines = f.readlines ()
	#read the assets of the lines
    read_assets (lines)
	#read the floor of the lines
    read_floor (lines)
	#return the file
    return f

#
#add_xaxis - adds a line of buttons.
#            y is the index on the yaxis.  posy is the screen coordinate.
#
def add_xaxis (line, y, ypos):
    global cell_array, button_array
    xpos = 0
    x=0
    for ch in line:
        b=button (xborder + xpos, yborder + ypos, cell_size)
        if ch == "#":
            cell_array.set_contents (xoffset+x, yoffset+y, "v")
            b.to_wall ()
        elif ch == " ":
            cell_array.set_contents (xoffset+x, yoffset+y, " ")
        button_array.set_contents (xoffset+x, yoffset+y, [b])
        xpos += cell_size
        x+=1

#Read the assets in a given line
def read_assets (lines):
    for line in lines:
        words = line.lstrip ().split ()
        if (len (words) > 2) and (words[0] == "define"):
            include_asset (words[1], words[2])


def save_map (name):
    #Opens a file
    f = open(name, "w+")
    #Writes asset
    f = write_assets(f)
    #Add blank line to aid viewing
    f.write ("\n")
    #Write map
    f = write_map(f)
    #Close file
    f.close ()

def myexport (name, tap):
    #Update pygame
    pygame.display.update()
    #Save map
    save_map(current_map_name)
    try_export(os.getcwd (), current_map_name)

#Export the given map name to a directory
def try_export (directory, map_name):
    os.chdir (os.path.join (os.getenv ("HOME"), "Sandpit/chisel/python"))
    r=os.system ("./developer-txt2map " + os.path.join (directory, map_name))
    os.chdir (directory)
    if r == 0:
        print ("all ok")
    else:
        print("not ok")


#Spawnable Defs

def hellknight (name, tap):
    global next_tile
    pygame.display.update ()
    if tap == 1:
        next_tile = hell_t

def create_hell(button, x, y, tap):
    global next_tile, cell_array
    button.to_hell()
    cell_array.set_contents (x + xoffset, y + yoffset, "H")
    include_asset ('H', "monster monster_demon_hellknight")
    next_tile = hell_t

def tick (name, tap):
    global next_tile
    pygame.display.update()
    if tap == 1:
        next_tile = tick_t

def create_tick(button, x, y, tap):
    global next_tile, cell_array
    button.to_tick()
    cell_array.set_contents (x + xoffset, y + yoffset, "T")
    include_asset ('T', "monster monster_demon_tick")
    next_tile = tick_t

def ammo_s (name, tap):
    global next_tile
    pygame.display.update()
    if tap == 1:
        next_tile = ammo_s

def create_ammo_s (button, x, y, tap):
    global next_tile, cell_array
    button.to_ammo_s()
    cell_array.set_contents (x + xoffset, y + yoffset, "H")
    include_asset ('H', "ammo_shells_large 32")
    next_tile = ammo_s

def ammo_r (name, tap):
    global next_tile
    pygame.display.update()
    if tap == 1:
        next_tile = ammo_r

def create_ammo_r (button, x, y, tap):
    global next_tile, cell_array
    button.to_ammo_r()
    cell_array.set_contents (x + xoffset, y + yoffset, "R")
    include_asset ('R', "ammo ammo_rockets_large 16")
    next_tile = ammo_r

def mydoor (name, tap):
    global next_tile
    pygame.display.update()
    next_tile = door_t

def mytrash(name, tap):
    global next_tile
    pygame.display.update ()
    if tap == 1:
        next_tile = blank_t


def libimagedir (name):
    return os.path.join (touchguiconf.touchguidir, name)

#Lists

def button_list (name):
    return [touchgui.image_gui (libimagedir ("images/PNG/White/2x/%s.png") % (name)).white2grey (.5),
            touchgui.image_gui (libimagedir ("images/PNG/White/2x/%s.png") % (name)).white2grey (.1),
            touchgui.image_gui (libimagedir ("images/PNG/White/2x/%s.png") % (name)).white2red(),
            touchgui.image_gui (libimagedir ("images/PNG/White/2x/%s.png") % (name)).white2blue()]


def private_list (name):
    return [touchgui.image_gui ("%s.png" % (name)),
            touchgui.image_gui ("%s.png" % (name)),
            touchgui.image_gui ("%s.png" % (name)).white2red(),
            touchgui.image_gui ("%s.png" % (name)).white2blue()]

def image_list(name):
    return [touchgui.image_gui ("%s.png" % (name)),
            touchgui.image_gui ("%s.png" % (name)),
            touchgui.image_gui ("%s.png" % (name)).white2red(),
            touchgui.image_gui ("%s.png" % (name)).white2blue()]

def private_quake (name):
    return [touchgui.image_gui ("%s.png" % (name)),
            touchgui.image_gui ("%s.png" % (name)),
            touchgui.image_gui ("%s.png" % (name)).white2red(),
            touchgui.image_gui ("%s.png" % (name)).white2blue()]

def blank_list (name, size):
    return [touchgui.image_gui ("%s.png" % (name)).resize (size, size),
            touchgui.color_tile (touchguipalate.black, size, size),
            touchgui.image_gui ("%s.png" % (name)).resize (size, size),
            touchgui.image_gui ("%s.png" % (name)).resize (size, size)]


def wall_list (orientation, size):
    return [touchgui.image_gui ("%s.png" % (orientation)).resize (size, size),
            touchgui.image_gui ("%s.png" % (orientation)).resize (size, size),
            touchgui.image_gui ("%s.png" % (orientation)).resize (size, size),
            touchgui.image_gui ("%s.png" % (orientation)).resize (size, size)]


def door_list (orientation, size):
    return [touchgui.image_gui ("%s.png" % (orientation)).resize (size, size),
            touchgui.image_gui ("%s.png" % (orientation)).resize (size, size),
            touchgui.color_tile (touchguipalate.black, size, size),
            touchgui.color_tile (touchguipalate.black, size, size)]


def myzoom (is_larger, tap):
    global cell_size, clicked

    clicked = True
    if is_larger:
        cell_size += 10
    else:
        cell_size -= 10
    recreate_button_grid ()


#Asset Defs

def assets ():
    return [touchgui.image_tile (private_list ("hellknight"),
                                 touchgui.posX (0.95), touchgui.posY (0.5),
                                 100, 100, hellknight),
            touchgui.image_tile (private_list ("tick"),
                                 touchgui.posX (0.95), touchgui.posY (0.4),
                                 100, 100, tick),
            touchgui.image_tile (image_list (wall_image_name),
                                 touchgui.posX (0.0), touchgui.posY (0.5),
                                 100, 100, mywall),
            touchgui.image_tile (image_list (door_image_name),
                                 touchgui.posX (0.0), touchgui.posY (0.4),
                                 100, 100, mydoor),
            touchgui.image_tile (private_list ("ammo_s"),
                                 touchgui.posX (0.0), touchgui.posY (0.3),
                                 100, 100, ammo_s),         
	   touchgui.image_tile (private_list ("ammo_r"),
                                 touchgui.posX (0.0), touchgui.posY (0.2),
                                 100, 100, ammo_r),
            touchgui.image_tile (button_list ("trashcanOpen"),
                                 touchgui.posX (0.55), touchgui.posY (1.0),
                                 100, 100, mytrash)]

def include_asset (asset, desc):
    global asset_list, asset_desc, asset_count
    #If asset is not in list...
    if not (asset in asset_list):
        #...add to list
        asset_list += [asset]
        #and add description
        asset_desc[asset] = desc
    #If it exists in the dictionary...
    if asset in asset_count:
        #...increment the count
        asset_count[asset] +=1
    else:
        #Otherwise set it to 1
        asset_count[asset] = 1

def exclude_asset (asset):
    global asset_list, asset_count
    #If asset exists in dictionary...
    if asset in asset_count:
        #...decrement the asset count
        asset_count[asset] -= 1
        #If the asset count reaches 0...
        if asset_count[asset] == 0:
            #...delete the asset_count
            del asset_count[asset]
            #and remove from the asset_list
            asset_list.remove[asset]

def mygrid (name, tap):
    print("grid callback")


def blank (x, y, size):
    b = touchgui.image_tile (blank_list ("target", size),
                             x, y,
                             size, size, cellback)
    assert (b != None)
    return b

#Cell Defs
double_tapped_cell = None
def get_cell (mouse):
    x, y = mouse
    x -= xborder
    y -= yborder
    return int (x / cell_size), int (y / cell_size)

def create_blank (button, x, y, tap):
    global next_tile, cell_array
    button.to_blank ()
    cell_array.set_contents (x + xoffset, y + yoffset, " ")
    next_tile = blank_t

def create_door (button, x, y, tap):
    global next_tile, cell_array
    button.to_door ()
    cell_array.set_contents (x + xoffset, y + yoffset, ".")
    include_asset ('.', "door")
    next_tile = door_t


#
#   pre-condition: l is a list of 1 or more elements
#   post-condition: returns two values: first element of the list l and the remainder of the list l
#                   from the 2nd element (if it exists upwards). Empty list is returned is the l has one element
#
def car_cdr (l):
    first = l[0]
    if len(l) == 1:
        remainder = []
    else:
        remainder = l[1:]
    return first, remainder


def delete_coordinate(button, x,y, tap):
    global next_tile, cell_array
    button.to_blank()
    ch = cell_array.get(x,y)
    exclude_asset(ch)
    cell_array.set_contents(x + xoffset, y + yoffset, " ")
    next_tile = delete_t

#
#draw_line - draw a line from the last_pos to, [x, y] providing [x, y]
#          lies on the same axis.
#
def draw_line (x, y):
    global cell_array, button_array
    if last_pos != []:
        if last_pos[0] == x:
            for j in range (min (y, last_pos[1]), max (y, last_pos[1])+1):
                old = cell_array.get (x, j)
                button = button_array.get (x, j)
                if old == " ":
                    button.to_wall ()
                    cell_array.set_contents (x, j, "v")
                elif last_pos[1] == y:
                    for i in range (min (x, last_pos[0]), max (x, last_pos[0])+1):
                        old = cell_array.get (i, y)
                        button = button_array.get (i, y)
                        if old == " ":
                            button.to_wall ()
                            cell_array.set_contents (i, y, "v")
def cellback (param, tap):
    global clicked, cell_array, button_array, double_tapped_cell
    clicked = True
    #get mouse pos
    mouse = pygame.mouse.get_pos ()
    #gets cell pos (button)
    x, y = get_cell (mouse)
    button = button_array.get (x + xoffset, y + yoffset)
    function_create[next_tile] (button, x, y, tap)


#Dictionary with associative function calls
function_create = {blank_t:create_blank,
                   wall_t:create_wall,
                   door_t:create_door,
                   spawn_t:create_spawn,
                   hell_t:create_hell,
                   tick_t:create_tick,
                   room_t:create_room,
                   delete_t:delete_coordinate,
                   ammo_s:create_ammo_s,
	           ammo_r:create_ammo_r}


def main ():
    global players, grid, cell_size

    pygame.init ()
    if full_screen:
        gameDisplay = pygame.display.set_mode ((display_width, display_height), FULLSCREEN)
    else:
        gameDisplay = pygame.display.set_mode ((display_width, display_height))

    touchgui.set_display (gameDisplay, display_width, display_height)
    controls = buttons () + glyphs () + assets ()

    while True:
        grid = button_grid (cell_size)
        forms = controls + grid
        touchgui.select (forms, event_test, finished)


main ()
