from PIL import Image
for i in range(1000):    
    v = Image.open(f"C:/screenshots/obs{i + 1000}.jpeg")
    t = v.resize((640,360))
    t.save(f"C:/Users/SoaPisGirseb/Desktop/GODD/obs{i + 1000}.jpeg")
    print(i)