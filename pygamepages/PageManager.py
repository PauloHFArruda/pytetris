
main_surf = None
current_page = None
_pages = []
number_event_types = 7

def set_surf(surf):
    global main_surf
    main_surf = surf

def set_start_page(tag, *args, **kw):
    global current_page
    for page in _pages:
        if page.tag == tag:
            current_page = page
            current_page.on_open(*args, **kw)
            return

def change_page(tag, *args, **kw):
    global current_page
    for page in _pages:
        if page.tag == tag:
            current_page.on_close()
            current_page = page
            current_page.on_open(*args, **kw)
            return

def find_object(obj_id):
    aux = list(map(int, obj_id.strip().split('-')))
    obj = _pages[aux[0]]
    for index in aux[1:]:
        obj = obj._objects[index]
    
    return obj

def loop():
    current_page.update()
    current_page.draw()

def bind(event_type, func, obj_id):
    page = _pages[int(obj_id.split('-')[0])]
    page.event_funcs[event_type].append(func)

def event_handler(event):
    if event.type < number_event_types:
        for func in current_page.event_funcs[event.type]:
            func(event)
