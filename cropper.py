import cv2
import cv2.cv as cv
import os
from subprocess import check_output
from time import time
import ast
import pandas as pd

PATH_INPUT = "input/"
PATH_OUTPUT = "output/crops/"
MAIN_WINDOW_NAME = "Let's draw some rectangles!"

RIGHT_ARROW = 65363
LEFT_ARROW = 65361
BACKSPACE = 65288
ESCAPE = 65307
ESCAPE2 = 27

SAVE_CROPPED_IMAGE_KEYS = [ord('s'), ord('S')]
NEXT_IMAGE_KEYS = [ord('n'), ord('N'), ord(' '), RIGHT_ARROW]
PREVIOUS_IMAGE_KEYS = [ord('b'), ord('B'), LEFT_ARROW, BACKSPACE]
QUIT_KEYS = [ord('q'), ord('Q'), ESCAPE, ESCAPE2]
CLEAR_BOXES_KEYS = [ord('c'), ord('C')]
NEXT_UNBOXED_IMAGE_KEYS = [ord('f'), ord('F')]

################################
####### global variables #######
path_out = None
boxes = None
drawing = None
ix = None
iy = None
current_fish = None
################################
################################

################################
########### structs ############
class fish():
    def construct(self):
        image = cv2.imread(self.path, cv2.CV_LOAD_IMAGE_COLOR)
        self.raw_image = image.copy()
        self.boxed_image = image.copy()
        cv2.rectangle(img=self.boxed_image,
                      pt1=(0,0),
                      pt2=(100,20),
                      color=(255,255,255), # white
                      thickness=-1) # filled
        cv2.putText(img=self.boxed_image, 
                    text=self.text,
                    org=(10,10),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.3,
                    color=(0,0,0)) # black
        for box in self.boxes:
            cv2.rectangle(self.boxed_image, box[0], box[1], (255, 0, 0), 1)
        return
    def destruct(self):
        self.raw_image = None
        self.boxed_image = None
        return
    def __init__(self, img_path, text_to_display, list_of_boxes=[], list_of_cropped_images=[]):
        self.path = img_path
        self.name = img_path.split('/')[-1]
        self.text = text_to_display
        self.raw_image = None
        self.boxed_image = None
        self.boxes = list_of_boxes
        self.cropped_images = list_of_cropped_images
        return
    def clear(self):
        for crop in self.cropped_images:
            os.remove(crop)
        self.boxes = []
        self.cropped_images = []
        self.boxed_image = self.raw_image.copy()
        return
    def append(self, box, crop):
        self.boxes.append(box)
        self.cropped_images.append(crop)
        cv2.rectangle(img=self.boxed_image, 
                      pt1=box[0], 
                      pt2=box[1], 
                      color=(255,0,0), # blue 
                      thickness=1) # very thin
        return
################################
################################

def read_log(dict_path):
    file_names = check_output(["ls", dict_path]).decode("utf8").strip().split('\n')
    image_names = [x for x in file_names if x[-4:]==".jpg"]
    boxes_dict = {}
    crops_dict = {}
    for img_name in image_names:
        boxes_dict[img_name] = []
        crops_dict[img_name] = []
    if "log.csv" in file_names:
        df = pd.read_csv(dict_path + "log.csv")
        for index, row in df.iterrows():
            img_name = row['name']
            for box in ast.literal_eval(row['boxes']):
                boxes_dict[img_name].append(box)
            for crop in ast.literal_eval(row['crops']):
                crops_dict[img_name].append(crop)
    return (boxes_dict, crops_dict)

def save_log(fishes, dict_path):
    log_list = []
    for fish in fishes:
        row = []
        row.append(fish.name)
        row.append(str(fish.boxes))
        row.append(str(fish.cropped_images))
        log_list.append(row)
    df = pd.DataFrame(log_list, columns=['name','boxes','crops'])
    df.to_csv(dict_path + "log.csv")
    return

def close_window(window_name):
    cv2.destroyWindow(window_name)
    cv2.waitKey(1)

def start_window(window_name, img):
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)
    cv2.setMouseCallback(window_name, on_mouse)
    cv2.imshow(window_name, img)

def refresh_window(window_name, new_image):
    cv2.imshow(window_name, new_image)
    cv2.waitKey(1)

def make_sure_point_on_image(x, y, image):
    x = min(max(x, 0), image.shape[1])
    y = min(max(y, 0), image.shape[0])
    return (x, y)

