async def has_brand_mention(text, brand_name):
    """Checks if the text contains at least one case-insensitive mention of the brand name."""
    if not text:
        return 0
    # Return 1 if mentioned at least once, 0 otherwise
    return 1 if brand_name.lower() in text.lower() else 0

