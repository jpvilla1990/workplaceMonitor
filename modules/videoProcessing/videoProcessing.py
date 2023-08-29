import os
import numpy as np
import cv2
import torch
from PIL import Image
import torchvision
from yolov6.data.data_augment import letterbox
from yolov6.core.inferer import Inferer
from modules.interfaceDatabase.interfaceDatabase import InterfaceDatabase
from modules.baseModule.baseModule import BaseModule

class VideoProcessing(BaseModule):
    """
    Class to handle the video processing using AI algorithms
    """
    def __init__(self):
        super().__init__()
        self.__interfaceDatabase : InterfaceDatabase = InterfaceDatabase()

    def __imageToTensor(self, imageNumpy : np.ndarray, imgSize : list, stride : int, half : bool, device : str) -> tuple:
        """
        Tool to conver image np to tensor
        """
        image : np.ndarray = letterbox(imageNumpy, imgSize, stride=stride)[0]

        resize : torchvision.transforms.Resize = torchvision.transforms.Resize(imgSize)

        image = image.transpose((2, 0, 1))  # HWC to CHW
        imageTorch : torch.Tensor = torch.from_numpy(np.ascontiguousarray(image))
        imageTorch = resize.forward(imageTorch)
        imageTorch = imageTorch.half() if half else imageTorch.float()  # uint8 to fp16/32
        imageTorch /= 255  # 0 - 255 to 0.0 - 1.0

        imageTorch = imageTorch.to(device)
        if len(imageTorch.shape) == 3:
            imageTorch = imageTorch[None]

        return imageTorch, imageNumpy

    def processImageToTensorPersonDetection(self, path : str, imgSize : int, stride : int, half : bool, device : str) -> tuple:
        """
        Method to convert image to tensor
        """
        imageNumpy : np.ndarray = np.asarray(
            Image.open(
                open(path, "rb")
            )
        )

        return self.__imageToTensor(
            imageNumpy=imageNumpy,
            imgSize=imgSize,
            stride=stride,
            half=half,
            device=device,
        )

    def annotateImage(self, imagePath : str, coordinatesDict : dict) -> str:
        """
        Method to annotate image
        """
        folderImages : str = os.path.dirname(imagePath)
        imageName : str = os.path.basename(imagePath)
        annotatedImagePath : str = os.path.join(
            folderImages,
            imageName.split(".png")[0] + "Annotated.png",
        )
        imgNumpy : np.ndarray = np.asarray(
            Image.open(imagePath)
        )
        color : int = 0
        for objectKey in list(coordinatesDict.keys()):
            coordinates : list = coordinatesDict[objectKey]["coordinates"]
            label : str

            if coordinatesDict[objectKey]["annotation"]:
                label = "not working"
            else:
                label = "working"
            Inferer.plot_box_and_label(imgNumpy, max(round(sum(imgNumpy.shape) / 2 * 0.003), 2), coordinates, label, color=Inferer.generate_colors(color, True))
            color += 1

        Image.fromarray(imgNumpy).save(annotatedImagePath)

        return annotatedImagePath
    
    def createVideoFromImages(self, images : dict, index : int) -> str:
        """
        Method to create video from images
        """
        fps : int = self.getConfig()["interfaceCamera"]["framesPerSecond"]

        imagePil : Image = Image.open(images[0]["framePath"])
        width, height = imagePil.size

        videosFolder : str = self.getPaths()["folders"]["videosPersonsIdle"]
        videoFile : str = os.path.join(videosFolder, str(index) + ".mp4")

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        videoWriter = cv2.VideoWriter(videoFile, fourcc, fps, (width, height))
        for imageIndex in list(images.keys()):
            imgNumpy : np.ndarray = np.asarray(
                Image.open(images[imageIndex]["framePath"])
            )

            coordinates : list = [images[imageIndex]["x0"], images[imageIndex]["y0"], images[imageIndex]["x1"], images[imageIndex]["y1"]]

            Inferer.plot_box_and_label(imgNumpy, max(round(sum(imgNumpy.shape) / 2 * 0.003), 2), coordinates, "", color=Inferer.generate_colors(1, True))

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')

            cvImage = cv2.cvtColor(imgNumpy, cv2.COLOR_RGB2BGR)
            videoWriter.write(cvImage)

        videoWriter.release()

        return videoFile