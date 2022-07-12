def find_exactly_one(
    xs,
):
    """like any(xs)
    except returns the found object or raises ValueError
    only accepts
    """
    b = False
    v = None
    for x in xs:
        if x:
            if b:
                raise ValueError("duplicate found")
            else:
                v = x
                b = True
    if b:
        return v
    else:
        raise ValueError("cannot find")
