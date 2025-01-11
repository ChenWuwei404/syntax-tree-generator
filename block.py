from src import Stack
import numpy
import svgwrite
from typing import Union

import pygame

class Block:
    subs: list["Block"]
    def __init__(self, expression: str, father: Union["Block", None] = None) -> None:
        self.width = 0
        self.center_pos = 0
        self.position = numpy.array([0, 0])
        self.end_level = -1
        self.father = father

        expression = expression.replace("\\phi", "φ")
        expression = expression.replace("\\empty", "∅")
        expression = expression.replace("\\theta", "θ")

        self.title = ""
        self.subs = []
        self.sub_shape = 0  # 0 - tree, 1 - trangle
        if expression[0] == "\"" and expression[-1] == "\"":
            self.title = expression[1:-1]
            self.subs = []
        elif expression.find("[") == -1 and expression.find("(") == -1:
            self.title = expression
            self.subs = []
        else:
            i = 0
            while expression[i] not in {"[", "("}:
                self.title += expression[i]
                i += 1
            
            sub_exp = ""
            stack = Stack()
            stack.push(expression[i])
            i += 1
            while stack.size() > 0 and i < len(expression):

                if expression[i] == "\"":
                    i += 1
                    while expression[i] != "\"":
                        sub_exp += expression[i]
                        i += 1
                    i += 1

                if expression[i] in {"[", "("}:
                    stack.push(expression[i])
                    sub_exp += expression[i]
                    while stack.size() > 1:
                        i += 1
                        sub_exp += expression[i]
                        if expression[i] in {"[", "("}:
                            stack.push(expression[i])
                        elif expression[i] in {"]", ")"}:
                            if stack.peek() == {"]": "[", ")": "("}[expression[i]]:
                                stack.pop()
                            else:
                                raise ValueError("Mismatched parentheses")
                        
                elif expression[i] in {"]", ")"}:
                    if stack.peek() == {"]": "[", ")": "("}[expression[i]]:
                        stack.pop()
                        if stack.size() == 0:
                            break
                    else:
                        raise ValueError("Mismatched parentheses")
                
                if expression[i] == " ":
                    sub_block = Block(sub_exp, self)
                    self.subs.append(sub_block)
                    sub_exp = ""
                    i += 1
                    continue

                sub_exp += expression[i]
                i += 1

            if stack.size() > 0:
                raise ValueError("Mismatched parentheses")

            if sub_exp:
                sub_block = Block(sub_exp, self)
                self.subs.append(sub_block)

    def analyze(self) -> dict:
        if not self.subs:
            self.width = 1
            self.center_pos = 0
        else:
            self.width = 0
            pos_min = 1e9
            pos_max = -1e9
            for sub in self.subs:
                sub_analyze = sub.analyze()
                pos_min = min(pos_min, sub_analyze["center_pos"] + self.width)
                pos_max = max(pos_max, sub_analyze["center_pos"] + self.width)
                self.width += sub_analyze["width"] + 1
            self.width -= 1
            self.center_pos = (pos_min + pos_max) / 2
        return {"width": self.width, "center_pos": self.center_pos}
    
    def render_analyze(self, pos: int, level: int) -> None:
        self.position = numpy.array([pos, level])
        if self.subs:
            width_sum = 0
            for sub in self.subs:
                sub.render_analyze(width_sum + pos, level + 1)
                width_sum += sub.width + 1

    def set_zoom(self, zoom: numpy.ndarray) -> None:
        self.zoom = zoom
        if self.subs:
            for sub in self.subs:
                sub.set_zoom(zoom)

    def set_end_leveled(self, end_level: int) -> None:
        if self.subs:
            for sub in self.subs:
                sub.set_end_leveled(end_level)
        self.end_level = end_level

    @property
    def level_count(self) -> int:
        if not self.subs:
            return 1
        else:
            return 1 + max(sub.level_count for sub in self.subs)

    @property
    def render_position(self) -> numpy.ndarray:
        if self.end_level > self.level_count and not self.subs and (self.father != None and self.father.subs.__len__() == 1):
            position = numpy.array((self.position[0], self.end_level - 1))
        else:
            position = self.position
        render_position = position * self.zoom
        render_position[0] += self.center_pos * self.zoom[0] + 50
        render_position[1] += 100

        return render_position

    def pg_render(self, surface: pygame.Surface, font: pygame.Font) -> None:
        if self.subs:
            for sub in self.subs:
                pygame.draw.aaline(surface, (255, )*3, self.render_position, sub.render_position)
                sub.pg_render(surface, font)

        text_surface = font.render(self.title, True, (255, )*3)
        rect = text_surface.get_rect()
        rect.center = self.render_position
        bgrect = rect.inflate(10, 10)
        bgrect.y -= 4
        pygame.draw.rect(surface, (0, )*3, bgrect, 0, 8)
        surface.blit(text_surface, rect)

    def svg_render(self, dwg: svgwrite.Drawing, font: pygame.font.Font) -> None:
        self_pos = (int(self.render_position[0]), int(self.render_position[1]))
        if self.subs:
            for sub in self.subs:
                sub_pos = (int(sub.render_position[0]), int(sub.render_position[1]))
                dwg.add(dwg.line(start=self_pos, end=sub_pos, stroke="black"))
                sub.svg_render(dwg, font)

        text_surface = font.render(self.title, True, (255, )*3)
        rect = text_surface.get_rect()
        rect.center = self.render_position
        bgrect = rect.inflate(10, 10)
        bgrect.y -= 4

        bg_rect = dwg.rect(insert=bgrect.topleft, size=bgrect.size, fill="white")
        dwg.add(bg_rect)
        if self.title != "\\0":
            text = dwg.text(self.title, insert=(self_pos[0], self_pos[1] + 6), text_anchor="middle", fill="black", font_family=font.name, font_size=font.get_height())
            dwg.add(text)

    def __str__(self) -> str:
        subs_str = ' '.join(str(sub) for sub in self.subs)
        return f"{self.title}[{subs_str}]" if subs_str else self.title
    
