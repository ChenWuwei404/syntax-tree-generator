from src import Stack, is_cjk
import numpy
import svgwrite
from typing import Union

import pygame

transformation_sources = {}
transformation_destinations = []

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
        expression = expression.replace("\\epsilon", "ε")
        expression = expression.replace("\\alpha", "α")
        expression = expression.replace("\\beta", "β")
        expression = expression.replace("\\gamma", "γ")
        expression = expression.replace("\\delta", "δ")
        expression = expression.replace("\\lambda", "λ")
        expression = expression.replace("\\mu", "μ")
        expression = expression.replace("\\pi", "π")
        expression = expression.replace("\\rho", "ρ")
        expression = expression.replace("\\sigma", "σ")
        expression = expression.replace("\\tau", "τ")
        expression = expression.replace("\\chi", "χ")
        expression = expression.replace("\\psi", "ψ")
        expression = expression.replace("\\omega", "ω")
        expression = expression.replace("\\Gamma", "Γ")
        expression = expression.replace("\\Delta", "Δ")

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

            if expression[i] == "(":
                self.sub_shape = 1
            
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
            center_pos = -1
            for i, sub in enumerate(self.subs):
                sub_analyze = sub.analyze()
                if self.subs.__len__() % 2 != 0 and i == (self.subs.__len__() // 2):
                    center_pos = sub_analyze["center_pos"] + self.width
                pos_min = min(pos_min, sub_analyze["center_pos"] + self.width)
                pos_max = max(pos_max, sub_analyze["center_pos"] + self.width)
                self.width += sub_analyze["width"] + 1
            self.width -= 1
            self.center_pos = (pos_min + pos_max) / 2
            if self.subs.__len__() % 2 != 0:
                self.center_pos = center_pos
        return {"width": self.width, "center_pos": self.center_pos}
    
    def render_analyze(self, pos: int, level: int) -> None:
        self.position = numpy.array([pos, level])
        if self.subs:
            width_sum = 0
            for sub in self.subs:
                sub.render_analyze(width_sum + pos, level + 1)
                width_sum += sub.width + 1


    def transform_analyze(self) -> None:
        if self.subs:
            for sub in self.subs:
                sub.transform_analyze()

        is_source = self.title.find("<") != -1
        is_destination = self.title.find("@") != -1

        if is_source:
            global transformation_sources
            i = 0
            source_key = ""
            while i < len(self.title):
                if self.title[i] == "<":
                    i += 1
                    while self.title[i] != ">":
                        source_key += self.title[i]
                        i += 1
                        if i == len(self.title):
                            break
                    transformation_sources[source_key] = self.render_position
                    print(source_key)
                    source_key = ""
                i += 1
        
        if is_destination:
            global transformation_destinations
            i = 0
            destination_key = ""
            while i < len(self.title):
                if self.title[i] == "@":
                    i += 1
                    while self.title[i] not in {" ", "@", "<"}:
                        destination_key += self.title[i]
                        i += 1
                        if i == len(self.title):
                            break
                    transformation_destinations.append((destination_key, self.render_position))
                    print(destination_key)
                    destination_key = ""
                    i -= 1
                i += 1

        if is_source:
            i =0
            cleared_title = ""
            while i < len(self.title):
                if self.title[i] == "<":
                    i += 1
                    while self.title[i] != ">":
                        i += 1
                else:
                    cleared_title += self.title[i]
                i += 1
            self.title = cleared_title

        if is_destination:
            i =0
            cleared_title = ""
            while i < len(self.title):
                if self.title[i] == "@":
                    i += 1
                    while self.title[i] not in {" ", "@", "<"}:
                        i += 1
                        if i == len(self.title):
                            break
                else:
                    cleared_title += self.title[i]
                i += 1
            self.title = cleared_title

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
        render_position[0] += self.center_pos * self.zoom[0] + 75
        render_position[1] += 50

        return render_position

    # def pg_render(self, surface: pygame.Surface, font: pygame.Font) -> None:
    #     if self.subs:
    #         for sub in self.subs:
    #             pygame.draw.aaline(surface, (255, )*3, self.render_position, sub.render_position)
    #             sub.pg_render(surface, font)

    #     text_surface = font.render(self.title, True, (255, )*3)
    #     rect = text_surface.get_rect()
    #     rect.center = self.render_position
    #     bgrect = rect.inflate(10, 10)
    #     bgrect.y -= 4
    #     pygame.draw.rect(surface, (0, )*3, bgrect, 0, 8)
    #     surface.blit(text_surface, rect)

    def svg_render(self, dwg: svgwrite.Drawing, font: pygame.font.Font) -> None:
        self_pos = (int(self.render_position[0]), int(self.render_position[1]))
        if self.subs:
            if self.sub_shape == 0:
                for sub in self.subs:
                    sub_pos = (int(sub.render_position[0]), int(sub.render_position[1]))
                    dwg.add(dwg.line(start=(self_pos[0], self_pos[1] + 20), end=(sub_pos[0], sub_pos[1] - 20), stroke="black"))
                    sub.svg_render(dwg, font)
            if self.sub_shape == 1:
                sub1_pos = (int(self.subs[0].render_position[0]), int(self.subs[0].render_position[1]))
                sub2_pos = (int(self.subs[-1].render_position[0]), int(self.subs[-1].render_position[1]))
                
                render_size = -20
                for sub in self.subs:
                    for char in sub.title:
                        if is_cjk(char):
                            render_size += 24
                        else:
                            render_size += font.size(char)[0]
                    render_size += 10
                render_size += 40 if self.subs.__len__() == 1 else 0

                dwg.add(dwg.polygon(points=[
                    (self_pos[0], self_pos[1] + 20),
                    (sub1_pos[0]-render_size/2, sub1_pos[1] - 20),
                    (sub2_pos[0]+render_size/2, sub2_pos[1] - 20),
                ], fill="white", stroke="black"))#闭合三角形
                for sub in self.subs:
                    sub.svg_render(dwg, font)

        title = self.title.replace('{', '[').replace('}', ']')

        text_surface = font.render(title, True, (255, )*3)
        rect = text_surface.get_rect()
        rect.center = self.render_position
        bgrect = rect.inflate(10, 10)
        bgrect.y -= 4
        if self.title != "\\0":
            text = dwg.text(title, insert=(self_pos[0], self_pos[1] + 6), text_anchor="middle", fill="black")
            dwg.add(text)

    def __str__(self) -> str:
        subs_str = ' '.join(str(sub) for sub in self.subs)
        return f"{self.title}[{subs_str}]" if subs_str else self.title
    
def generate_file(code: str, name: str, end_leveled: bool = True) -> tuple[int, int]:

    global transformation_sources, transformation_destinations
    transformation_sources = {}
    transformation_destinations = []

    if not code:
        raise ValueError("Empty code")
    block = Block(code, None)
    block.analyze()
    block.render_analyze(0, 0)
    zoom = numpy.array([50, 80])
    block.set_zoom(zoom)
    block.transform_analyze()

    if end_leveled:
        block.set_end_leveled(block.level_count)

    size = (int(block.width * zoom[0] + 100), int(block.level_count * zoom[1] + 40)) if not transformation_destinations \
        else (int(block.width * zoom[0] + 100), int(block.level_count * zoom[1] + 140))
    pygame.init()
    font = pygame.font.Font(r'./lmromanslant.otf', 16)
    dwg = svgwrite.Drawing(name, size=size, font_family="'Latin Modern Roman Slanted'", font_size=24)
    dwg.add(dwg.rect(insert=(0, 0), size=size, fill="white"))
    block.svg_render(dwg, font)

    for dest_key, dest_pos in transformation_destinations:
        if dest_key in transformation_sources:
            source_pos = transformation_sources[dest_key]
            source_pos = (int(source_pos[0]), int(source_pos[1] + 20))
            dest_pos = (int(dest_pos[0]), int(dest_pos[1] + 20))

            x_diff = abs(dest_pos[0] - source_pos[0])

            dwg.add(
                dwg.path(
                    d=f"M {source_pos[0]} {source_pos[1]} C {source_pos[0]} {source_pos[1]+x_diff*0.5} {dest_pos[0]} {dest_pos[1]+x_diff*0.5} {dest_pos[0]} {dest_pos[1]}",
                    stroke="black",
                    stroke_width=1,
                    fill="none"
                )
            )

            ARROW_SIZE = 5
            dwg.add(
                dwg.line(
                    start=(dest_pos[0], dest_pos[1]),
                    end=(dest_pos[0]-ARROW_SIZE, dest_pos[1]+ARROW_SIZE),
                    stroke="black",
                    stroke_width=1,
                )
            )
            dwg.add(
                dwg.line(
                    start=(dest_pos[0], dest_pos[1]),
                    end=(dest_pos[0]+ARROW_SIZE, dest_pos[1]+ARROW_SIZE),
                    stroke="black",
                    stroke_width=1,
                )
            )


    dwg.save()
    return size

if __name__ == "__main__":
    generate_file("S[NP[D[the] N[boy]] IP[I'[\\empty] VP[V[hit] NP[D[the] N[\"ball <a>\"]]]]]", "test.svg")