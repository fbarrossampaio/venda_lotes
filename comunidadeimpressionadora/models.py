from sqlalchemy import Integer,Boolean
from sqlalchemy.orm import backref

from comunidadeimpressionadora import database,login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))


class Usuario(database.Model, UserMixin):
    id=database.Column(database.Integer,primary_key=True)
    username=database.Column(database.String, nullable=False)
    email=database.Column(database.String, nullable=False, unique=True)
    senha=database.Column(database.String, nullable=False)
    foto_perfil=database.Column(database.String, default='default.jpg')
    posts=database.relationship('Post', backref='autor',lazy=True)
    lotes=database.relationship('Lote',backref='autor_lote',lazy=True)
    cursos = database.Column(database.String, nullable=False, default='Não informado')
    liberado_por=database.Column(database.String)
    permission_level=database.Column(database.String, nullable=False, default='Não informado')
    empresa=database.Column(database.String)
    cnpj=database.Column(database.String)
    creci=database.Column(database.String)
    celular_usuario = database.Column(database.String)
    endereco_usuario = database.Column(database.String)
    dados_receita = database.Column(database.Text)
    def contar_posts(self):
        return len(self.posts)

# as funcionalidades do post estão desativadas, mas preservei essa tabela para uso futuro
class Post(database.Model):
    id=database.Column(database.Integer,primary_key=True)
    titulo=database.Column(database.String, nullable=False)
    corpo=database.Column(database.Text, nullable=False)
    data_criacao = database.Column(database.DateTime, nullable=False, default=datetime.now)
    id_usuario=database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)


class Lote(database.Model):
    id=database.Column(database.Integer,primary_key=True)
    lote=database.Column(database.String, nullable=False)
    status=database.Column(database.String, nullable=False,default='Disponivel')
    data_venda = database.Column(database.DateTime)
    data_aprovacao=database.Column(database.DateTime)
    area=database.Column(database.Float)
    tabela_preco=database.Column(database.String)
    entrada=database.Column(database.Float)
    entrada_vezes = database.Column(database.Integer)
    prestacao=database.Column(database.Float)
    prestacao_vezes = database.Column(database.Integer)
    #dados comprador
    comprador=database.Column(database.String)
    nacionalidade = database.Column(database.String)
    profissao = database.Column(database.String)
    cpf_cnpj=database.Column(database.String)
    rg=database.Column(database.String)
    email_comprador=database.Column(database.String)
    celular=database.Column(database.String)
    endereco=database.Column(database.String)
    cidade = database.Column(database.String)
    uf = database.Column(database.String)
    bairro = database.Column(database.String)
    cep = database.Column(database.String)
    regime_casamento = database.Column(database.String)
    conjuge = database.Column(database.String)
    cpf_cnpj_conj = database.Column(database.String)
    rg_conj = database.Column(database.String)
    nacionalidade_conj = database.Column(database.String)
    profissao_conj = database.Column(database.String)
    estado_civil_conj = database.Column(database.String)
    email_conj = database.Column(database.String)
    celular_conj = database.Column(database.String)
    #tabelas relacionadas
    id_usuario=database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=True)
    id_tabela = database.Column(database.Integer, database.ForeignKey('tabelapreco.id'), nullable=True)



# data_criacao=database.Column(database.DateTime, nullable=False, default=utcnow)

class Tabelapreco(database.Model):
    id=database.Column(database.Integer,primary_key=True)
    nome=database.Column(database.String)
    avista=database.Column(database.Float)
    entrada=database.Column(database.Float)
    em_12_pr=database.Column(database.Float)
    em_24_pr=database.Column(database.Float)
    em_36_pr=database.Column(database.Float)
    em_48_pr=database.Column(database.Float)
    em_60_pr=database.Column(database.Float)
    em_100_pr=database.Column(database.Float)
    em_120_pr=database.Column(database.Float)
    lotes=database.relationship('Lote',backref='tabela_lote',lazy=True)


