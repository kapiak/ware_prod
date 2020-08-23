from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property

TOTAL_FORM_COUNT = "TOTAL_FORMS"
INITIAL_FORM_COUNT = "INITIAL_FORMS"
MIN_NUM_FORM_COUNT = "MIN_NUM_FORMS"
MAX_NUM_FORM_COUNT = "MAX_NUM_FORMS"


class VueManagementForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.base_fields[TOTAL_FORM_COUNT] = forms.IntegerField(
            widget=forms.HiddenInput(attrs={"v-model": "totalForms"})
        )
        self.base_fields[INITIAL_FORM_COUNT] = forms.IntegerField(
            widget=forms.HiddenInput(attrs={"v-model": "initialForms"})
        )
        self.base_fields[MIN_NUM_FORM_COUNT] = forms.IntegerField(
            required=False, widget=forms.HiddenInput(attrs={"v-model": "minNumForms"}),
        )
        self.base_fields[MAX_NUM_FORM_COUNT] = forms.IntegerField(
            required=False, widget=forms.HiddenInput(attrs={"v-model": "maxNumForms"}),
        )
        super().__init__(*args, **kwargs)


class VueBaseFormSet(forms.BaseFormSet):
    @cached_property
    def management_form(self):
        if self.is_bound:
            form = VueManagementForm(
                self.data, auto_id=self.auto_id, prefix=self.prefix
            )
            if not form.is_valid():
                raise forms.ValidationError(
                    _("ManagementForm data is missing or has been tampered with"),
                    code="missing_management_form",
                )
        else:
            form = VueManagementForm(
                auto_id=self.auto_id,
                prefix=self.prefix,
                initial={
                    TOTAL_FORM_COUNT: self.total_form_count(),
                    INITIAL_FORM_COUNT: self.initial_form_count(),
                    MIN_NUM_FORM_COUNT: self.min_num,
                    MAX_NUM_FORM_COUNT: self.max_num,
                },
            )
        return form
