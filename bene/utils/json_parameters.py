class JSCONConversionError(Exception):
    pass


def json_to_params(j):
    """Given a JSON object convert it to a URL parameter string"""
    if len(j) == 0:
        return ""
    else:
        result = "params="
        for n, f in enumerate(j):
            if n:
                result += "%7C"
            result += f"{f}%3A"
            param = j[f]
            if (
                isinstance(param, str)
                or isinstance(param, int)
                or isinstance(param, float)
            ):
                result.append(param)
            elif isinstance(param, list) and len(param) == 3:  # Then a coded date
                result += (
                    str(param[0])
                    + "-"
                    + ("0" + str(param[1]))[-2:]
                    + "-"
                    + ("0" + str(param[2]))[-2:]
                )
        return result


def json_to_param_dict(j):
    """Given a JSON object convert it to a parameter dictionary"""
    result = {}
    for f in j:
        param = j[f]
        if isinstance(param, str) or isinstance(param, int) or isinstance(param, float):
            result[f"{f}"] = param
        elif isinstance(param, list) and len(param) == 3:  # Then a coded date
            result[f"{f}"] = (
                str(param[0])
                + "-"
                + ("0" + str(param[1]))[-2:]
                + "-"
                + ("0" + str(param[2]))[-2:]
            )
    return result
