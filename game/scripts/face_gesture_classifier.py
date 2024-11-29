from emotrics.core.frame_analysis import FrameSymmetry
from game.scripts.configu_ration import MODEL_PATH
import os
import torch
import torch.nn as nn  # Añadimos esta importación
import torch.nn.functional as F
from torchvision import transforms
from facenet_pytorch import MTCNN
from PIL import Image

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MODEL_PATH = os.path.join(PROJECT_ROOT, 'emotrics', 'assets', 'models', 'best_model.pth')

#%% 
# Check if CUDA (GPU support) is available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Cargar el modelo de clasificación de gestos
num_classes = 4
class_names = {
    0: 'NEGATIVE',
    1: 'NSM_KISS',
    2: 'NSM_OPEN',
    3: 'NSM_SPREAD'
}

class CNN(nn.Module):
    def __init__(self):
        
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv4 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.conv5 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(32)
        self.bn5 = nn.BatchNorm2d(256)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(256 * 4 * 4, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        x = self.pool(F.relu(self.conv3(x)))
        x = self.pool(F.relu(self.conv4(x)))
        x = self.pool(F.relu(self.bn5(self.conv5(x))))
        x = x.view(-1, 256 * 4 * 4)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.softmax(self.fc3(x), dim=1)
        return x


class FaceGestureClassifier:
    def __init__(self):
        self.mtcnn_module = MTCNN(keep_all=False, device=device)
        self.model = CNN()
        self.load_model()
        self.transform = self.get_transform()

    def load_model(self):
        model_save_path = 'game/assets/best_model.pth'
        state_dict = torch.load(model_save_path, map_location=device)
        self.model.load_state_dict(state_dict)
        self.model.eval()

    @staticmethod
    def get_transform():
        return transforms.Compose([
            transforms.Resize((128, 128)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def detect_and_crop_face(self, image):
        with torch.no_grad():
            boxes, _ = self.mtcnn_module.detect(image)
        if boxes is not None and len(boxes) > 0:
            face_box = boxes[0].astype(int)
            cropped_face = image.crop(face_box)
            return cropped_face
        else:
            return None

    def classify_face(self, img):
        pil_image = Image.fromarray(img)
        cropped_face = self.detect_and_crop_face(pil_image)

        if cropped_face is not None:
            input_tensor = self.transform(cropped_face).unsqueeze(0)
            with torch.no_grad():
                output = self.model(input_tensor)
            prob, predicted = torch.max(output, 1)
            predicted_class = predicted.item()
            class_name = class_names[predicted_class]
            probability = prob.item()
            return class_name
        else:
            return None