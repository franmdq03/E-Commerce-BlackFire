"""
Formulario de creación de órdenes para la tienda.

Incluye información del cliente, dirección, tipo de entrega y notas adicionales.
Valida que los campos de envío estén completos si se selecciona "Envío a domicilio".
"""

from django import forms

TIPO_ENTREGA = (
    ("domicilio", "Envío a domicilio"),
    ("retiro_local", "Retiro en local"),
)


class FormularioOrden(forms.Form):
    # Información del cliente
    nombre = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    apellido = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    correo = forms.EmailField(
        required=True, widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    telefono = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    # Dirección de facturación (opcional)
    direccion_1 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    direccion_2 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    ciudad = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    provincia = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    pais = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    # Nota adicional de la orden
    nota_orden = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        required=False,
    )

    # Tipo de entrega: domicilio o retiro en local
    tipo_entrega = forms.ChoiceField(
        choices=TIPO_ENTREGA,
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
    )

    # Campos obligatorios si se selecciona envío a domicilio
    direccion_envio = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    ciudad_envio = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    cp_envio = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def clean(self):
        """
        Valida que los campos de envío estén completos si se selecciona "domicilio".
        """
        cleaned_data = super().clean()
        tipo_entrega = cleaned_data.get("tipo_entrega")

        if tipo_entrega == "domicilio":
            if not cleaned_data.get("direccion_envio"):
                self.add_error(
                    "direccion_envio",
                    "Este campo es obligatorio para envío a domicilio.",
                )
            if not cleaned_data.get("ciudad_envio"):
                self.add_error(
                    "ciudad_envio", "Este campo es obligatorio para envío a domicilio."
                )
            if not cleaned_data.get("cp_envio"):
                self.add_error(
                    "cp_envio", "Este campo es obligatorio para envío a domicilio."
                )
