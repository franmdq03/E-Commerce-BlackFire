from django import forms

TIPO_ENTREGA = (
    ('domicilio', 'Envío a domicilio'),
    ('retiro_local', 'Retiro en local'),
)

class FormularioOrden(forms.Form):
    nombre = forms.CharField(max_length=100, required=True)
    apellido = forms.CharField(max_length=100, required=True)
    correo = forms.EmailField(required=True)
    telefono = forms.CharField(max_length=20, required=True)
    direccion_1 = forms.CharField(max_length=255, required=False)
    direccion_2 = forms.CharField(max_length=255, required=False)
    ciudad = forms.CharField(max_length=100, required=False)
    provincia = forms.CharField(max_length=100, required=False)
    pais = forms.CharField(max_length=100, required=False)
    nota_orden = forms.CharField(widget=forms.Textarea, required=False)
    
    tipo_entrega = forms.ChoiceField(choices=TIPO_ENTREGA, widget=forms.RadioSelect)
    
    # Campos para envío a domicilio
    direccion_envio = forms.CharField(max_length=255, required=False)
    ciudad_envio = forms.CharField(max_length=100, required=False)
    cp_envio = forms.CharField(max_length=20, required=False)

    def clean(self):
        cleaned_data = super().clean()
        tipo_entrega = cleaned_data.get("tipo_entrega")

        # Si es envío a domicilio, estos campos son obligatorios
        if tipo_entrega == 'domicilio':
            if not cleaned_data.get('direccion_envio'):
                self.add_error('direccion_envio', 'Este campo es obligatorio para envío a domicilio.')
            if not cleaned_data.get('ciudad_envio'):
                self.add_error('ciudad_envio', 'Este campo es obligatorio para envío a domicilio.')
            if not cleaned_data.get('cp_envio'):
                self.add_error('cp_envio', 'Este campo es obligatorio para envío a domicilio.')


