import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from PIL import Image
import gc  # For explicit garbage collection

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def torch_backends():
    torch.set_default_tensor_type('torch.cuda.FloatTensor')
    torch.backends.mkl.enabled = True
    torch.backends.cudnn.enabled = True
    torch.backends.cudnn.benchmark = True
    torch.backends.cuda.cufft_plan_cache_enabled = True
    torch.backends.cuda.matmul.allow_bf16_reduced_precision_reduction = True
    torch.set_num_threads(28)
    torch.backends.cudnn.deterministic = False

torch_backends()

# Lighter model architecture
model = nn.Sequential(
    nn.Conv2d(3, 32, kernel_size=3, padding=1),
    nn.ReLU(),
    nn.Conv2d(32, 3, kernel_size=3, padding=1),
    nn.ReLU(),
    nn.Upsample(size=(1080, 1920), mode='bilinear', align_corners=False)
).to(device)

loss_fn = nn.MSELoss()
optimizer = optim.AdamW(model.parameters(), lr=0.00001, weight_decay=5e-7)
to_tensor = transforms.ToTensor()

num_epochs = 1000000
foto_i = 0
f = 0
cycles = 1500

for epoch in range(num_epochs):
    if epoch == 0 or epoch % 8000 == 0:
        # Load images only when needed
        low_res_img = Image.open(f"C:/Users/user/Desktop/GODD/obs{foto_i + 1}.jpeg").convert("RGB")
        high_res_img = Image.open(f"C:/screenshots/obs{foto_i + 1}.jpeg").convert("RGB")
        
        low_res_tensor = to_tensor(low_res_img).unsqueeze(0).to(device)
        high_res_tensor = to_tensor(high_res_img).unsqueeze(0).to(device)
        
        # Clear PIL images from memory
        del low_res_img, high_res_img
        gc.collect()
        
        foto_i += 1
        if foto_i >= cycles:
            foto_i = 0
        print(f"Processing image {foto_i}")
    
    optimizer.zero_grad()
    with torch.amp.autocast(device_type="cuda", dtype=torch.float16):
        output = model(low_res_tensor)
        loss = loss_fn(output, high_res_tensor)
    
    loss.backward()
    optimizer.step()
    
    if epoch % 8000 == 0:
        to_pil = transforms.ToPILImage()
        output_img = to_pil(output.squeeze(0).detach().cpu().clamp(0, 1))
        output_img.save(f"C:/photoes/output{f + 1}.jpeg")
        f += 1
        del output_img
        gc.collect()
        
    print(f"Эпоха {epoch+1}/{num_epochs}, Потери: {loss.item()}")
    
    if epoch % 1000 == 0:
        torch.save(model.state_dict(), "super_resolution3.pth")

    # Clear CUDA cache periodically
    if epoch % 100 == 0:
        torch.cuda.empty_cache()