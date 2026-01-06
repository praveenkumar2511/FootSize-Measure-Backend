def cm_to_shoe_size(foot_length_cm: float):
    """
    Converts foot length in cm to Indian, UK, and US shoe sizes.
    Approximate mapping based on standard charts.
    """
    # India/UK sizes are generally the same
    # US Size (Men) = UK Size + 1
    # Example: 26.3 cm -> UK 8, US 9, India 8
    
    # Simple linear approximation or lookup table
    # This is a common reference:
    # 25.4 cm -> UK 7 / US 8
    # 26.3 cm -> UK 8 / US 9
    # 27.1 cm -> UK 9 / US 10
    
    # Using a formula: UK = (CM / 2.54) * 3 - 23 (approx for adults)
    # However, a lookup or structured interpolation is better.
    
    size_chart = [
        (22.8, 4), (23.7, 5), (24.5, 6), (25.4, 7), (26.3, 8), (27.2, 9), (28.0, 10), (28.9, 11), (29.7, 12)
    ]
    
    # Find the closest size (rounding up)
    uk_size = 0
    for cm, size in size_chart:
        if foot_length_cm <= cm + 0.5: # Allow slight buffer
            uk_size = size
            break
    else:
        uk_size = 13 # Default max
        
    return {
        "india": uk_size,
        "uk": uk_size,
        "us": uk_size + 1
    }
