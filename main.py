import pygame
import random
from bplus_tree import BPlusTree, get_levels

pygame.init()

WIDTH, HEIGHT = 1100, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Database Index Visualizer")
font = pygame.font.SysFont(None, 32)
font1 = pygame.font.SysFont(None, 20)
clock = pygame.time.Clock()


def format_node_keys(keys, max_keys_shown=6):
    if len(keys) <= max_keys_shown:
        return "  ".join(map(str, keys))
    head = "  ".join(map(str, keys[:3]))
    tail = "  ".join(map(str, keys[-2:]))
    return f"{head}  ...  {tail}"


def draw_node(node, x, y):
    text = format_node_keys(node.keys)
    key_font = pygame.font.SysFont(None, 34 if len(node.keys) <= 6 else 28)
    txt = key_font.render(text, True, "blue")

    width = min(max(txt.get_width() + 22, 80), 220)
    rect = pygame.Rect(x, y, width, 40)

    pygame.draw.rect(screen, "white", rect)
    pygame.draw.rect(screen, "black", rect, 2)
    text_rect = txt.get_rect(center=rect.center)
    screen.blit(txt, text_rect)
    return rect


def draw_tree(levels):
    if not levels:
        return

    node_positions = []
    gap_y = 100
    min_gap = 18
    margin = 10

    for index, level in enumerate(levels):
        y = 120 + index * gap_y

        widths = []
        for node in level:
            preview_text = format_node_keys(node.keys)
            preview_font = pygame.font.SysFont(None, 34 if len(node.keys) <= 6 else 28)
            preview_width = preview_font.render(preview_text, True, "blue").get_width() + 22
            widths.append(min(max(preview_width, 80), 220))

        total_nodes_width = sum(widths)
        available = WIDTH - 2 * margin
        gap_x = min_gap
        if len(level) > 1 and total_nodes_width < available:
            gap_x = max(min_gap, (available - total_nodes_width) // (len(level) - 1))

        total_width = total_nodes_width + gap_x * max(0, len(level) - 1)
        start_x = max(margin, (WIDTH - total_width) // 2)

        level_positions = []
        x = start_x
        for node in level:
            rect = draw_node(node, x, y)
            level_positions.append(rect)
            x += rect.width + gap_x

        node_positions.append(level_positions)

    draw_lines(node_positions)


def draw_lines(node_positions):
    for level in range(len(node_positions) - 1):
        parents = node_positions[level]
        children = node_positions[level + 1]

        for i, parent in enumerate(parents):
            start = round(i * len(children) / len(parents))
            end = round((i + 1) * len(children) / len(parents))
            parent_center = (parent.centerx, parent.bottom)

            for child in children[start:end]:
                pygame.draw.line(screen, "black", parent_center, child.midtop, 2)

    draw_arrow(node_positions[-1])


def draw_arrow(nodes):
    for i in range(len(nodes) - 1):
        current_node = (nodes[i].x + nodes[i].width, nodes[i].y + 20)
        next_node = (nodes[i + 1].x, nodes[i + 1].y + 20)
        pygame.draw.line(screen, "black", current_node, next_node, 2)

        x = nodes[i + 1].x
        y = nodes[i + 1].y + 20
        points = [(x, y), (x - 6, y - 6), (x - 6, y + 6)]
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
demo_button = pygame.Rect(561, 5, 90, 30)
range_start_box = pygame.Rect(653, 5, 80, 30)
range_end_box = pygame.Rect(735, 5, 80, 30)
range_button = pygame.Rect(817, 5, 75, 30)
insert_active = False
delete_active = False
search_active = False
range_start_active = False
range_end_active = False
insert_text = ""
delete_text = ""
search_text = ""
range_start_text = ""
range_end_text = ""
search_message = ""        
search_message_timer = 0   
highlight_value = None     
tree = BPlusTree(order=16)
levels = []
range_message = ""

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

            range_start_active = range_start_box.collidepoint(mouse_pos)
            range_end_active = range_end_box.collidepoint(mouse_pos)

            if range_button.collidepoint(mouse_pos):
                if range_start_text != "" and range_end_text != "":
                    start = int(range_start_text)
                    end = int(range_end_text)
                    results = tree.range_query(start, end)
                    range_message = f"Range [{start}, {end}] -> {results}"

            if print_button.collidepoint(mouse_pos):
                node = tree.root
                while not node.leaf:
                    node = node.children[0]
                while node:
                    print(node.keys)
                    node = node.next

            if demo_button.collidepoint(mouse_pos):
                dataset = random.sample(range(1, 999), 40)
                tree = BPlusTree(order=16)
                tree.bulk_load(dataset)
                levels = get_levels(tree.root)
                search_message = "Loaded 40 random integer records"
                search_message_timer = 2500
                range_message = ""
                    
            if clear_button.collidepoint(mouse_pos):
                tree = BPlusTree(order=16)
                levels = []
                search_message = ""
                highlight_value = None
                range_message = ""

        
                
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

        if event.type == pygame.KEYDOWN and range_start_active:
            if event.key == pygame.K_BACKSPACE:
                range_start_text = range_start_text[:-1]
            elif event.unicode.isdigit() and len(range_start_text) < 4:
                range_start_text += event.unicode

        if event.type == pygame.KEYDOWN and range_end_active:
            if event.key == pygame.K_BACKSPACE:
                range_end_text = range_end_text[:-1]
            elif event.unicode.isdigit() and len(range_end_text) < 4:
                range_end_text += event.unicode

            
    
    
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

    range_start_surface = font.render(range_start_text, True, "purple")
    screen.blit(range_start_surface, (range_start_box.x + 5, range_start_box.y + 5))

    range_end_surface = font.render(range_end_text, True, "purple")
    screen.blit(range_end_surface, (range_end_box.x + 5, range_end_box.y + 5))

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

    if range_start_active and cursor_visible:
        cursor_x = range_start_box.x + 5 + range_start_surface.get_width()
        cursor_y = range_start_box.y + 5
        cursor_height = range_start_surface.get_height()
        pygame.draw.line(screen, "grey", (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)

    if range_end_active and cursor_visible:
        cursor_x = range_end_box.x + 5 + range_end_surface.get_width()
        cursor_y = range_end_box.y + 5
        cursor_height = range_end_surface.get_height()
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

    if range_start_active:
        pygame.draw.rect(screen, "black", range_start_box, 2)
    else:
        pygame.draw.rect(screen, "grey", range_start_box, 2)

    if range_end_active:
        pygame.draw.rect(screen, "black", range_end_box, 2)
    else:
        pygame.draw.rect(screen, "grey", range_end_box, 2)

    
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

    pygame.draw.rect(screen, "lightblue", demo_button, border_radius=10)
    pygame.draw.rect(screen, "black", demo_button, 2, border_radius=10)
    ins_text = font1.render("Load Demo", True, "black")
    text_rect = ins_text.get_rect(center=demo_button.center)
    screen.blit(ins_text, text_rect)

    pygame.draw.rect(screen, "thistle", range_button, border_radius=10)
    pygame.draw.rect(screen, "black", range_button, 2, border_radius=10)
    ins_text = font1.render("Range", True, "black")
    text_rect = ins_text.get_rect(center=range_button.center)
    screen.blit(ins_text, text_rect)

    if search_message:
        color = "green" if "Not" not in search_message else "red"
        msg_surface = font.render(search_message, True, color)
        screen.blit(msg_surface, (WIDTH // 2 - msg_surface.get_width() // 2, 80))

    if range_message:
        msg_surface = font1.render(range_message, True, "purple")
        screen.blit(msg_surface, (10, 88))
    
    if levels:
        draw_tree(levels)
    pygame.display.flip()


pygame.quit()
