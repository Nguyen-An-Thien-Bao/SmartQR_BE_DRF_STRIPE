from products.models import MenuItem


def get_price(menu_item_id):
    try:
        item = MenuItem.objects.get(id=menu_item_id)
        return float(item.price)
    except MenuItem.DoesNotExist:
        return 0.0