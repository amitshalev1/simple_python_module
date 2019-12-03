import cv2
import numpy as np

def draw_annoations(img,annots):
    """
    draw segmentations on image
    img : np.array
    annots: maagad format
    """
    font = cv2.FONT_HERSHEY_PLAIN
    for annot in annots:
        if annot['deleted']!=1:
            if annot['annotation_type']=='polygon':
                img = draw_polygon(img,annot['annotations'])

            elif annot['annotation_type']=='oval':
                print(annot['annotations'])
                box=[(annot['annotations']['x'],annot['annotations']['y']),
                                 (annot['annotations']['x']+annot['annotations']['width'],annot['annotations']['y']),
                                 (annot['annotations']['x'],annot['annotations']['y']+annot['annotations']['height']),
                                 (annot['annotations']['x']+annot['annotations']['width'],annot['annotations']['y']+annot['annotations']['height'])]
                box=[int(x) for x in box]
                cv2.ellipse(img,box, (0,0,0),18)

    fig, ax = plt.subplots(figsize=(10, 22))
    ax.imshow(img, interpolation='nearest')

def get_contour(polygon,x='x',y='y'):
    '''
    polygon= [{'x':23,'y':531}]
    outputs = [[x,y],[x,y]]
    '''
    return np.array([(point[x],point[y]) for point in polygon],dtype=np.int32)

def draw_polygon(img,ploygon,
                 x='x',
                 y='y',
                 contourIdx=0,
                 color = (0,0,0),
                 thickness=18):
    '''
    adds a polygon to the img and returns the new img
    
    '''
    new_img = img.copy() # otherwise changes the original
    return cv2.drawContours(new_img,[get_contour(ploygon)],contourIdx,color,thickness)


def crop(im,cont):
    """
    crop image by contour

    crops the cont object out of the image
    
    ----------
    values
    ----------------
    img : np.array image
    contour : [[x,y],[x,y]] closed contour

    Returns
    -------
    img : np.array image
    ----------

    Examples
    --------
    # create image
    img = (255*np.random.random((100,100))).astype('uint8') 
    img[11:40,20:40]= 0

    # create a square to crop (this is a test, we crop the only area sure to equel zero)
    cont =[[21,12],[39,12],[39,39],[21,12]]


    assert (crop(img,np.array(cont))==0).all()
    """

    img = im.copy()

    mask = np.zeros(img.shape[:2], dtype=np.uint8)

    points=cont.copy()
    mask = cv2.fillPoly(mask, [points], (255))
    
    res = cv2.bitwise_and(img,img,mask = mask)

    rect = cv2.boundingRect(points) # returns (x,y,w,h) of the rect
    cropped = res[rect[1]: rect[1] + rect[3], rect[0]: rect[0] + rect[2]]
    return cropped




def get_im_cont(num):
    idx=data['annotations'][num]['image_id']
    url=data['images'][idx]['url']
    rr='../'+url.split('/T/')[1]
    if not os.path.isfile(rr):
        rr=rr.replace('masks1','masks2')

    im=cv2.imread(rr)
    # plt.imshow(im)
    return im,np.array(data['annotations'][num]['segmentation']).T,data['images'][idx]['path']

    
def crop2(im,cont,fname,num,dire='daniel_images2018_05_30/'):
    img = im.copy()
    height = img.shape[0]
    width = img.shape[1]

    mask = np.zeros((height, width), dtype=np.uint8)
    #points = np.array([[[10,150],[150,100],[300,150],[350,100],[310,20],[35,10]]])
    points=cont.copy()
    cv2.fillPoly(mask, [points], (255))

    res = cv2.bitwise_and(img,img,mask = mask)

    rect = cv2.boundingRect(points) # returns (x,y,w,h) of the rect
    cropped = res[rect[1]: rect[1] + rect[3], rect[0]: rect[0] + rect[2]]

    fname=dire+fname[:-4]+str(num)+'.JPG'
    cv2.imwrite(fname,cropped)

def worker(crp):
    #print(crp)
    a,b,c=get_im_cont(i)
    crop2(a,b,c,i)  
    #print ('Worker')
    

def crop_generator(values,
                   target_size = (224,224),
                   thresh = 5):           
    """
    creates a generator with cropped image from a list where each item is [path,annotation]
    
    data[['image_uri','annotations']].sample(5).values
    ----------
    values
    ----------------
    target_size : (int,int)
        size of target image (height,width).
    thresh : int
        minimal size of cropped object height or width.

    Returns
    -------
    (img generator) where each image is in target_size and minimal size of the edge is thresh
    References
    ----------

    Examples
    --------
    # with annoations downloaded from maagad:
    filtered_cropped,filtered_paths = crop_generator(df[['image_uri','annotations']].values)
    """
    cropped = ((path,crop(cv2.imread(path),get_contour(annotation))) for path,annotation in values)
    filtered_cropped = filter(lambda x: min(x[1].shape[:2])>thresh,cropped)

    
    filtered_paths = list(map(lambda x: x[0],filtered_cropped))  
    filtered_cropped = (cv2.resize(crop(cv2.imread(path),get_contour(annotation)),target_size) for path,annotation in values if path in filtered_paths)
    return filtered_cropped,filtered_paths

# if __name__ == '__main__':

#     jobs = []
#     for i in tqdm(range(len(data['annotations']))):
#         p = multiprocessing.Process(target=worker, args=[i])
#         jobs.append(p)
#         p.start()              
# #         jobs[-1].terminate()

#     for j in jobs:
#         j.join()
        #print (j.name, j.exitcode)
            