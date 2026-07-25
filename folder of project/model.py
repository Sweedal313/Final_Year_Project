def detect_category(text):
    text = text.lower()

    if any(x in text for x in ["swiggy","zomato","dominos","pizza hut","kfc","magicpin"]):
        return "Food"
    elif any(x in text for x in ["zudio","decathlon","max"]):
        return "Cloth"
    elif "agency" in text:
        return "Travel"
    elif "ramakrishna" in text:
        return "Rent"
    elif any(x in text for x in ["amazon","flipkart","myntra"]):
        return "Shopping"
    elif any(x in text for x in ["grocery","vegetable","fruit"]):
        return "Household"
    else:
        return "Others"