def on_mouse(event, x, y, flags, params):
    global path_out
    global boxes
    global log
    global current_fish
    global drawing
    global ix
    global iy
    if event == cv.CV_EVENT_LBUTTONDOWN:
        sbox = (x, y)
        boxes.append(sbox)
        drawing = True 
        ix, iy = (x, y)
    elif event == cv.CV_EVENT_LBUTTONUP:
        if drawing is not True:
            return
        drawing = False
        ebox = (x, y)
        boxes.append(ebox)
        xmin = min(boxes[-1][0], boxes[-2][0])
        xmax = max(boxes[-1][0], boxes[-2][0])
        ymin = min(boxes[-1][1], boxes[-2][1])
        ymax = max(boxes[-1][1], boxes[-2][1])
        boxes[-2] = make_sure_point_on_image(xmin, ymin, current_fish.raw_image)
        boxes[-1] = make_sure_point_on_image(xmax, ymax, current_fish.raw_image)
        if abs(boxes[-2][0] - boxes[-1][0]) < 5 or abs(boxes[-2][1] - boxes[-1][1]) < 5:
            boxes = boxes[:-2]
            return
        crop = current_fish.raw_image[boxes[-2][1]:boxes[-1][1],boxes[-2][0]:boxes[-1][0]]
        cv2.imshow('crop', crop)
        cv2.moveWindow('crop', 10, 10)
        key = cv2.waitKey(0) & 0xEFFFFF
        if key in SAVE_CROPPED_IMAGE_KEYS:
            crop_nr = len(current_fish.boxes) + 1
            crop_name = path_out + 'CROPPED_' + current_fish.name  + "_" + str(crop_nr) + ".jpg"
            cv2.imwrite(crop_name, crop)
            current_fish.append((boxes[-2], boxes[-1]), crop_name)
            print "Written to file", crop_name
        cv2.destroyWindow('crop')
        cv2.waitKey(1)
        refresh_window(MAIN_WINDOW_NAME, current_fish.boxed_image)
        boxes = boxes[:-2]
    elif event == cv.CV_EVENT_RBUTTONDOWN:
        if drawing is True:
            drawing = False
            boxes = boxes[:-1]
            refresh_window(MAIN_WINDOW_NAME, current_fish.boxed_image)
            return
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing is True:
            image_with_ghost_selection = current_fish.boxed_image.copy()
            cv2.rectangle(img=image_with_ghost_selection,
                          pt1=(ix,iy), 
                          pt2=(x,y),
                          color=(0,255,0), # light green
                          thickness=1) # very thin boundary
            refresh_window(MAIN_WINDOW_NAME, image_with_ghost_selection)

def exit_program():
    cv2.destroyAllWindows()
    for _ in xrange(5): # the only way to successfully close windows and finish
        cv2.waitKey(1)
    raise ValueError('exiting')

def paths_for_given_purpose(purpose):
    purpose = purpose.upper()
    if purpose == "TEST":
        path_in = PATH_INPUT + "test_stg1/"
        path_out = PATH_OUTPUT + "test_stg1/"
    else:
        folders = ['ALB', 'BET', 'DOL', 'LAG', 'NoF', 'OTHER', 'SHARK', 'YFT']
        if purpose not in folders:
            raise ValueError("Wrong fish")
        else:
            path_in = PATH_INPUT + "train/" + purpose + "/"
            path_out = PATH_OUTPUT + purpose + "/"
    return (path_in, path_out)
    
def gogogo(purpose):
    """
        TODO(kaszubki): and saving csv not only at the end
    """
    global path_out
    global boxes
    global current_fish
    global drawing
    
    path_in, path_out = paths_for_given_purpose(purpose)
    
    file_names = check_output(["ls", path_in]).decode("utf8").strip().split('\n')
    image_names = [x for x in file_names if x[-4:]==".jpg"]
    image_paths = [path_in + img for img in image_names]
    if not os.path.exists(path_out):
        os.makedirs(path_out)

    boxes = []
    fishes = []
    
    boxes_dict, crops_dict = read_log(path_in)
    
    for i, img_path in enumerate(image_paths):
        img_name = img_path.split('/')[-1]
        fishes.append(fish(img_path=img_path,
                           text_to_display=(str(i+1)+"/"+str(len(image_paths))),
                           list_of_boxes=boxes_dict[img_name],
                           list_of_cropped_images=crops_dict[img_name]))
    
    try:
        fish_index = 0
        display_helper = 0 # 0 if starting, 1 if need refresh, 2 otherwise
        while True:
            current_fish = fishes[fish_index]
            while True:
                if display_helper == 0:
                    current_fish.construct()
                    start_window(MAIN_WINDOW_NAME, current_fish.boxed_image)
                    display_helper = 2
                elif display_helper == 1:
                    current_fish.construct()
                    refresh_window(MAIN_WINDOW_NAME, current_fish.boxed_image)
                
                key = cv2.waitKey(0) & 0xEFFFFF # wait for a key
                
                if drawing is True: # key pressed while drawing - ignore
                    display_helper = 2
                    continue
                
                if key in NEXT_IMAGE_KEYS:
                    fish_index = (fish_index + 1) % len(fishes)
                    current_fish.destruct()
                    break
                    
                if key in PREVIOUS_IMAGE_KEYS:
                    fish_index = (fish_index + len(fishes) - 1) % len(fishes)
                    current_fish.destruct()
                    break
                    
                if key in CLEAR_BOXES_KEYS:
                    current_fish.clear()
                    refresh_window(MAIN_WINDOW_NAME, current_fish.boxed_image)
                    
                if key in NEXT_UNBOXED_IMAGE_KEYS:
                    current_index = fish_index
                    fish_index = (fish_index + 1) % len(fishes)
                    to_break = False
                    while (fish_index != current_index):
                        if (len(fishes[fish_index].boxes) == 0):
                            current_fish.destruct()
                            to_break = True
                            break
                        fish_index = (fish_index + 1) % len(fishes)
                    if to_break is True:
                        break
                        
                if key in QUIT_KEYS:
                    exit_program()
                    
            display_helper = 1
    except ValueError as e:
        print e
        
    save_log(fishes, path_in)
    return

if __name__ == "__main__":
    print "what do you want to crop? ('test' or fish name)"
    purpose = raw_input()
    gogogo(purpose)
