
def nonconsec_find(needle, haystack, anchored=False):
    """checks if each character of "needle" can be
    found in order (but not
    necessarily consecutivly) in haystack.
    For example, "mm" can be found in "matchmove",
    but not "move2d"
    "m2" can be found in "move2d", but not "matchmove"

    >>> nonconsec_find("m2", "move2d")
    True
    >>> nonconsec_find("m2", "matchmove")
    False

    Anchored ensures the first letter matches

    >>> nonconsec_find(
    "atch", "matchmove", anchored = False)
    True
    >>> nonconsec_find(
    "atch", "matchmove", anchored = True)
    False
    >>> nonconsec_find(
    "match", "matchmove", anchored = True)
    True

    If needle starts with a string,
    non-consecutive searching is disabled:

    >>> nonconsec_find(
    " mt", "matchmove", anchored = True)
    False
    >>> nonconsec_find(
    " ma", "matchmove", anchored = True)
    True
    >>> nonconsec_find(
    " oe", "matchmove", anchored = False)
    False
    >>> nonconsec_find(
    " ov", "matchmove", anchored = False)
    True
    """

    # if "[" not in needle:
    #     haystack = haystack.rpartition(" [")[0]

    if len(haystack) == 0 and len(needle) > 0:
        # "a" is not in ""
        return False

    elif len(needle) == 0 and len(haystack) > 0:
        # "" is in "blah"
        return True

    elif len(needle) == 0 and len(haystack) == 0:
        # ..?
        return True

    # Turn haystack into list of characters
    # (as strings are immutable)
    haystack = [hay for hay in str(haystack)]

    if needle.startswith(" "):
        # "[space]abc" does consecutive
        # search for "abc" in "abcdef"
        if anchored:
            if "".join(
                haystack).startswith(
                needle.lstrip(" ")):
                return True
        else:
            if needle.lstrip(" ") in "".join(haystack):
                return True

    if anchored:
        if needle[0] != haystack[0]:
            return False
        else:
            # First letter matches, remove it
            # for further matches
            needle = needle[1:]
            del haystack[0]

    for needle_atom in needle:
        try:
            needle_pos = haystack.index(needle_atom)
        except ValueError:
            return False
        else:
            # Dont find string in same pos or
            # backwards again
            del haystack[:needle_pos + 1]
    return True
