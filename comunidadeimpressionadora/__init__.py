from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os
import sqlalchemy
from sqlalchemy.testing.plugin.plugin_base import engines

app = Flask(__name__)

# lista_usuarios=['lira','francisco','joao','luis','teresa']

app.config['SECRET_KEY'] = '889a05f99d8db7daebb469834cab3130'
# if os.getenv("DATABASE_URL"):
#     app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
#     db_uri = os.getenv("DATABASE_URL")
# else:
#     app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///comunidade.db'
#     db_uri = "sqlite:///comunidade.db"

db_uri = os.getenv("DATABASE_URL", "sqlite:///comunidade.db")
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
print("DATABASE_URL:", os.getenv("DATABASE_URL"))
database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

login_manager.login_view = 'login'  # se o usuário não estiver logado ele direciona para esta FUNÇÂO
login_manager.login_message_category = 'alert-info'

# if os.getenv("DATABASE_URL"):
from comunidadeimpressionadora import models
from comunidadeimpressionadora.models import Usuario, Lote, Tabelapreco
import pandas as pd

engine = sqlalchemy.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
inspector = sqlalchemy.inspect(engine)
if not inspector.has_table('usuario') and not db_uri == "sqlite:///comunidade.db":
    print('not inspector.has_table(usuari) and not db_uri == sqlite:///comunidade.db:')
    with app.app_context():
        # database.drop_all()
        database.create_all()
        database.session.commit()
    # with app.app_context():
    #     senha_cript = (bcrypt.generate_password_hash('123123'))
    #     usuario = Usuario(username='supervisor', email='corretor@gmail.com', senha=senha_cript,liberado_por='supervisor',permission_level='supervisor')
    #     database.session.add(usuario)
    #     database.session.commit()
    try:
        tabela_df = pd.read_csv('tabela.csv', sep=';')
        with app.app_context():
            for index, row in tabela_df.iterrows():
                nova_tab = Tabelapreco(
                    nome=row['nome'],
                    avista=row['avista'],
                    entrada=row['entrada'],
                    em_12_pr=row['em_12_pr'],
                    em_24_pr=row['em_24_pr'],
                    em_36_pr=row['em_36_pr'],
                    em_48_pr=row['em_48_pr'],
                    em_60_pr=row['em_60_pr'],
                    em_100_pr=row['em_100_pr'],
                    em_120_pr=row['em_120_pr']
                )
                database.session.add(nova_tab)
            database.session.commit()
    except Exception as e:
        print(f"Erro ao inserir dados na tabela Tabelapreco: {e}")
    try:
        lotes_df = pd.read_csv('lotes2.csv', sep=';')
        with app.app_context():
            for index, row in lotes_df.iterrows():
                id_tabela = row['id_tabela']  # Captura o id_tabela da linha atual
                tabela_existente = Tabelapreco.query.get(id_tabela)  # Verifica se o id_tabela existe

                if tabela_existente:  # Somente insere se o id_tabela existir na tabela Tabelapreco
                    novo_lote = Lote(
                        lote=row['lote'],
                        status=row['status'],
                        area=row['area'],
                        tabela_preco=row['tabela_preco'],
                        id_tabela=id_tabela  # Usa o id_tabela verificado
                    )
                    database.session.add(novo_lote)
                else:
                    print(f"Erro: id_tabela {id_tabela} não encontrado na tabela Tabelapreco.")

            database.session.commit()
    except Exception as e:
        print(f"Erro ao inserir dados na tabela Lote: {e}")

    # lotes_df = pd.read_csv('lotes2.csv', sep=';')
    # with app.app_context():
    #     for index, row in lotes_df.iterrows():
    #         novo_lote = Lote(
    #             lote=row['lote'],
    #             status=row['status'],
    #             area=row['area'],
    #             tabela_preco=row['tabela_preco'],
    #             id_tabela=row['id_tabela']
    #         )
    #         database.session.add(novo_lote)

    #     database.session.commit()

    # ##########################################################
    # tabela_df = pd.read_csv('tabela.csv', sep=';')
    # with app.app_context():
    #     for index, row in tabela_df.iterrows():
    #         nova_tab = Tabelapreco(
    #         nome=row['nome'],
    #         avista=row['avista'],
    #         entrada=row['entrada'],
    #         em_12_pr=row['em_12_pr'],
    #         em_24_pr=row['em_24_pr'],
    #         em_36_pr=row['em_36_pr'],
    #         em_48_pr=row['em_48_pr'],
    #         em_60_pr=row['em_60_pr'],
    #         em_100_pr=row['em_100_pr'],
    #         em_120_pr=row['em_120_pr']
    #         )
    #         database.session.add(nova_tab)
    #     database.session.commit()

from comunidadeimpressionadora import routes