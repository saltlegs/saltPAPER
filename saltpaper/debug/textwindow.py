import pygame
from pathlib import Path

cwd = Path.cwd()
default_font_path = cwd / "engine" / "assets" / "fonts" / "LibertinusMono-Regular.ttf"
blank_char = " "

class TextWindow():
    def __init__(self,font=None,width=60,height=30,fontsize=20,caption="text window"):
        pygame.init()

        pygame.display.set_caption(caption)

        if font is None:
            try:
                font = pygame.font.Font(default_font_path,fontsize)
            except:
                font = pygame.font.Font()

        self.font = font

        self.textwidth = width
        self.textheight = height

        fontbounds =    font.size("g")
        screenwidth =   fontbounds[0] * width
        screenheight =  fontbounds[1] * height

        self.charwidth =    fontbounds[0]
        self.charheight =   fontbounds[1]

        self.blank()

        self.screen = pygame.display.set_mode((screenwidth,screenheight))
        self.clock = pygame.time.Clock()

        self.running = True
        self.dirty = True

    def blank(self):
        self.textarray = {}
        for w in range(self.textwidth):
            if self.textarray.get(w) is None:
                self.textarray[w] = {}
            for h in range(self.textheight):
                self.textarray[w][h] = blank_char

    def write(self, x, y, text):
        text = str(text)
        writelength = len(text)

        for i in range(writelength):
            x1 = (x + i) % self.textwidth
            self.textarray[x1][y] = text[i]
        
        self.dirty = True

    def render_textarray(self):
        
        for w in range(self.textwidth):
            for h in range(self.textheight):
                char = self.textarray[w][h]
                if char == " ":
                    continue
                char_surf = self.font.render(char, True, (255,255,255))
                self.screen.blit(char_surf,(w*self.charwidth,h*self.charheight))

    def tick(self):

        self.events = pygame.event.get()
        for event in self.events:
            if event.type == pygame.QUIT:
                self.running = False

        if not self.dirty:
            return
        
        self.screen.fill((0,0,0))

        self.render_textarray()
        pygame.display.flip()
        self.dirty = False

def main_ant():
    tw = TextWindow(caption="ant")
    w = tw.textwidth
    h = tw.textheight

    antx = w//2
    anty = h//2

    ant_dir = 0

    def dir_to_offsets(v):
        neg = bool(v & 2)
        invert = 1 - 2 * int(neg)
        
        wO = (bool(v & 1)) * invert
        hO = (not bool(v & 1)) * invert
        return wO, hO

    step = 0
    while tw.running:
        tw.tick()
        here = tw.textarray[antx][anty]
        if here == "8":
            ant_dir = (ant_dir - 1) % 4
            tw.write(" ", antx, anty)
        else:
            ant_dir = (ant_dir + 1) % 4
            tw.write("8", antx, anty)

        movex, movey = dir_to_offsets(ant_dir)
        antx = (antx + movex) % tw.textwidth
        anty = (anty + movey) % tw.textheight
        step += 1
        tw.clock.tick(240)

def main_text():
    tw = TextWindow(width=25,height=17,caption="text display")

    while tw.running:
        tw.blank()
        tw.write("you know what i HATE?",2,2)
        tw.write("that's",5,5)
        tw.write("BEPIS",5,6)
        tw.write("the taste...",3,8)
        tw.write("the smell...",4,9)
        tw.write("the texture...",5,10)
        tw.write("hey.....",3,12)
        tw.write("your drooling.....",2,14)


        tw.tick()


if __name__ == "__main__":
    main_ant()