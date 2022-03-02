from django.forms import ModelForm, ValidationError, Field, CharField

from .models import FilebabyFile, RemittanceFile, Report


class FilebabyForm(ModelForm):
    """Upload files with this form"""

    class Meta:
        model = FilebabyFile
        exclude = ("md5",)


class RemittanceForm(ModelForm):
    """Upload files with this form"""

    class Meta:
        model = RemittanceFile
        exclude = ("md5",)


class RemittanceForm(ModelForm):
    """Upload files with this form"""

    class Meta:
        model = RemittanceFile
        exclude = ("md5",)


# Code based on Forms in django-sql_explorer
class SqlField(Field):
    """This is class for each parameter field."""

    def validate(self, value):
        """
        Ensure that the SQL passes the blacklist.
        :param value: The SQL for this Query model.
        """

        # implmeent a simple blacklist see sql-explorer for a more complete version
        error = value.upper().find("DELETE") != -1
        error = error or value.upper().find("DROP") != -1
        error = error or value.upper().find("TRUCATE") != -1

        if error:
            raise ValidationError(
                "Field contains blacklist workd eg DELETE, DROP or TRUNCATE",
                code="InvalidSql",
            )


class QueryReportForm(ModelForm):
    """This is a class for SQL Query forms report.  Unlike sql-explorer there is no editing
    of the query eg (Title, Description, SQL)  Only the parameters"""

    def __init__(self, *args, **kwargs):
        super(QueryReportForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.instance and self.data.get("created_by_user", None):
            self.cleaned_data["created_by_user"] = self.instance.created_by_user
        return super(QueryReportForm, self).clean()

    @property
    def created_by_user_email(self):
        return (
            self.instance.created_by_user.email
            if self.instance.created_by_user
            else "--"
        )

    @property
    def created_at_time(self):
        return self.instance.created_at.strftime("%Y-%m-%d")

    class Meta:
        model = Report
        fields = ["name"]
