import pygame
import sys
import math
from bplus_tree import BPlusTree, get_levels
pygame.init()

WIDTH, HEIGHT = 1100, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Database Index Visualizer")
font = pygame.font.SysFont(None, 32)
font1 = pygame.font.SysFont(None, 20)
clock = pygame.time.Clock()

def draw_node(node, x, y):
    keys = node.keys
    text = "   ".join(map(str,keys))
    txt = font.render(text, True, "blue")
    

    width = txt.get_width() + 20
    rect = pygame.Rect(x, y, width, 40)

    pygame.draw.rect(screen, "white", rect)
    pygame.draw.rect(screen, "black", rect, 2)
    screen.blit(txt, (x + 10, y + 10))
    return rect

def draw_tree(levels):
    node_positions = []
    gap_y = 100
    gap_x = 150
    for index, level in enumerate(levels):
        y = 120 + index * gap_y
        total_width = len(level)* gap_x
        
        start_x = (WIDTH - total_width) //2
        level_positions = []
        for i, node in enumerate(level): 
            x = start_x + i * gap_x
            rect = draw_node(node, x, y)
            level_positions.append(rect)
    
        node_positions.append(level_positions)
    draw_lines(node_positions)

def draw_lines(node_positions):

    for level in range(len(node_positions) -1):
        parents = node_positions[level];
        childs = node_positions[level + 1]

        for i, parent in enumerate(parents):
            
            each_child_count = math.ceil(len(childs) / len(parents))
        

            for j in range(each_child_count):
                
                child_index = i * each_child_count + j
                if child_index >= len(childs):
                    break
                parent_center = (
                    parent.left + (j + 1) * parent.width // (each_child_count + 1),
                    parent.bottom
                )
                child = childs[child_index]
                child_center = child.midtop

                pygame.draw.line(screen, "black", parent_center, child_center, 2)
                


    draw_arrow(node_positions[-1])        

def draw_arrow(nodes):
    for i in  range(len(nodes)-1):
        current_node = (nodes[i].x + nodes[i].width, nodes[i].y + 20)
        next_node = (nodes[i+1].x, nodes[i+1].y + 20)
        pygame.draw.line(screen, "black",current_node, next_node , 2)

        x = nodes[i+1].x
        y = nodes[i+1].y + 20
        points = [(x,y), (x-6, y - 6), (x - 6, y+6)]
        pygame.draw.polygon(screen, "black", points)


insertButton_center = 100, 50
deleteButton_center = 200, 50
searchButton_center = 300, 50
printButton_center = 400, 50
resetButton_center  = 500, 50
cursor_visible = True
cursor_timer = 0
cursor_interval = 500 
insert_box = pygame.Rect(5, 5, 80, 30)
insert_button = pygame.Rect(87, 5, 60, 30)
delete_box = pygame.Rect(149, 5, 80, 30)
delete_button = pygame.Rect(231, 5, 60, 30)
search_box = pygame.Rect(293, 5, 80, 30)
search_button = pygame.Rect(375, 5, 60, 30)
print_button = pygame.Rect(437, 5, 60, 30)
clear_button = pygame.Rect(499, 5, 60, 30)
insert_active = False
delete_active = False
search_active = False
insert_text = ""
delete_text = ""
search_text = ""
search_message = ""        
search_message_timer = 0   
highlight_value = None     
tree = BPlusTree(order=3)
levels = []

