
def formatAuthorName(author: str) -> str:
    author = author.strip().lower().replace("-", "")

    formatted_author = author.strip()  # Remove leading/trailing whitespace

    # Check for comma
    if ',' in formatted_author:
        family_name, given_name = formatted_author.split(',', 1)
        formatted_author = f"{family_name.strip()}, {given_name.strip()}"
    else:
        # Check for space (no comma found)
        if ' ' not in formatted_author:
            return formatted_author
        else:
            # Split by last space
            last_space_index = formatted_author.rfind(' ')
            family_name = formatted_author[last_space_index + 1:]
            given_name = formatted_author[:last_space_index]
            formatted_author = f"{family_name.strip()}, {given_name.strip()}"

    return formatted_author
