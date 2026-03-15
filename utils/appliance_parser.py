import re


def parse_appliances(text):

    appliances = []

    pattern = r'(\d+)\s*([a-zA-Z\s]+?)\s*(\d+(\.\d+)?)\s*k?w?\s*(\d+(\.\d+)?)\s*h'

    matches = re.findall(pattern, text.lower())

    for m in matches:

        qty = int(m[0])
        name = m[1].strip()
        kw = float(m[2])
        hours = float(m[4])

        appliances.append({
            "name": name.title(),
            "kw": kw,
            "quantity": qty,
            "hours": hours
        })

    return appliances