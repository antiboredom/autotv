from glob import glob
import json
import os
from random import shuffle
from subprocess import call

base = '/Users/sam/Dropbox/Projects/autotv/copshow/'
images = glob(base + "images/*.jpg")
people = []
kens = []
imgindex = 0
nextindex = 1
interval = 300
lifespan = 400
fader = (lifespan - interval)/2.0


def setup():
    global images, people, kens
    frameRate(25)
    
    imageMode(CENTER)

    with open(base + "cops.json", 'r') as infile:
        data = json.load(infile)

    for p in data:
        pid = p['memberId']
        img = base + 'images/{}.jpg'.format(pid)
        if os.path.exists(img):
            p['image'] = img
            people.append(p)
    
    shuffle(people)
    people = people[0:10]
    
    try:
        rmtree('slideimages')
    except:
        pass
    try:
        os.makedirs('slideimages')
    except:
        pass
    
    for i, p in enumerate(people):
        tmpname = 'slideimages/{}.jpg'.format(str(i).zfill(5))
        #print(i, tmpname, p['image'])

        #call(['/usr/local/bin/convert', p['image'], '-resize', '1280x720', '-ordered-dither', 'h4x4o', tmpname])
        call(['/usr/local/bin/convert', p['image'], '-resize', '1280x720', tmpname])
        #print(tmpname)
        p['img'] = loadImage(tmpname)
        #p['img'] = loadImage(p['image'])


    size(1280, 720, P3D)  
    
    kens = [Ken(people[0])]
    
def draw():
    global kens, imgindex
    
    background(255)
    
    for k in kens:
        k.update()
        k.display()
    
    if frameCount % interval == 0:
        imgindex += 1
        if imgindex >= len(people):
            imgindex = 0  
        kens.append(Ken(people[imgindex]))
        kens[0].fadeout()
            
    kens = [k for k in kens if k.alive]
    
    person = kens[-1]
    txt = person.name + '\n' +  person.title + ', ICE\n' + person.location 
    noTint()
    fill(255, 0, 0)
    textSize(30)
    text(txt, 10, 60)
        
    
class Ken:
    def __init__(self, person):
        self.s = random(2.0, 3.0)
        self.s = 1.5
        self.d = random(-0.01, 0.01)
        self.d = 0.001
        self.x = random(width/2 - 100, width/2 + 100)
        self.y = random(height/2 - 100, height/2 + 100)
        self.person = person
        self.name = person.get('formattedName', '')
        self.location = person.get('location', '')
        self.title = person.get('title', '')
        self.img = person['img']
        self.frames = 0
        self.opacity = 0
        self.alive = True
        self.fadeto = (fader, 255)
        
    def fadein():
        pass
    
    def fadeout():
        self.fadeto = (fader, 0)
        
        
    def update(self):       
        self.s += self.d
        if self.s < 0:
            self.s = 0
            
        self.frames += 1
        
        # if self.frames > lifespan:
        #     self.alive = False
        
        # if self.frames < fader:
        #     self.opacity = map(self.frames, 0, fader, 0, 255)
        # elif self.frames >= lifespan - fader*2:
        #     self.opacity = map(self.frames, lifespan - fader*2, lifespan, 255, 0)
        # else:
        #     self.opacity = 255
        
    def display(self):
        tint(255, self.opacity)
        pushMatrix()
        translate(self.x, self.y)
        scale(self.s)
        image(self.img, 0, 0)
        popMatrix()
        
        
        
        
        