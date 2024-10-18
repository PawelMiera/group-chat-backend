from django import forms


class CommaSeparatedField(forms.CharField):

    def to_python(self, value):
        if value in self.empty_values:
            return self.empty_value
        value = str(value).split(',')
        if self.strip:
            value = [s.strip() for s in value]
        return value

    def prepare_value(self, value):
        if value is None:
            return None
        return ','.join([str(s) for s in value])
