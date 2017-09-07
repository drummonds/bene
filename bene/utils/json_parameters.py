class JSCONConversionError(Exception):
    pass

def json_to_params(j):
    if len(j) == 0:
        return ''
    else:
        result = '?params='
        for n, f in enumerate(j):
            if n:
                result +='%7C'
            result += f'{f}%3A'
            param = j[f];
            if isinstance(param, str) or isinstance(param, int) or isinstance(param, float):
                result.append(param)
            elif isinstance(param, list) and len(param) == 3:  # Then a coded date
                result += str(param[0]) + '-' +  ('0' + str(param[1]))[-2:] + '-' +  ('0' + str(param[2]))[-2:]
        return result

