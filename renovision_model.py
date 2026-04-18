
"""
RenoVision — Custom Model Integration Helper
============================================
Drop this file + renovision_final_model.pth into your project.
Replace your YOLOv8x calls with predict_room() from this file.

Project: RenoVision: AI-Based Smart Interior Planner
Authors: Ahmad Raza | Tabeel John
University: Lahore Garrison University
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import json
import os


# ── Model Architecture (must match training) ──────────────────────────────────
class ConvBlock(nn.Module):
    def __init__(self, in_ch, out_ch, kernel=3, stride=1, padding=1):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, kernel, stride, padding, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )
    def forward(self, x): return self.block(x)

class ResidualBlock(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(channels, channels, 3, 1, 1, bias=False),
            nn.BatchNorm2d(channels), nn.ReLU(inplace=True),
            nn.Conv2d(channels, channels, 3, 1, 1, bias=False),
            nn.BatchNorm2d(channels),
        )
        self.relu = nn.ReLU(inplace=True)
    def forward(self, x): return self.relu(x + self.block(x))

class ChannelAttention(nn.Module):
    def __init__(self, channels, reduction=16):
        super().__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(
            nn.Linear(channels, channels // reduction, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(channels // reduction, channels, bias=False),
            nn.Sigmoid(),
        )
    def forward(self, x):
        b, c, _, _ = x.size()
        w = self.avg_pool(x).view(b, c)
        w = self.fc(w).view(b, c, 1, 1)
        return x * w.expand_as(x)

class RenoVisionCNN(nn.Module):
    def __init__(self, num_classes, dropout_rate=0.4):
        super().__init__()
        self.stage1 = nn.Sequential(
            ConvBlock(3,  32, kernel=7, stride=2, padding=3),
            ConvBlock(32, 64),
            nn.MaxPool2d(2, 2),
        )
        self.stage2 = nn.Sequential(
            ConvBlock(64, 128), ResidualBlock(128), ChannelAttention(128), nn.MaxPool2d(2, 2),
        )
        self.stage3 = nn.Sequential(
            ConvBlock(128, 256), ResidualBlock(256), ResidualBlock(256), ChannelAttention(256), nn.MaxPool2d(2, 2),
        )
        self.stage4 = nn.Sequential(
            ConvBlock(256, 512), ResidualBlock(512), ResidualBlock(512), ChannelAttention(512), nn.MaxPool2d(2, 2),
        )
        self.stage5 = nn.Sequential(
            ConvBlock(512, 512), ResidualBlock(512), ChannelAttention(512),
        )
        self.gap = nn.AdaptiveAvgPool2d(1)
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(512, 512), nn.BatchNorm1d(512), nn.ReLU(inplace=True), nn.Dropout(dropout_rate),
            nn.Linear(512, 256), nn.BatchNorm1d(256), nn.ReLU(inplace=True), nn.Dropout(dropout_rate / 2),
            nn.Linear(256, num_classes),
        )
    def forward(self, x):
        x = self.stage1(x); x = self.stage2(x); x = self.stage3(x)
        x = self.stage4(x); x = self.stage5(x); x = self.gap(x)
        return self.classifier(x)


# ── RenoVision Model Loader ───────────────────────────────────────────────────
class RenoVisionModel:
    """
    Drop-in replacement for your YOLOv8x room detection.
    
    Usage:
        from renovision_model import RenoVisionModel
        model = RenoVisionModel("renovision_final_model.pth")
        result = model.predict("path/to/room.jpg")
        print(result["room_type"])        # "bedroom"
        print(result["confidence"])       # 0.87
        print(result["top5"])             # [("bedroom", 0.87), ...]
    """
    
    def __init__(self, model_path: str, device: str = None):
        self.device = torch.device(
            device if device else 
            ("cuda" if torch.cuda.is_available() else "cpu")
        )
        print(f"[RenoVision] Loading model on {self.device}...")
        
        checkpoint = torch.load(model_path, map_location=self.device)
        
        self.num_classes  = checkpoint["num_classes"]
        self.classes      = checkpoint["classes"]
        self.idx_to_class = checkpoint["idx_to_class"]
        self.class_to_idx = checkpoint["class_to_idx"]
        self.img_size     = checkpoint.get("img_size", 224)
        
        self.model = RenoVisionCNN(
            num_classes=self.num_classes, dropout_rate=0.0  # No dropout at inference
        ).to(self.device)
        self.model.load_state_dict(checkpoint["model_state"])
        self.model.eval()
        
        self.transform = transforms.Compose([
            transforms.Resize((self.img_size, self.img_size)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
        ])
        
        val_acc = checkpoint.get("best_val_acc", "N/A")
        test_acc = checkpoint.get("test_acc", "N/A")
        print(f"[RenoVision] Model loaded! Classes: {self.num_classes}")
        print(f"[RenoVision] Val Acc: {val_acc:.2f}% | Test Acc: {test_acc:.2f}%")
    
    def predict(self, image_path_or_pil, top_k: int = 5) -> dict:
        """
        Predict room type from image.
        Args:
            image_path_or_pil: str path OR PIL.Image object
            top_k: number of top predictions to return
        Returns:
            dict with keys: room_type, confidence, top5, class_idx
        """
        if isinstance(image_path_or_pil, str):
            image = Image.open(image_path_or_pil).convert("RGB")
        else:
            image = image_path_or_pil.convert("RGB")
        
        tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            logits = self.model(tensor)
            probs  = F.softmax(logits, dim=1).squeeze(0)
        
        probs_np    = probs.cpu().numpy()
        top_indices = probs_np.argsort()[::-1][:top_k]
        
        top_predictions = [
            {
                "room_type"  : self.idx_to_class[str(i)],
                "confidence" : float(probs_np[i]),
                "percentage" : f"{float(probs_np[i])*100:.1f}%"
            }
            for i in top_indices
        ]
        
        best = top_predictions[0]
        return {
            "room_type"  : best["room_type"],
            "confidence" : best["confidence"],
            "percentage" : best["percentage"],
            "class_idx"  : int(top_indices[0]),
            "top_k"      : top_predictions,
            # Legacy format (for XAI module)
            "xai_data": {
                "detected_room" : best["room_type"],
                "confidence"    : best["confidence"],
                "alternatives"  : top_predictions[1:4],
            }
        }
    
    def predict_batch(self, image_paths: list) -> list:
        """Predict multiple images at once."""
        return [self.predict(p) for p in image_paths]


# ── Quick Test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Example usage — replace with your image path
    model = RenoVisionModel("renovision_final_model.pth")
    
    # Test with a random PIL image
    from PIL import Image
    import numpy as np
    dummy = Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8))
    result = model.predict(dummy)
    
    print("
=== Prediction Result ===")
    print(f"Room Type  : {result["room_type"]}")
    print(f"Confidence : {result["percentage"]}")
    print(f"Top 5      :")
    for p in result["top_k"]:
        print(f"  {p["room_type"]:<25} {p["percentage"]}")