running = True
while running:
    dt = clock.tick(30) 
 # Count down the search message timer
    if search_message_timer > 0:
        search_message_timer -= dt
        if search_message_timer <= 0:
            search_message = ""
            highlight_value = None
            
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            if insert_button.collidepoint(mouse_pos):
                if insert_text != "":
                    value = int(insert_text)

                    tree.insert(value)

                    levels = get_levels(tree.root)

                    insert_text = ""
            if insert_box.collidepoint(mouse_pos):
                insert_active = True
                print("Insert Box Pressed")
            else:
                insert_active = False

            if delete_button.collidepoint(mouse_pos):
                if delete_text != "":
                    value = int(delete_text)
                    tree.delete(value)
                    levels = get_levels(tree.root)
                    delete_text = ""
                    
            if delete_box.collidepoint(mouse_pos):
                delete_active = True
                print("Delete Box Pressed")
            else:
                delete_active = False

            if search_button.collidepoint(mouse_pos):
                if search_text != "":
                    value = int(search_text)
                    found = tree.search(value)
                    if found:
                        search_message = f"{value} Found!"
                        highlight_value = value
                    else:
                        search_message = f"{value} Not Found!"
                        highlight_value = None
                    search_message_timer = 2500  
                    search_text = ""
                    
            if search_box.collidepoint(mouse_pos):
                search_active = True
                print("Search Box Pressed")
            else:
                search_active = False

            if print_button.collidepoint(mouse_pos):
                node = tree.root
                while not node.leaf:
                    node = node.children[0]
                while node:
                    print(node.keys)
                    node = node.next
                    
            if clear_button.collidepoint(mouse_pos):
                tree = BPlusTree(order=3)
                levels = []
                search_message = ""
                highlight_value = None

        
                
        if event.type == pygame.KEYDOWN and insert_active:
            if event.key == pygame.K_BACKSPACE:
                insert_text = insert_text[:-1]
            elif event.unicode.isdigit() and len(insert_text) < 4:
                 insert_text += event.unicode
        
        if event.type == pygame.KEYDOWN and delete_active:
            if event.key == pygame.K_BACKSPACE:
                delete_text = delete_text[:-1]
            elif event.unicode.isdigit() and len(delete_text) < 4:
                delete_text += event.unicode
        
        if event.type == pygame.KEYDOWN and search_active:
            if event.key == pygame.K_BACKSPACE:
                search_text = search_text[:-1]
            elif event.unicode.isdigit() and len(search_text) < 4: 
                search_text += event.unicode

            
    
    
    cursor_timer += dt
    if cursor_timer >= cursor_interval:
        cursor_visible = not cursor_visible
        cursor_timer = 0
    screen.fill("white")
 
    insert_surface = font.render(insert_text, True, "blue")
    screen.blit(insert_surface, (insert_box.x + 5, insert_box.y + 5))

    delete_surface = font.render(delete_text, True, "red")
    screen.blit(delete_surface, (delete_box.x + 5, delete_box.y + 5))

    search_surface = font.render(search_text, True, "blue")
    screen.blit(search_surface, (search_box.x + 5, search_box.y + 5))

    if insert_active and cursor_visible:
        cursor_x = insert_box.x + 5 + insert_surface.get_width()
        cursor_y = insert_box.y + 5
        cursor_height = insert_surface.get_height()
        pygame.draw.line(screen, "grey", (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)
        

    if delete_active and cursor_visible:
        cursor_x = delete_box.x + 5 + delete_surface.get_width()
        cursor_y = delete_box.y + 5
        cursor_height = delete_surface.get_height()
        pygame.draw.line(screen, "grey", (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)


    if search_active and cursor_visible:
        cursor_x = search_box.x + 5 + search_surface.get_width()
        cursor_y = search_box.y + 5
        cursor_height = search_surface.get_height()
        pygame.draw.line(screen, "grey", (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)


    # Draw input box rectangle
    if insert_active:
        pygame.draw.rect(screen, "black", insert_box, 2)
    else:
        pygame.draw.rect(screen, "grey", insert_box, 2)

    if delete_active:
        pygame.draw.rect(screen, "black", delete_box, 2)
    else:
        pygame.draw.rect(screen, "grey", delete_box, 2)
    
    if search_active:
        pygame.draw.rect(screen, "black", search_box, 2)
    else:
        pygame.draw.rect(screen, "grey", search_box, 2)

    
    pygame.draw.rect(screen, "lightblue", insert_button, border_radius=10)
    pygame.draw.rect(screen, "black", insert_button, 2, border_radius=10)
    ins_text = font1.render("Insert", True, "black")
    text_rect = ins_text.get_rect(center=insert_button.center)
    screen.blit(ins_text, text_rect)
    


    pygame.draw.rect(screen, "lightblue", delete_button, border_radius=10)
    pygame.draw.rect(screen, "black", delete_button, 2, border_radius=10)
    ins_text = font1.render("Delete", True, "black")
    text_rect = ins_text.get_rect(center=delete_button.center)
    screen.blit(ins_text, text_rect)


    pygame.draw.rect(screen, "lightblue", search_button, border_radius=10)
    pygame.draw.rect(screen, "black", search_button, 2, border_radius=10)
    ins_text = font1.render("Search", True, "black")
    text_rect = ins_text.get_rect(center=search_button.center)
    screen.blit(ins_text, text_rect)

    pygame.draw.rect(screen, "lightblue", print_button, border_radius=10)
    pygame.draw.rect(screen, "black", print_button, 2, border_radius=10)
    ins_text = font1.render("Print", True, "black")
    text_rect = ins_text.get_rect(center=print_button.center)
    screen.blit(ins_text, text_rect)

    pygame.draw.rect(screen, "lightblue", clear_button, border_radius=10)
    pygame.draw.rect(screen, "black", clear_button, 2, border_radius=10)
    ins_text = font1.render("Clear", True, "black")
    text_rect = ins_text.get_rect(center=clear_button.center)
    screen.blit(ins_text, text_rect)

    if search_message:
        color = "green" if "Not" not in search_message else "red"
        msg_surface = font.render(search_message, True, color)
        screen.blit(msg_surface, (WIDTH // 2 - msg_surface.get_width() // 2, 80))
    
    if levels:
        draw_tree(levels)
    pygame.display.flip()




    clock.tick(60)

pygame.quit()
