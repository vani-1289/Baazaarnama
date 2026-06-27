from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from bazaar.models import Market, Shop
from .map_generator import generate_virtual_grid
from .route_optimizer import get_shortest_path

def market_map(request, market_id):
    market = get_object_or_404(Market, id=market_id)
    shops = market.shops.all()
    categories = list(set([shop.category for shop in shops if shop.category]))
    
    context = {
        'market': market,
        'categories': categories,
    }
    return render(request, 'ai_maps/market_map.html', context)


def market_map_data(request, market_id):
    market = get_object_or_404(Market, id=market_id)
    shops = market.shops.select_related('category').all()
    layout = generate_virtual_grid(shops)
    
    return JsonResponse({
        'market': {
            'id': market.id,
            'name': market.name,
            'latitude': float(market.latitude) if market.latitude else 28.6139,
            'longitude': float(market.longitude) if market.longitude else 77.2090,
        },
        'shops': list(layout.values())
    })


def walking_directions(request, market_id):
    market = get_object_or_404(Market, id=market_id)
    shops = market.shops.all()
    layout = generate_virtual_grid(shops)
    
    start_shop_id = request.GET.get('start')
    end_shop_id = request.GET.get('end')
    
    # Entrance coordinates default (let's say it's at walkway center x=5, y=10)
    start_x, start_y = 5, 10
    end_x, end_y = 5, 1
    
    if start_shop_id and start_shop_id != 'entrance':
        try:
            s_shop = layout[int(start_shop_id)]
            start_x, start_y = s_shop['x'], s_shop['y']
        except (KeyError, ValueError):
            pass
            
    if end_shop_id:
        try:
            e_shop = layout[int(end_shop_id)]
            end_x, end_y = e_shop['x'], e_shop['y']
        except (KeyError, ValueError):
            pass

    path = get_shortest_path(start_x, start_y, end_x, end_y, shop_positions=layout)
    
    # Generate instructions text based on steps
    instructions = []
    for i in range(len(path) - 1):
        curr = path[i]
        nxt = path[i+1]
        dx = nxt[0] - curr[0]
        dy = nxt[1] - curr[1]
        
        if dx == 1:
            instructions.append("Walk East (Right)")
        elif dx == -1:
            instructions.append("Walk West (Left)")
        elif dy == 1:
            instructions.append("Walk South (Down)")
        elif dy == -1:
            instructions.append("Walk North (Up)")

    # Group identical sequential instructions
    grouped_instructions = []
    if instructions:
        curr_inst = instructions[0]
        steps = 1
        for inst in instructions[1:]:
            if inst == curr_inst:
                steps += 1
            else:
                grouped_instructions.append(f"{curr_inst} for {steps} step(s)")
                curr_inst = inst
                steps = 1
        grouped_instructions.append(f"{curr_inst} for {steps} step(s)")
    else:
        grouped_instructions.append("You are already at the destination stall!")

    return JsonResponse({
        'path': path,
        'instructions': grouped_instructions
    })

# Helper shortcut for get_object_or_404 support if not imported
from django.shortcuts import get_object_or_404
