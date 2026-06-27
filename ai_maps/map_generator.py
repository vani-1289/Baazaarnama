import random

def generate_virtual_grid(shops):
    """
    Given a list of shops, assigns them virtual layout positions (map_x, map_y) on a 10x10 grid.
    Walkways are at rows/cols 3 and 7 to simulate a structured market.
    Stalls are placed in blocks: [1,2], [4,5,6], [8,9,10].
    """
    available_spots = []
    walkways_x = {3, 7}
    walkways_y = {3, 7}

    for x in range(1, 11):
        if x in walkways_x:
            continue
        for y in range(1, 11):
            if y in walkways_y:
                continue
            available_spots.append((x, y))

    # Shuffle to distribute randomly but reproducibly (using shop IDs or names as seed if desired)
    random.seed(42)
    random.shuffle(available_spots)

    layout = {}
    for i, shop in enumerate(shops):
        # If the shop has a customized map_x and map_y, keep it (unless it's default 1,1)
        if (shop.map_x != 1 or shop.map_y != 1) and (shop.map_x, shop.map_y) not in walkways_x:
            layout[shop.id] = {
                'id': shop.id,
                'name': shop.name,
                'category': shop.category.name if shop.category else "Other",
                'icon': shop.category.icon if shop.category else "fa-store",
                'x': shop.map_x,
                'y': shop.map_y,
                'image': shop.shop_image.url if shop.shop_image else "/static/images/default_shop.jpg",
                'rating': shop.average_rating,
                'verified': shop.verified_shop
            }
        else:
            # Fallback to dynamic spot from available spots list
            if i < len(available_spots):
                x, y = available_spots[i]
            else:
                x, y = (random.randint(1, 10), random.randint(1, 10))
            
            layout[shop.id] = {
                'id': shop.id,
                'name': shop.name,
                'category': shop.category.name if shop.category else "Other",
                'icon': shop.category.icon if shop.category else "fa-store",
                'x': x,
                'y': y,
                'image': shop.shop_image.url if shop.shop_image else "/static/images/default_shop.jpg",
                'rating': shop.average_rating,
                'verified': shop.verified_shop
            }
    return layout
