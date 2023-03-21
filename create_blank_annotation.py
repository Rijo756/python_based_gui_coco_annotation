import os,json
'''
This script will create a blank json file without any annotations. For a different dataset you can add the categories as you like in this file as in the gui file
'''
image_path = '/home/students/roy/Cell_Annotations/data'
image_name = 'P0001_t001'

imagewise_clf_result = {'info': { 
                                                "year": 2023,
                                                "version": "1.0",
                                                "description": "Creating a new dataset with similar format for COCO dataset.",
                                                "contributor": "Rijo"
                                                },
                                      'licences': [{
                                                        "id": 1,
                                                        "name": "Selfown License",
                                                        "url": "add/yoir/url"
                                                    }],
                                      'categories':[{
                                                        "id": 1,
                                                        "name": "interphase",
                                                        "supercategory": "cell"
                                                        },
                                                        {
                                                        "id": 2,
                                                        "name": "mitosis",
                                                        "supercategory": "cell"
                                                        },
                                                        {
                                                        "id": 3,
                                                        "name": "post-mitosis",
                                                        "supercategory": "cell"
                                                        },
                                                        {
                                                        "id": 4,
                                                        "name": "dead-cell",
                                                        "supercategory": "cell"
                                                    }],
                                      'images': { 
                                                    "id": 1,
                                                    "width": 800,
                                                    "height": 800,
                                                    "file_name": image_name
                                        },
                                      'annotations':[]
                                      }

with open( os.path.join(image_path, image_name + '.json' ), 'w') as fout:
                    json.dump(imagewise_clf_result, fout)
                    