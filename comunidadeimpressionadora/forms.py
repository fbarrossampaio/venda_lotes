from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import StringField, PasswordField, SubmitField,BooleanField,TextAreaField,RadioField,SelectField,DecimalField,HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, length,ValidationError,NumberRange,InputRequired
from comunidadeimpressionadora.models import Usuario,Tabelapreco,Lote
from flask_login import current_user
import re


def validar_cpf_cnpj(form, field):
    value = field.data

    # Remove caracteres não numéricos
    value_numeros = re.sub(r'\D', '', value)

    if len(value_numeros) == 11:  # CPF tem 11 dígitos
        if not validar_cpf(value_numeros):
            raise ValidationError('CPF inválido.')
    elif len(value_numeros) == 14:  # CNPJ tem 14 dígitos
        if not validar_cnpj(value_numeros):
            raise ValidationError('CNPJ inválido.')
    elif len(value_numeros) == 0:
        return True
    else:
        raise ValidationError('Deve ser um CPF ou CNPJ válido.')


def validar_cpf(cpf):
    # Adicione aqui a lógica de
    werrocgc = "nao"
    cf = cpf[0:9]
    print(cf)
    tam = len(cf)
    cont = tam
    vira = 1
    wtotal = 0
    while cont > 0:
        vira += 1
        corte = cf[cont - 1:cont]
        corte_num = int(corte)
        wmult = corte_num * vira
        wtotal = wtotal + wmult
        cont = cont - 1
    #cont = 0
    print(wtotal)
    wfinal = 11 - (wtotal % 11)
    wdac = str(wfinal)
    if len(wdac) > 1:
        wdac = wdac[1]
    if wfinal == 11:
        wdac = '0'
    if cpf[9:10] != wdac:
        return False
    #######################2a verificação
    cf = cpf[0:10]
    tam = len(cf)
    cont = tam
    vira = 1
    wtotal = 0
    while cont > 0:
        vira += 1
        corte = cf[cont - 1:cont]
        corte_num = int(corte)
        wmult = corte_num * vira
        wtotal = wtotal + wmult
        cont = cont - 1
    print(wtotal)
    wfinal = 11 - (wtotal % 11)
    wdac = str(wfinal)
    if len(wdac) > 1:
        wdac = wdac[1]
    if wfinal == 11:
        wdac = '0'
    if cpf[10:11] != wdac:
        return False
    return True


def validar_cnpj(cnpj):
    #cnpj = '48837314000123'
    werro = 'nao'
    wtotal = 0
    # cf = SUBS(cnpj, 1, 12)
    cf = cnpj[0:12]
    tam = len(cf)
    xcont = tam
    vira = 1
    while xcont > 0:
        if vira == 9:
            vira = 1
        vira += 1
        corte = cf[xcont - 1:xcont]
        corte_num = int(corte)
        wmult = corte_num * vira
        # wtotal = wtotal + VAL(TRAN(WMULT, "99"))
        wtotal = wtotal + wmult
        xcont = xcont - 1
    # ENDDO
    wfinal = 11 - (wtotal % 11)
    wdac = str(wfinal)
    if wfinal == 11:
        wdac = '0'
        print('1111111111')
    # ENDIF
    if len(wdac) > 1:
        wdac = wdac[1]
    if cnpj[12:13] != wdac:
        return False
    ################## 2a verif cnpj
    wtotal = 0
    cf = cnpj[0:13]
    tam = len(cf)
    xcont = tam
    vira = 1
    while xcont > 0:
        if vira == 9:
            vira = 1
        vira += 1
        corte = cf[xcont - 1:xcont]
        corte_num = int(corte)
        wmult = corte_num * vira
        # wtotal = wtotal + VAL(TRAN(WMULT, "99"))
        wtotal = wtotal + wmult
        xcont = xcont - 1
    # ENDDO
    wfinal = 11 - (wtotal % 11)
    wdac = str(wfinal)
    if wfinal == 11:
        wdac = '0'
        print('1111111111')
    if len(wdac) > 1:
        wdac = wdac[1]
        print('wdaccccc deu 2222222222')
    if cnpj[13:14] != wdac:
        return False
    return True  # Substitua pela lógica real
################fim funções cpf


class FormCriarConta(FlaskForm):
    username=StringField('Nome',validators=[DataRequired()])
    creci=StringField('Creci')
    celular_usuario = StringField('Celular')
    email=StringField('E-mail',validators=[DataRequired(),Email()])
    senha=PasswordField('Senha',validators=[DataRequired(),length(6,20)])
    confirmacao_senha=PasswordField('Confirmação senha',validators=[DataRequired(),EqualTo('senha')])
    botao_submit_criarconta=SubmitField('Criar conta')
    def validate_email(self, email):
        usuario=Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('email já cadastrado use outro email,ou faça login ')


