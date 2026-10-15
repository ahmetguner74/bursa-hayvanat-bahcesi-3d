from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib,cv2
H=Path(__file__).resolve().parent
im=Image.open(H/'source-texture.png').convert('RGB'); n=im.width; mask=Image.new('L',im.size)
d=ImageDraw.Draw(mask)
for tr in json.loads((H/'uv-height-mask.json').read_text()):
 z=sum(tr['height'])/3
 # The lower shank is plain in Bursa's official Baringo reference. Hoof remains untouched.
 w=min(1,max(0,(z-.18)/.10))*min(1,max(0,(1.40-z)/.18))
 if w:d.polygon([(u*n,(1-v)*n)for u,v in tr['uv']],fill=int(w*255))
mask=mask.filter(ImageFilter.GaussianBlur(.9));arr=np.array(im).astype(float);lum=np.mean(arr,axis=2);target=np.array([210,190,150])[None,None,:]*(.87+.13*lum[:,:,None]/255)
a=np.array(mask)[:,:,None]/255; out=np.clip(arr*(1-a)+target*a,0,255).astype('uint8')
# Add a technical eight-pixel colour margin around UV islands. This prevents
# transparent atlas-black pixels bleeding into the nape after subdivision/mips.
valid=np.max(out,axis=2)>24
dist,labels=cv2.distanceTransformWithLabels((~valid).astype('uint8'),cv2.DIST_L2,5,labelType=cv2.DIST_LABEL_PIXEL)
colors=out[valid]; padding=(~valid)&(dist<=8);out[padding]=colors[labels[padding]-1]
Image.fromarray(out).save(H/'baringo-basecolor.png')
mask.save(H/'baringo-lower-leg-mask.png')
print('mask',float(a.mean()),'heightRange',min(min(t['height']) for t in json.loads((H/'uv-height-mask.json').read_text())),max(max(t['height'])for t in json.loads((H/'uv-height-mask.json').read_text())))
