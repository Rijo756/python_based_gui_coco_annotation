import tkinter as tk
from tkinter import filedialog, ttk
import json
from PIL import Image, ImageTk, ImageDraw
import cv2, os
import numpy as np
import pycocotools.mask as mask_utils

import gc

class AnnotationViewer:
    '''
    This is a simple gui made with tkinter for the annotations to be saved in coco dataset format.
    '''
    
    def __init__(self, master, categories):
        self.master = master
        self.master.title("Cell Annotation Tool")
        
        self.img_frame = tk.Frame(self.master, width=800, height=800)
        self.img_frame.pack(side=tk.LEFT)
        self.canvas = tk.Canvas(self.img_frame, width=1000, height=1000)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.draw_button = tk.Button(self.master, text="Show_all", command=self.draw_all_annotation)
        self.draw_button.place(relx=0.89, rely=0.16, anchor=tk.CENTER)

        self.draw_button2 = tk.Button(self.master, text="clear", command=self.clear_all_annotation)
        self.draw_button2.place(relx=0.95, rely=0.16, anchor=tk.CENTER)

        self.draw_button3 = tk.Button(self.master, text="Del Polygon", command=self.on_del_polygon)
        self.draw_button3.place(relx=0.81, rely=0.85, anchor=tk.CENTER)

        self.draw_button4 = tk.Button(self.master, text="Save Polygon", command=self.on_save_polygon)
        self.draw_button4.place(relx=0.89, rely=0.85, anchor=tk.CENTER)

        self.draw_button5 = tk.Button(self.master, text="Add Cell", command=self.on_add_new_cell)
        self.draw_button5.place(relx=0.96, rely=0.85, anchor=tk.CENTER)

        self.draw_button6 = tk.Button(self.master, text="Save", command=self.on_save_results)
        self.draw_button6.place(relx=0.96, rely=0.96, anchor=tk.CENTER)

        self.annotation_frame = tk.Frame(self.master, width=300, height=600)
        self.annotation_frame.pack(side=tk.RIGHT)
        self.annotation_listbox = tk.Listbox(self.annotation_frame, width=30, height=30)
        self.annotation_listbox.pack()
        self.annotation_listbox.bind('<<ListboxSelect>>', self.on_annotation_select)

        self.category_frame = tk.Frame(self.annotation_frame, width=300, height=50)
        self.category_frame.pack(side=tk.TOP)
        self.category_label = tk.Label(self.category_frame, text="Object Category:")
        self.category_label.pack(side=tk.LEFT)
        self.category_options = categories  # Change this to your desired category list
        self.category_combobox = ttk.Combobox(self.category_frame, values=self.category_options)
        self.category_combobox.pack(side=tk.LEFT)
        self.category_combobox.bind("<<ComboboxSelected>>", self.on_category_select)
                
        self.load_button = tk.Button(self.master, text="Load Image", command=self.load_image)
        self.load_button.pack()
        self.set_initial_val()

        # Bind the close event to the window
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def set_initial_val(self):
        # Call garbage collector to free up memory
        gc.collect()

        #function variables 
        self.image = None
        self.photo_image = None
        self.annotations = {}
        self.index = None
        self.selected_annotation = None
        self.selected_category = None
        self.selected_polygon = None
        self.current_polygon = []
        self.current_points = []
        self.canvas_points = []
        self.height = None
        self.width = None
        
    def load_image(self):
        '''
        function to load images and current annotations (both should have same name)
        '''
        #reset values each time load image
        self.set_initial_val()
        image_path = filedialog.askopenfilename(title="Select Image", filetypes=[])

        if image_path:
            self.image = Image.open(image_path)
            self.photo_image = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor="nw", image=self.photo_image)
            self.canvas.config(width=self.image.width, height=self.image.height)
            #load the annotation 
            annotation_path = image_path.replace(".jpg", ".json").replace(".jpeg", ".json").replace(".png", ".json")
            self.annotation_path = annotation_path

            with open(annotation_path, "r") as f:
                self.annotations_all = json.load(f)

            self.height = self.annotations_all['images']['height']
            self.width = self.annotations_all['images']['width']

            self.annotations = self.annotations_all['annotations']
            print ('loading annotations..')
            for anno in self.annotations:
                anno["segmentation"] = self.rle_to_polygon(anno["segmentation"])
            self.populate_annotation_list()
            
    def populate_annotation_list(self):
        '''
        Function to show the listbox with cell ids
        '''
        self.annotation_listbox.delete(0, tk.END)
        for annotation in self.annotations:
            self.annotation_listbox.insert(tk.END, annotation["id"])
            
    def on_annotation_select(self, event):
        '''
        actions to do when a cell is selected from the list box
        '''
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            self.index = index
            self.selected_annotation = self.annotations[index]
            print ('Selected cell:', self.selected_annotation['id'])
            self.draw_annotation()
            self.category_combobox.set(self.category_options[self.selected_annotation['category_id']])
            
    def draw_annotation(self):
        '''
        To display the current annotations
        '''
        for cids in self.canvas_points:
            self.canvas.delete(cids)
        self.canvas_points = []
        if "segmentation" in self.selected_annotation:
            polygons = self.selected_annotation["segmentation"]
            for polygon in polygons:
                if len(polygon) < 6:
                    continue
                coords = []
                for i in range(0, len(polygon), 2):
                    coords.extend([polygon[i], polygon[i+1]])
                polygon_id = self.canvas.create_polygon(coords, outline="red", width=2, fill="")
                self.canvas_points.append(polygon_id)

    def draw_all_annotation(self):
        '''
        To show all the annotations along with their classes
        '''
        for cids in self.canvas_points:
            self.canvas.delete(cids)
        self.canvas_points = []
        self.index = None
        self.selected_annotation = None
        for annotation in self.annotations:
            polygon = annotation["segmentation"][0]
            if len(polygon) < 6:
                continue
            category = self.category_options[annotation["category_id"]]
            cell_id = str(annotation["id"])
            x, y = int(annotation['bbox'][0]), int(annotation['bbox'][1])
            coords = []
            for i in range(0, len(polygon), 2):
                coords.extend([polygon[i], polygon[i+1]])
            polygon_id = self.canvas.create_polygon(coords, outline="red", width=2, fill="")
            self.canvas_points.append(polygon_id)
            text_id = self.canvas.create_text(x, y, text= category + ' (' +cell_id+ ')', fill='green')
            self.canvas_points.append(text_id)
        self.category_combobox.set(self.category_options[0])

    def clear_all_annotation(self):
        '''
        To clear all the annotations from display and also clear all the previous points saved
        '''
        for cids in self.canvas_points:
            self.canvas.delete(cids)
        self.canvas_points = []
        self.index = None
        self.selected_annotation = None
        self.current_polygon = []

    def rle_to_polygon(self, rle):
        """
        Convert COCO RLE format to a list of polygons.
        """
        mask = mask_utils.decode(rle)
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        polygons = []
        for contour in contours:
            segmentation = contour.flatten().tolist()
            # Check if the polygon is valid (has at least 6 points)
            if len(segmentation) >= 6:
                polygons.append(segmentation)
        return polygons
    
    def on_category_select(self, event):
        '''
        Function to change the class of the object from the dropdown box
        '''
        selected_category = self.category_combobox.get()
        ind = self.category_options.index(selected_category)
        if ind != 0:
            self.selected_annotation['category_id'] = ind
            self.annotations[self.index]['category_id'] = ind

    def on_canvas_click(self, event):
        '''
        function which takes care of drawing the segmentation mask over image canvas
        '''
        self.current_polygon.append(event.x)
        self.current_polygon.append(event.y)
        print ('current polygon points',self.current_polygon)
        if len(self.current_polygon) > 3:
            for cids in self.canvas_points:
                self.canvas.delete(cids)
                self.canvas_points = []
            coords = []
            for i in range(0, len(self.current_polygon), 2):
                coords.extend([self.current_polygon[i], self.current_polygon[i+1]])
            polygon_id = self.canvas.create_polygon(coords, outline="red", width=2, fill="")
            self.canvas_points.append(polygon_id)

        #self.current_polygon = self.canvas.create_line(self.current_points, fill="red", width=2)

    def on_del_polygon(self):
        '''
        to delete the current annotations of a cell
        '''
        index = self.index
        self.selected_annotation = self.annotations[index]
        self.selected_annotation['segmentation'] = [[]]
        self.annotations[index]['segmentation'] = [[]]
        print ('Deleted polygon for cell:', self.selected_annotation['id']  )
        self.current_polygon = []

    def on_save_polygon(self):
        '''
        to save a new annotation for a cell
        '''
        index = self.index
        self.selected_annotation = self.annotations[index]
        self.selected_annotation['segmentation'] = [self.current_polygon]
        self.annotations[index]['segmentation'] = [self.current_polygon]
        
        bbox, area = self.create_bbox_from_poly()

        self.selected_annotation['bbox'] = bbox
        self.annotations[index]['bbox'] = bbox
        self.selected_annotation['area'] = area
        self.annotations[index]['area'] = area

        print ('Created new polygon for cell:', self.selected_annotation['id']  )
        self.current_polygon = []

    def create_bbox_from_poly(self):
        '''
        after the new segmenation is drawn to find the bbox from it
        '''
        #create new bbox
        x_coords = self.current_polygon[::2]
        y_coords = self.current_polygon[1::2]
        min_x = min(x_coords)
        max_x = max(x_coords)
        min_y = min(y_coords)
        max_y = max(y_coords)
        bbox_width = max_x - min_x
        bbox_height = max_y - min_y
        bbox_topleft_x = min_x
        bbox_topleft_y = min_y
        bbox = [bbox_topleft_x, bbox_topleft_y, bbox_width, bbox_height]

        area = 0
        for i in range(len(x_coords)):
            j = (i + 1) % len(x_coords)
            area += x_coords[i] * y_coords[j]
            area -= y_coords[i] * x_coords[j]
        area = abs(area) / 2
        return bbox, area
        
    def on_add_new_cell(self):
        '''
        Function to add a new cell
        '''
        all_ids = [anno['id'] for anno in self.annotations]
        if len(all_ids) == 0:
            all_ids = [0]
        new_id = max(all_ids) + 1
        print ('created new cell with id:', new_id)
        
        seg = [[]]
        bbox = []
        area = 0
        if len(self.current_polygon) > 5:
            seg = [self.current_polygon]
            bbox,area = self.create_bbox_from_poly()
            self.current_polygon = []

        new_annotations = {
                        "id": new_id,
                        "image_id": 1,
                        "category_id": 1,
                        "bbox": bbox,
                        "segmentation": seg,
                        "area": area,
                        "iscrowd": 0
                        }

        self.annotations.append(new_annotations)
        self.selected_annotation = new_annotations
        self.populate_annotation_list()
    

    def on_save_results(self):
        '''
        To save the results of your annotations into json file
        '''
        for i, anno in enumerate(self.annotations):
            polygon = anno['segmentation'][0]
            poly_cords = np.asarray(polygon).reshape((-1, 2))
            mask = np.zeros((self.height, self.width), dtype=np.uint8)
            cv2.fillPoly(mask, [poly_cords.astype(int)], 1)

            # Convert the binary mask to RLE string format
            rle = mask_utils.encode(np.asfortranarray(mask))
            rle['counts'] = rle['counts'].decode('utf-8')
            
            self.annotations[i]['segmentation'] = rle

        self.annotations_all['categories'] = []
        for i in range(1,len(self.category_options)):
            self.annotations_all['categories'].append({
                                                        "id": i,
                                                        "name": self.category_options[i],
                                                        "supercategory": "cell"
                                                        })
        self.annotations_all['annotations'] = self.annotations



        with open( self.annotation_path, 'w') as fout:
                    json.dump(self.annotations_all, fout)

        for anno in self.annotations:
            anno["segmentation"] = self.rle_to_polygon(anno["segmentation"])
            self.populate_annotation_list()

    def on_close(self):
        # Destroy the window and its associated widgets
        self.master.destroy()

        # Call garbage collector to free up memory
        gc.collect()

categories = ['None', 'interphase', 'mitosis', 'post-mitosis']
root = tk.Tk()
app = AnnotationViewer(root, categories)
root.mainloop()
