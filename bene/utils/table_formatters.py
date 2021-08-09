import django_tables2 as tables

counter = 0


def generate(li_dict):
    # unique classname.
    global counter
    counter += 1
    table_classname = "MyTableClass%s" % (counter)

    class Meta:
        # ahhh... Bootstrap
        attrs = {"class": "table table-striped"}

    # generate a class dynamically
    cls = type(table_classname, (tables.Table,), dict(Meta=Meta))

    # grab the first dict's keys
    try:
        li = li_dict[0].keys()
    except IndexError:
        li = ["No Data"]

    for colname in li:
        column = tables.Column(orderable=False)
        cls.base_columns[colname] = column

    return cls
