from PIL import Image

# 打开图片
img = Image.open('favicon.png')

# 保存为 ICO 格式
img.save('favicon (6).ico', format='ICO') 