from wtforms import Form, BooleanField, TextField, TextAreaField, validators
from wtfrecaptcha.fields import RecaptchaField

class CommentForm(Form):
    name            = TextField('Name', [validators.Length(min=4, max=25)])
    email           = TextField('E-Mail-Addresse', [validators.Length(min=6, max=35)])
    text            = TextAreaField('Dein Kommentar', [validators.Length(min=30, max=1000)])
    captcha         = RecaptchaField('Bist Du wirklich ein Mensch, und nicht etwa ein Kohlkopf oder irgendsowas?', public_key='6LfNEd8SAAAAAGXTp2hHAm5qVsLBQ5N3TyisQivr', private_key='6LfNEd8SAAAAAAIG55vs01zxnSnFsSgEAGtiOMF-', secure=True)
    accept_rules    = BooleanField('Ich bin weder ein Nazi noch ein sonstiger Vollidiot', [validators.Required()])
