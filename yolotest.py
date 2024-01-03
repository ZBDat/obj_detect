import sys
import cv2
sys.path.append('./yolov7')
from yolov7.hubconf import custom


class Detector:
    
    def __init__(self, model_path):
        self.model = custom(path_or_model=model_path)
        
    def detect(self, image, draw=False) -> list:
        """main method to give the position of objects
        in a given picture.

        Args:
            image: path to the image or np array

        Returns:
            detect_list or None: all objects positions, given in the form of four 
            points of the bbox. If nothing detected, return None
        """        
        image = cv2.imread(image)
        result = self.model(image)
        # Error for failed detection
        if len(result.xyxy[0].cpu()) == 0:
            print("No bottle detected!")
            return None
        
        print(result.pandas().xyxy[0])
        result_list = result.xyxy[0].cpu()
        
        # return the bounding boxes of the objects
        detect_list = []
        for i in range(len(result.xyxy[0])):
            box = result.xyxy[0][i]
            print(box)
            bbox = box.cpu().tolist()
            xmin, ymin, xmax, ymax = bbox[0], bbox[1], bbox[2], bbox[3]
            detect_list.append([xmin, ymin, xmax, ymax])
        
        if draw:  
            im_copy = image.copy()
            for bbox in detect_list:
                xmin, ymin, xmax, ymax = bbox
                xmin = int(xmin)
                ymin = int(ymin)
                xmax = int(xmax)
                ymax = int(ymax)
                cv2.rectangle(im_copy, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            
            cv2.imwrite('detect.png', im_copy)
        
        return detect_list
    

if __name__=="__main__":
    detector = Detector(model_path='best.pt')
    detect_list = detector.detect('./test_images/sample.png', draw=True)
