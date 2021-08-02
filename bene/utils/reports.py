from explorer.exporters import BaseExporter
import json
from datetime import datetime

from six import StringIO, BytesIO
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell, xl_range


class ExcelExporter(BaseExporter):
    name = "Excel"
    content_type = "application/vnd.ms-excel"
    file_extension = ".xlsx"

    def _get_output(self, res, **kwargs):
        if self.query.id == 1:
            return self.sales_day_book_output(res, **kwargs)
        else:
            return self.default_output(res, **kwargs)

    def sales_day_book_output(self, res, **kwargs):
        output = BytesIO()

        header_dict = {
            "inv_number": "Number",
            "name": "Name",
            "number": "A/C",
            "inv_date": "Date",
            "nett": "Goods",
            "tax": "VAT",
            "gross": "Total",
        }

        def header_lookup(name):
            try:
                return header_dict[name]
            except:
                return name

        wb = xlsxwriter.Workbook(output)

        # XLSX writer wont allow sheet names > 31 characters
        # https://github.com/jmcnamara/XlsxWriter/blob/master/xlsxwriter/test/workbook/test_check_sheetname.py
        title = self.query.title[:31]

        ws = wb.add_worksheet(name=title)
        for range, width in [
            ("A:A", 9),
            ("B:B", 11),
            ("C:C", 6),
            ("D:D", 37),
            ("E:G", 9),
        ]:
            ws.set_column(range, width)
        # Write headers
        row = 0
        col = 0
        header_style = wb.add_format({"bold": True})
        total_style = wb.add_format({"bold": True, "num_format": "#,##0.00"})
        total_style.set_top()
        total_style.set_bottom()
        std_format = wb.add_format({"num_format": "#,##0.00"})
        for header in res.header_strings:
            ws.write(row, col, header_lookup(header), header_style)
            col += 1

        # Write data
        row = 1
        col = 0
        for data_row in res.data:
            for data in data_row:
                # xlsxwriter can't handle timezone-aware datetimes, so we help out here and just cast it to a string
                if isinstance(data, datetime):
                    data = str(data)
                # JSON and Array fields
                if isinstance(data, dict) or isinstance(data, list):
                    data = json.dumps(data)
                ws.write(row, col, data, std_format)
                col += 1
            row += 1
            col = 0
        # Write Footers
        for sum_col in (4, 5, 6):
            ws.write_formula(
                row,
                sum_col,
                f"=sum({xl_range(1,sum_col, row-1, sum_col)})",
                total_style,
            )
        wb.close()
        return output

    def default_output(self, res, **kwargs):
        import xlsxwriter

        output = BytesIO()

        wb = xlsxwriter.Workbook(output)

        # XLSX writer wont allow sheet names > 31 characters
        # https://github.com/jmcnamara/XlsxWriter/blob/master/xlsxwriter/test/workbook/test_check_sheetname.py
        title = self.query.title[:31]

        ws = wb.add_worksheet(name=title)

        # Write headers
        row = 0
        col = 0
        header_style = wb.add_format({"bold": True})
        for header in res.header_strings:
            ws.write(row, col, header, header_style)
            col += 1

        # Write data
        row = 1
        col = 0
        for data_row in res.data:
            for data in data_row:
                # xlsxwriter can't handle timezone-aware datetimes, so we help out here and just cast it to a string
                if isinstance(data, datetime):
                    data = str(data)
                # JSON and Array fields
                if isinstance(data, dict) or isinstance(data, list):
                    data = json.dumps(data)
                ws.write(row, col, data)
                col += 1
            row += 1
            col = 0

        wb.close()
        return output