def generate_file(code: str, name: str, end_leveled: bool = True) -> tuple[int, int]:
    if not code:
        raise ValueError("Empty code")
    block = Block(code, None)
    block.analyze()
    block.render_analyze(0, 0)
    zoom = numpy.array([50, 70])
    block.set_zoom(zoom)

    if end_leveled:
        block.set_end_leveled(block.level_count)

    size = (int(block.width * zoom[0] + 100), int(block.level_count * zoom[1] + 100))
    pygame.init()
    font = pygame.font.Font(r'./lmromanslant.otf', 16)
    dwg = svgwrite.Drawing(name, size=size)
    dwg.add(dwg.rect(insert=(0, 0), size=size, fill="white"))
    block.svg_render(dwg, font)
    dwg.save()
    return size

if __name__ == "__main__":
    # block = Block("S[NP[\"the boy\"] IP[I'[\\empty] VP[V[hit] NP[D[the] N[ball]]]]]")
    # print(block)
    # print(block.analyze())
    # block.render_analyze(0, 0)
    # print(block.subs[1].position)

    # zoom = numpy.array([50, 70])

    # block.set_zoom(zoom)

    # size = (int(block.width * zoom[0] + 100), int(block.level_count * zoom[1] + 100))

    # pygame.init()
    # screen = pygame.display.set_mode(size)
    # font = pygame.font.Font(r'./HanSans.ttf', 20)



    # dwg = svgwrite.Drawing('test.svg', size=size)
    # dwg.add(dwg.rect(insert=(0, 0), size=size, fill="white"))
    # block.svg_render(dwg, font)
    # dwg.save()
    # block.pg_render(screen, font)
    # pygame.display.flip()
    # while True:
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             pygame.quit()
    #             exit()

    generate_file("S[NP[D[the] N[boy]] IP[I'[\\empty] VP[V[hit] NP[D[the] N[ball]]]]]", "test.svg")