class FormAlterarConta(FlaskForm):
    id = HiddenField()  # Campo oculto para armazenar o ID do usuário
    # empresa=StringField('empresa',validators=[DataRequired()])
    # cnpj=StringField('cnpj',validators=[DataRequired()])
    celular_usuario = StringField('Celular')
    creci=StringField('creci',validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    nova_senha = PasswordField('Nova Senha',)
    confirmacao_nova_senha = PasswordField('Confirmação Nova Senha', validators=[EqualTo('nova_senha')])
    botao_submit_alterarconta=SubmitField('alterar conta')
    def validate_nova_senha(self, nova_senha):
        if nova_senha.data and nova_senha.data.strip()!='':
            if len(nova_senha.data)<6 or len(nova_senha.data)>20:
                raise ValidationError('a senha deve ter de 6 a 20 caracteres, ou estar vazia ')

    def validate_email(self, email):
        # Obtenha o ID do usuário que está sendo alterado (se disponível)
        usuario_atual = Usuario.query.get(self.id.data)  # Assumindo que você esteja passando o ID do usuário
        # Procure por outro usuário com o mesmo e-mail, mas que não seja o usuário atual
        usuario = Usuario.query.filter(
            Usuario.email == email.data,
            Usuario.id != usuario_atual.id  # Exclui o ID do usuário atual
        ).first()
        if usuario:
            raise ValidationError('Email já cadastrado, use outro email ou faça login.')

class FormLogin(FlaskForm):
    email = StringField('email',validators=[DataRequired(),Email()])
    senha = PasswordField('senha',validators=[DataRequired(),length(6,20)])
    botao_submit_login = SubmitField('fazer login')
    lembrar_dados=BooleanField('lembrar dados')

class FormCnpjNovo(FlaskForm):
    cnpj = StringField('cnpj',validators=[DataRequired()])
    botao_submit_cnpj = SubmitField('criar conta')


ESTADOS_BRASILEIROS = [
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
    'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
    'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO',
    'ac', 'al', 'ap', 'am', 'ba', 'ce', 'df', 'es', 'go', 'ma',
    'mt', 'ms', 'mg', 'pa', 'pb', 'pr', 'pe', 'pi', 'rj', 'rn',
    'rs', 'ro', 'rr', 'sc', 'sp', 'se', 'to', ''
]


class FormVenderLote(FlaskForm):
    comprador = StringField('Comprador', id='comprador', validators=[DataRequired()])
    nacionalidade=StringField('Nacionalidade',id='nacionalidade')
    profissao=StringField('Profissão',id='profissao')
    cpf_cnpj = StringField('CPF / CNPJ', id='cpf_cnpj', validators=[DataRequired(), validar_cpf_cnpj])
    rg=StringField('RG',id='rg')
    endereco=StringField('endereco',id='endereco')
    bairro=StringField('bairro',id='bairro')
    cep=StringField('cep',id='cep')
    cidade = StringField('cidade', id='cidade')
    email_comprador=StringField('e-mail',id='email_comprador')
    #  email_comprador = StringField('E-mail', id='email_comprador', validators=[EmailOptional()])
    # email=StringField('email',id='email_comprador')
    celular=StringField('celular',id='celular')
    ############################
    uf = StringField('UF',id='uf')

    regime_casamento = SelectField('Estado Civíl/Regime de Casamento',id='regime_casamento', choices=[
         ('', 'Selecione'),
         ('1 solteiro', 'Solteiro(a)'),
         ('1 separado', 'Separado(a)'),
         ('1 divorciado', 'Divorciado(a)'),
         ('1 viuvo', 'Viúvo(a)'),
         ('2 casado(a) comunhão parcial de bens', 'Casado(a) comunhão parcial de bens'),
         ('2 casado(a) comunhão universal de bens', 'Casado(a) comunhão universal de bens'),
         ('2 casado(a) separação total de bens', 'Casado(a) separação total de bens'),
         ('2 solteiro(a) em união estável', 'Solteiro(a) em União estável'),
         ('2 separado(a) em união estável', 'Separado(a) em União estável'),
         ('2 divorciado(a) em união estável', 'Divorciado(a) em União estável'),
         ('2 viúvo(a) em união estável', 'Viúvo(a) em União estável')])
    ######################dados cônjuge
    conjuge = StringField('Cônjuge', id='conjuge')
    #cpf_cnpj_conj = StringField('Cpf Cônjuge', id='cpf_cnpj_conj')
    cpf_cnpj_conj = StringField('Cpf Cônjuge', id='cpf_cnpj_conj', validators=[validar_cpf_cnpj])
    rg_conj = StringField('Rg Cônjuge', id='rg_conj')
    email_conj = StringField('E-mail Cônjuge', id='email_conj')
    celular_conj = StringField('Celular Cônjuge', id='celular_conj')
    nacionalidade_conj = StringField('Nacionalidade Cônjuge', id='nacionalidade_conj')
    profissao_conj = StringField('Profissao Cônjuge', id='profissao_conj')

    estado_civil_conj = SelectField('Estado Civíl Conjuge (SOMENTE PARA UNIÃO ESTÁVEL)',id='estado_civil_conj', choices=[
        ('', 'Exclusivo para UNIÃO ESTÁVEL'),
        ('solteiro', 'Solteiro(a)'),
        ('separado', 'Separado(a)'),
        ('divorciado', 'Divorciado(a)'),
        ('viúvo', 'Viúvo(a)')
    ])

    #######################

    tabela_preco_radio = RadioField('Tabela de Preço',id='tabela_preco_radio', coerce=float, choices=[])  # Criação do RadioField
    botao_submit_venda= SubmitField('Incluir dados acima')

    def __init__(self, lote_id, *args, **kwargs):
        super(FormVenderLote, self).__init__(*args, **kwargs)

        # Recuperar a tabela de preços vinculada ao lote
        lote = Lote.query.get(lote_id)  # Substitua pelo método que obtém o lote correto
        if lote and lote.tabela_lote:  # Verifique se o lote tem uma tabela associada
            precos = lote.tabela_lote  # Acesse a tabela de preços
            self.tabela_preco_radio.choices = []

            # Adiciona as opções, desabilitando aquelas com valor zero ou None
            if precos.avista:
                self.tabela_preco_radio.choices.append((precos.avista, f'À vista.........{precos.avista:,.2f}'))
            if precos.em_12_pr:
                self.tabela_preco_radio.choices.append((precos.em_12_pr, f'entrada {precos.entrada:,.2f} + 12 X {precos.em_12_pr:,.2f}'))
            if precos.em_24_pr:
                self.tabela_preco_radio.choices.append((precos.em_24_pr, f'entrada {precos.entrada:,.2f} + 24 X {precos.em_24_pr:,.2f}'))
            if precos.em_36_pr:
                self.tabela_preco_radio.choices.append((precos.em_36_pr, f'entrada {precos.entrada:,.2f} + 36 X {precos.em_36_pr:,.2f}'))
            if precos.em_48_pr:
                self.tabela_preco_radio.choices.append((precos.em_48_pr, f'entrada {precos.entrada:,.2f} + 48 X {precos.em_48_pr:,.2f}'))
            if precos.em_60_pr:
                self.tabela_preco_radio.choices.append((precos.em_60_pr, f'entrada {precos.entrada:,.2f} + 60 X {precos.em_60_pr:,.2f}'))
            if precos.em_100_pr:
                self.tabela_preco_radio.choices.append((precos.em_100_pr, f'entrada {precos.entrada:,.2f} + 100 X {precos.em_100_pr:,.2f}'))
            if precos.em_120_pr:
                self.tabela_preco_radio.choices.append((precos.em_120_pr, f'entrada {precos.entrada:,.2f} + 120 X {precos.em_120_pr:,.2f}'))
    ##########voltar uf
    def validate_uf(self, campo):
        if campo.data not in ESTADOS_BRASILEIROS:
            raise ValidationError('Por favor, insira uma sigla de estado válida.')

    def validate_email_comprador(self, email_comprador):
        if email_comprador.data and not email_comprador.data.strip():
            raise ValidationError('Este campo deve ser um e-mail válido ou vazio.')
        elif email_comprador.data:
            validator = Email()
            validator(self, email_comprador)


    def validate_email_conj(self, email_conj):
        if email_conj.data and not email_conj.data.strip():
            raise ValidationError('Este campo deve ser um e-mail válido ou vazio.')
        elif email_conj.data:
            validator = Email()
            validator(self, email_conj)

class FormFiltroLote(FlaskForm):
    lista = [('Mostrar todos', 'Mostrar todos')]
    for i in range(65, 91):
        tupla = (chr(i), chr(i))
        lista.append(tupla)
    #letra = SelectField('Filtrar por Letra:', choices=[(chr(i), chr(i)) for i in range(65, 91)])  # A-Z
    letra = SelectField('Filtrar por Letra:',id='letra', choices=lista)  # A-Z
    #letra= 'combined_select'
    valor_minimo = DecimalField('Valor Mín:',id='valor_minimo', default=0) #,validators=[DataRequired(), NumberRange(min=0)])
    valor_maximo = DecimalField('Valor Máx:',id='valor_maximo', default=0) #,validators=[DataRequired(), NumberRange(min=0)])
    # RadioField para seleção da ordem
    ordem = RadioField('Filtro de Lotes:',id='ordem', choices=[
        ('lote', 'Todos os Lotes'),
        ('data_venda', 'Lotes Alterados em ordem de 1ª inclusão ')
    ])
    submit = SubmitField('Filtrar')
class FormFiltroUsuario(FlaskForm):
    filtro_nome_usuario = StringField(id='filtro_nome_usuario')

    botao_submit = SubmitField('Filtrar')
