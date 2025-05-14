from fileinput import filename

from flask import render_template,redirect,url_for,flash,request,abort,session
from comunidadeimpressionadora import app,database,bcrypt,db_uri
from comunidadeimpressionadora.forms import (FormLogin,FormVenderLote,
                                             FormFiltroLote,FormCriarConta,
                                             FormAlterarConta,FormCnpjNovo,FormFiltroUsuario)

#FormEditarPerfil,FormCriarPost
from comunidadeimpressionadora.models import Usuario,Post,Lote,Tabelapreco
from flask_login import login_user,logout_user,current_user,login_required
from datetime import datetime
import secrets
import os
from PIL import Image
import re
import requests
import json

############lista_usuarios=['lira','francisco','joao','luis','teresa']
def consulta_cnpj(cnpj):
    url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Retorna os dados da empresa
    else:
        return None  # Ou trate o erro conforme necessário
def formatar_cpf_cnpj(cpf_cnpj):
    # Remove caracteres não numéricos
    vnum = re.sub(r'\D', '', cpf_cnpj)

    if len(vnum) == 11:  # CPF
        return f"{vnum[0:3]}.{vnum[3:6]}.{vnum[6:9]}-{vnum[9:11]}"
    elif len(vnum) == 14:  # CNPJ
        return f"{vnum[0:2]}.{vnum[2:5]}.{vnum[5:8]}/{vnum[8:12]}-{vnum[12:14]}"
    else:
        return cpf_cnpj  # Retorna o original se não for CPF ou CNPJ

def verificar_dados_nao_preenchidos(lote):
    dados_nao_preenchidos = []  # Usando uma lista para armazenar campos não preenchidos
    if lote.uf is None or lote.uf.strip() == '':
        dados_nao_preenchidos.append('UF')
    if lote.rg is None or lote.rg.strip() == '':
        dados_nao_preenchidos.append('RG')
    if lote.nacionalidade is None or lote.nacionalidade.strip() == '':
        dados_nao_preenchidos.append('Nacionalidade')
    if lote.profissao is None or lote.profissao.strip() == '':
        dados_nao_preenchidos.append('Profissão')
    if lote.email_comprador is None or lote.email_comprador.strip() == '':
        dados_nao_preenchidos.append('E-mail do Comprador')
    if lote.celular is None or lote.celular.strip() == '':
        dados_nao_preenchidos.append('Celular')
    if lote.endereco is None or lote.endereco.strip() == '':
        dados_nao_preenchidos.append('Endereço')
    if lote.bairro is None or lote.bairro.strip() == '':
        dados_nao_preenchidos.append('Bairro')
    if lote.cep is None or lote.cep.strip() == '':
        dados_nao_preenchidos.append('CEP')
    if lote.cidade is None or lote.cidade.strip() == '':
        dados_nao_preenchidos.append('Cidade')

    # Se o regime de casamento é 'casado' ou 'união estável'
    if lote.regime_casamento.startswith('2'):
        if lote.conjuge is None or lote.conjuge.strip() in [None, '', 'None']:
            dados_nao_preenchidos.append('Cônjuge')
        if lote.cpf_cnpj_conj is None or lote.cpf_cnpj_conj.strip() in [None, '', 'None']:
            dados_nao_preenchidos.append('CPF do Cônjuge')
        if lote.rg_conj is None or lote.rg_conj.strip() in [None, '', 'None']:
            dados_nao_preenchidos.append('RG do Cônjuge')
        if lote.email_conj is None or lote.email_conj.strip() in [None, '', 'None']:
            dados_nao_preenchidos.append('E-mail do Cônjuge')
        if lote.celular_conj is None or lote.celular_conj.strip() in [None, '', 'None']:
            dados_nao_preenchidos.append('Celular do Cônjuge')
        if lote.nacionalidade_conj is None or lote.nacionalidade_conj.strip() in [None, '', 'None']:
            dados_nao_preenchidos.append('Nacionalidade do Cônjuge')
        if lote.profissao_conj is None or lote.profissao_conj.strip() in [None, '', 'None']:
            dados_nao_preenchidos.append('Profissão do Cônjuge')
        # Se estiver em união estável
        if 'união estável' in lote.regime_casamento:
            if lote.estado_civil_conj is None or lote.estado_civil_conj.strip() in [None, '', 'None']:
                dados_nao_preenchidos.append('Estado Civil do Cônjuge')

    return dados_nao_preenchidos

@app.route("/", methods=["GET","POST"])
@login_required
def home():
    form = FormFiltroLote()
    data_atual = datetime.now()
    if form.validate_on_submit():
        # print("passei submit")
        #letra_selecionada = form.combined_select.data
        letra_selecionada = form.letra.data

        valor_minimo = form.valor_minimo.data
        valor_maximo = form.valor_maximo.data
        # if valor_minimo is None:
        #     valor_minimo=0
        # if valor_maximo is None:
        #    valor_maximo=0
        # ##########

        # print(valor_maximo)
        ordem = form.ordem.data  # Captura a opção de ordenação

        query = Lote.query

        # Filtrar pela letra selecionada
        if letra_selecionada != 'Mostrar todos':
            query = query.filter(Lote.lote.startswith(letra_selecionada))

        # Filtrar pelo intervalo de valores
        if valor_minimo != 0 and valor_maximo != 0 :
        #if valor_minimo is not None and valor_maximo is not None:

            #query = query.filter(Lote.avista.between(valor_minimo, valor_maximo))
            query = query.join(Lote.tabela_lote).filter(Tabelapreco.avista.between(valor_minimo, valor_maximo))

        # Filtrar para incluir apenas lotes com data de venda não vazia
        if ordem == 'data_venda':
            query = query.filter(Lote.data_venda.isnot(None))  # Filtra lotes com data_venda não vazia
            query = query.order_by(Lote.data_venda.desc())  # Ordena do mais recente para o mais antigo
        else:
            query = query.filter(Lote.status != 'Cancelado')
            #lote.status == 'Cancelado'
            query = query.order_by(Lote.lote)  # Ordena por lote

        lotes = query.all()  # Execute a consulta finalizada
        lote_id_n = 0
    else:
        if not form.ordem.data:
            form.ordem.data='lote'
        # form.valor_minimo.data=0
        # form.valor_maximo.data=0
        #lotes = Lote.query.order_by(Lote.lote).all()  # Carrega todos os lotes se não houver filtro
        lotes = Lote.query.filter(Lote.status != 'Cancelado').order_by(Lote.lote).all()
        #total_100 = sum(lote.preco for lote in lotes if lote.preco is not None)
        # print("nao passei submit")
        lote_id = request.args.get('lote_id')
        lote_id_n = 0
        if lote_id is not None:
            lote_id_n = int(lote_id)

    return render_template('home.html', lotes=lotes, form=form,data_atual=data_atual,lote_id_n=lote_id_n)
@app.route("/contato")
def contato():
    return  render_template('contato.html')

@app.route("/usuarios", methods=["GET", "POST"])
@login_required
def usuarios():
    form=FormFiltroUsuario()
    if form.validate_on_submit():
        filtro_nome_usuario=form.filtro_nome_usuario.data
        usuario_id_n=0
        #usuario_id=0
        usuario_id = request.args.get('usuario_id')
        if filtro_nome_usuario:
            lista_usuarios = Usuario.query.order_by(Usuario.id.desc()).filter(
                Usuario.username.ilike(f'%{filtro_nome_usuario}%')).all()
        else:
            lista_usuarios = Usuario.query.order_by(Usuario.id.desc()).all()

    else:
        usuario_id = request.args.get('usuario_id')  # Obtém o usuario_id da query string
        #usuario_id = request.args.get('usuario_id')
        usuario_id_n=0
        if usuario_id is not None:
            usuario_id_n = int(usuario_id)

        lista_usuarios=Usuario.query.order_by(Usuario.id.desc()).all()
    return  render_template('usuarios.html',form=form, lista_usuarios=lista_usuarios,
                            usuario_id_n= usuario_id_n, usuario_id= usuario_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    form_login = FormLogin()
    form_cnpj_novo = FormCnpjNovo()
    form_criarconta = FormCriarConta()

    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha,
                                                  form_login.senha.data) and usuario.liberado_por is not None:
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f'Login ok {form_login.email.data}', 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
            if not usuario:
                flash(f'USUÁRIO INVÁLIDO {form_login.email.data}', 'alert-danger')
            elif not bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
                flash(f"Senha INVÁLIDA {form_login.email.data}", "alert-danger")
            elif usuario.liberado_por is None:
                flash(f'USUÁRIO NÃO LIBERADO, AGUARDE LIBERAÇÃO', 'alert-danger')

    # Verifique se o formulário de CNPJ foi enviado
    if form_cnpj_novo.validate_on_submit() and 'botao_submit_cnpj' in request.form:
        cnpj = form_cnpj_novo.cnpj.data
        cnpj = re.sub(r'\D', '', cnpj)
        dados_empresa = consulta_cnpj(cnpj)
        if dados_empresa and dados_empresa['status']!='ERROR':
            # print(f"Nome da empresa: {dados_empresa['nome']}")
            #print("Preparando para renderizar criarconta.html com dados:", dados_empresa)
            session['dados_empresa'] = dados_empresa
            return redirect(url_for('criarconta'))

            #return render_template('criarconta.html', dados=dados_empresa, form_criarconta=form_criarconta)
            #return redirect(url_for('criarconta', dados=dados_empresa, form_criarconta=form_criarconta))
        else:
            flash(f'CNPJ NÃO RECONHECIDO', 'alert-danger')
    return render_template('login.html', form_login=form_login, form_cnpj_novo=form_cnpj_novo,
                           form_criarconta=form_criarconta)  # Passando form_criarconta para o template


@app.route("/criarconta", methods=["GET", "POST"])
def criarconta():
    dados_empresa = session.get('dados_empresa')  # Recupera os dados da sessão, se existir
    form_criarconta = FormCriarConta()
    if form_criarconta.validate_on_submit() and 'botao_submit_criarconta'  in request.form:
        senha_cript=(bcrypt.generate_password_hash(form_criarconta.senha.data)).decode("utf-8")
        wendereco = (
            f"{dados_empresa['logradouro']}, {dados_empresa['numero']} - {dados_empresa['bairro']}, "
            f"{dados_empresa['municipio']} - {dados_empresa['uf']}, {dados_empresa['cep']}"
        )
        dados_empresa_string = json.dumps(dados_empresa, ensure_ascii=False)
        is_first_record = (Usuario.query.count() == 0)
        if is_first_record:
            usuario=Usuario(username=form_criarconta.username.data,
                            email=form_criarconta.email.data,
                            senha=senha_cript,liberado_por='supervisor',permission_level='supervisor',
                            empresa =dados_empresa['nome'],
                            cnpj = dados_empresa['cnpj'],
                            creci = form_criarconta.creci.data,
                            celular_usuario = form_criarconta.celular_usuario.data,
                            endereco_usuario = wendereco,
                            dados_receita=dados_empresa_string
                              )
                            #dados_receita = dados_empresa #database.Column(database.Text)
        else:
            usuario = Usuario(username=form_criarconta.username.data,
                              email=form_criarconta.email.data, senha=senha_cript,
                              empresa=dados_empresa['nome'],
                              cnpj=dados_empresa['cnpj'],
                              creci=form_criarconta.creci.data,
                              celular_usuario=form_criarconta.celular_usuario.data,
                              endereco_usuario=wendereco,
                              dados_receita=dados_empresa_string
                              )
        database.session.add(usuario)
        database.session.commit()
 #       login_user(usuario, remember=True)
        flash(f'conta criada {form_criarconta.email.data} aguarde a liberação para iniciar as vendas','alert-success')
        return redirect(url_for('login'))

    #return  render_template('criarconta.html',form_criarconta=form_criarconta)
    return render_template('criarconta.html', dados=dados_empresa, form_criarconta=form_criarconta)


@app.route("/alterarconta/<usuario_id>", methods=["GET", "POST"])
def alterar_conta(usuario_id):
    form_alterarconta = FormAlterarConta()
    usuario = Usuario.query.get(usuario_id)
    if usuario:
        if current_user.id == int(usuario_id) or current_user.permission_level == 'supervisor':
            if form_alterarconta.validate_on_submit():
                senha_cript =None
                if form_alterarconta.nova_senha.data and form_alterarconta.nova_senha.data.strip()!='':
                    senha_cript = (bcrypt.generate_password_hash(form_alterarconta.nova_senha.data)).decode("utf-8")
                # usuario.empresa=form_alterarconta.empresa.data
                # usuario.cnpj=form_alterarconta.cnpj.data
                usuario.celular_usuario = form_alterarconta.celular_usuario.data
                usuario.creci=form_alterarconta.creci.data
                usuario.email=form_alterarconta.email.data
                if senha_cript:
                    usuario.senha = senha_cript
                database.session.commit()
                flash(f'conta alterada ok {usuario.username} / {usuario.empresa}', 'alert-success')
                return redirect(url_for('usuarios'))
            elif request.method == 'GET':
                    #form_alterarconta.username.data=usuario.username
                    # form_alterarconta.empresa.data=usuario.empresa
                    # form_alterarconta.cnpj.data=usuario.cnpj
                    form_alterarconta.celular_usuario.data=usuario.celular_usuario
                    form_alterarconta.creci.data=usuario.creci
                    form_alterarconta.email.data = usuario.email
                    form_alterarconta.nova_senha.data=None
                    form_alterarconta.confirmacao_nova_senha.data = None

            return render_template('alterarconta.html', form_alterarconta=form_alterarconta,usuario_id=usuario.id,usuario=usuario)
        else:
            abort(403)
    else:
        flash('usuario não encontrado.', 'alert-danger')

@app.route("/alterarconta/<usuario_id>/aprovar", methods=["GET", "POST"])
@login_required
def aprovar_corretor(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if usuario and current_user.permission_level == 'supervisor':
        usuario.liberado_por = current_user.username
        usuario.permission_level = 'corretor'
        database.session.commit()
        flash(f'{usuario.username} aprovado como CORRETOR', 'alert-success')  # alterado para alert-success
        return redirect(url_for('usuarios', usuario_id=usuario.id))
    else:
        abort(403)


@app.route("/alterarconta/<usuario_id>/aprovar_supervisor", methods=["GET","POST"])
@login_required
def aprovar_supervisor(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if usuario and current_user.permission_level=='supervisor':
        # if usuario.liberado_por is None:
            usuario.liberado_por = current_user.username
            usuario.permission_level = 'supervisor'
            database.session.commit()
            flash(f'{usuario.username} aprovado como SUPERVISOR','alert-danger')
            return redirect(url_for('usuarios', usuario_id=usuario.id))
    else:
        abort(403)
@app.route("/alterarconta/<usuario_id>/desaprovar_usuario", methods=["GET","POST"])
@login_required
def desaprovar_usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if usuario and current_user.permission_level=='supervisor':
            usuario.liberado_por = None
            usuario.permission_level = 'Desaprovado'
            database.session.commit()
            flash(f'{usuario.username} desaprovado com sucesso','alert-danger')
            return redirect(url_for('usuarios', usuario_id=usuario.id))
    else:
        abort(403)


@app.route("/sair")
@login_required
def sair():
    logout_user()
    flash(f'logout feito com sucesso', 'alert-success')
    return redirect(url_for('home'))
##################criar post/perfil##################
# @app.route("/perfil")
# @login_required
# def perfil():
#     foto_perfil=url_for('static',filename='fotos_perfil/{}'.format(current_user.foto_perfil))
#     return render_template('perfil.html', foto_perfil=foto_perfil)
#
# @app.route("/post/criar", methods=["GET","POST"])
# @login_required
# def criar_post():
#     form=FormCriarPost()
#     if form.validate_on_submit():
#         post=Post(titulo=form.titulo.data,corpo=form.corpo.data,autor=current_user)
#         database.session.add(post)
#         database.session.commit()
#         flash('post criado com sucesso','alert-success')
#         return redirect(url_for('home'))
#     return render_template('criarpost.html',form=form)
#
#

# def salvar_imagem(imagem):
#     codigo=secrets.token_hex(8)
#     nome,extencao =os.path.splitext(imagem.filename)
#     nome_arquivo=nome+codigo+extencao
#     caminho_completo=os.path.join(app.root_path,'static/fotos_perfil',nome_arquivo)
#     tamanho=(200,200)
#     imagem_reduzida=Image.open(imagem)
#     imagem_reduzida.thumbnail(tamanho)
#     imagem_reduzida.save(caminho_completo)
#     return nome_arquivo
# ###########################
# def atualizar_cursos(form):
#     lista_cursos=[]
#     for campo in form:
#         if 'curso_' in campo.name:
#             if campo.data:
#                 lista_cursos.append(campo.label.text)
#     return ';'.join(lista_cursos)
#
#
# @app.route("/perfil/editar", methods=["GET","POST"])
# @login_required
# def editar_perfil():
#     form=FormEditarPerfil()
#     if form.validate_on_submit():
#         current_user.email=form.email.data
#         current_user.username=form.username.data
#         current_user.permission_level =form.permissao.data
#         if form.foto_perfil.data:
#             nome_imagem=salvar_imagem(form.foto_perfil.data)
#             current_user.foto_perfil=nome_imagem
#
#         database.session.commit()
#         flash('perfil atualizado com sucesso','alert-success')
#         return redirect(url_for('perfil'))
#     elif request.method=='GET':
#         form.email.data=current_user.email
#         form.username.data=current_user.username
#         form.permissao.data=current_user.permission_level
#         # if 'curso exel' in current_user.cursos:
#         #     form.curso_exel.data = True
#         # if 'curso vba' in current_user.cursos:
#         #     form.curso_vba.data = True
#         # if 'curso powerbi' in current_user.cursos:
#         #     form.curso_powerbi.data = True
#         # if 'curso python' in current_user.cursos:
#         #     form.curso_python.data = True
#         # if 'curso ppt' in current_user.cursos:
#         #     form.curso_ppt.data = True
#         # if 'curso SQL' in current_user.cursos:
#         #     form.curso_SQL.data = True
#     foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
#     return render_template('editarperfil.html', foto_perfil=foto_perfil,form=form)
#
# @app.route("/post/<post_id>", methods=["GET","POST"])
# @login_required
# def exibir_post(post_id):
#     post=Post.query.get(post_id)
#     if current_user==post.autor:
#         form= FormCriarPost()  # reaproveitado
#         if request.method=='GET':
#             form.titulo.data=post.titulo
#             form.corpo.data = post.corpo
#         elif form.validate_on_submit():
#             post.titulo=form.titulo.data
#             post.corpo=form.corpo.data
#             database.session.commit()
#             flash('post atualizado','alert-success')
#             return redirect(url_for('home'))
#     else:
#         form= None
#     return render_template('post.html',post=post, form=form)
#
#
# @app.route("/post/<post_id>/excluir", methods=["GET","POST"])
# @login_required
# def excluir_post(post_id):
#     post=Post.query.get(post_id)
#     if current_user==post.autor:
#         database.session.delete(post)
#         database.session.commit()
#         flash('post excluido com sucesso','alert-danger')
#         return redirect(url_for('home'))
#     else:
#         abort(403)

##################fim criar post/perfil##################
@app.route("/venderlote/<lote_id>", methods=["GET","POST"])
@login_required
def vender_lote(lote_id):
    lote=Lote.query.get(lote_id)

    if current_user==lote.autor_lote or lote.id_usuario is None or current_user.permission_level=='supervisor':
        form= FormVenderLote(lote_id=lote_id)  #o parametro (lote_id=lote_id) serve para o funcionamento do RadioField
        if request.method=='GET':
            form.comprador.data=lote.comprador
            form.cpf_cnpj.data=lote.cpf_cnpj
            form.rg.data = lote.rg
            form.nacionalidade.data = lote.nacionalidade
            form.profissao.data = lote.profissao
            form.email_comprador.data = lote.email_comprador
            form.celular.data = lote.celular
            form.endereco.data = lote.endereco
            form.bairro.data = lote.bairro
            form.cep.data = lote.cep
            form.cidade.data = lote.cidade
            form.uf.data = lote.uf
            ########### if not form.tabela_preco_radio.data:
            if lote.entrada:
                if lote.prestacao:
                    form.tabela_preco_radio.data=lote.prestacao
                else:
                    form.tabela_preco_radio.data = lote.entrada

            if lote.regime_casamento:
                form.regime_casamento.data = lote.regime_casamento
            else:
                form.regime_casamento.data =''

            if lote.conjuge is None:
                form.conjuge.data =''
            else:
                form.conjuge.data = lote.conjuge

            if lote.cpf_cnpj_conj is None:
                form.cpf_cnpj_conj.data=''
            else:
                form.cpf_cnpj_conj.data=lote.cpf_cnpj_conj

            if lote.rg_conj is None:
                form.rg_conj.data = ''
            else:
                form.rg_conj.data = lote.rg_conj

            if lote.email_conj is None:
                form.email_conj.data = ''
            else:
                form.email_conj.data = lote.email_conj

            if lote.celular_conj is None:
                form.celular_conj.data = ''
            else:
                form.celular_conj.data = lote.celular_conj

            if lote.nacionalidade_conj is None:
                form.nacionalidade_conj.data = ''
            else:
                form.nacionalidade_conj.data = lote.nacionalidade_conj

            if lote.profissao_conj is None:
                form.profissao_conj.data = ''
            else:
                form.profissao_conj.data = lote.profissao_conj

            if lote.estado_civil_conj is None:
                form.estado_civil_conj.data = ''
            else:
                form.estado_civil_conj.data = lote.estado_civil_conj

        elif form.validate_on_submit():
             if current_user == lote.autor_lote :
                 wmensagem=f'lote {lote.lote} alterado pelo vendedor '
             elif lote.id_usuario == None :
                 wmensagem=f'lote {lote.lote} reservado '
                 # 1a vez lote.id_usuario == None:
             elif current_user.permission_level == 'supervisor':
                 wmensagem=f'lote {lote.lote} alterado por supervisor '
             else:
                 wmensagem=f'lote {lote.lote} reservado opção desconhecida'
             if lote.comprador== None:
                 lote.id_usuario = current_user.id
                 lote.data_venda = datetime.now()
                 lote.status = 'Em cadastramento'
             lote.comprador = form.comprador.data
             lote.uf=form.uf.data.upper()
             lote.regime_casamento=form.regime_casamento.data
             lote.rg=form.rg.data
             lote.nacionalidade=form.nacionalidade.data
             lote.profissao=form.profissao.data
             lote.email_comprador=form.email_comprador.data
             lote.celular=form.celular.data
             lote.endereco=form.endereco.data
             lote.bairro=form.bairro.data
             lote.cep=form.cep.data
             lote.cidade=form.cidade.data
             # distrinchanco os valores selecionados no tabela_preco_radio
             valor_selecionado = form.tabela_preco_radio.data
             descricao_selecionada = None
             num_opcao_preco_radio=0
             for value, description in form.tabela_preco_radio.choices:
                 num_opcao_preco_radio+=1
                 if value == valor_selecionado:
                     descricao_selecionada = description
                     break
             if num_opcao_preco_radio==1:
                 valor_entrada=lote.tabela_lote.avista
                 valor_prest=0
                 wvezes_prest = 0
             else:
                 valor_entrada=lote.tabela_lote.entrada
                 valor_prest=valor_selecionado
                 if num_opcao_preco_radio == 2:
                     wvezes_prest=12
                 elif num_opcao_preco_radio == 3:
                     wvezes_prest=24
                 elif num_opcao_preco_radio == 4:
                     wvezes_prest=36
                 elif num_opcao_preco_radio == 5:
                     wvezes_prest=48
                 elif num_opcao_preco_radio == 6:
                     wvezes_prest=60
                 elif num_opcao_preco_radio == 7:
                     wvezes_prest=100
                 elif num_opcao_preco_radio == 8:
                     wvezes_prest=120
             lote.prestacao_vezes=wvezes_prest
             lote.entrada=valor_entrada
             lote.prestacao=valor_prest
             #fim distrinchanco os valores selecionados no tabela_preco_radio
             # print(f'valor vezes_prest gravar{wvezes_prest}')
             # print(f'valor entrada para gravar{valor_entrada}')
             # print(f'valor prest para gravar{valor_prest}')
             # # Agora você pode usar 'valor_selecionado' como necessário
             # print(f'Valor selecionado: {valor_selecionado}')
             # print(f'Opção selecionada: {descricao_selecionada}')
             # print(f'Numero da opção: {num_opcao_preco_radio}')
             cpf_cnpj = form.cpf_cnpj.data
             lote.cpf_cnpj = formatar_cpf_cnpj(cpf_cnpj)  # Chamando a função de formatação
             #database.session.commit()
             if lote.regime_casamento=='aaasolteiro':
                 database.session.commit()
                 flash(wmensagem, 'alert-success')
                 return redirect(url_for('home', lote_id=lote.id))
             else:
                 lote.conjuge=form.conjuge.data
                 cpf_cnpj = form.cpf_cnpj_conj.data
                 lote.cpf_cnpj_conj = formatar_cpf_cnpj(cpf_cnpj)
                 lote.rg_conj = form.rg_conj.data
                 lote.email_conj = form.email_conj.data
                 lote.celular_conj = form.celular_conj.data
                 lote.nacionalidade_conj=form.nacionalidade_conj.data
                 lote.profissao_conj=form.profissao_conj.data
                 lote.estado_civil_conj=form.estado_civil_conj.data
                 database.session.commit()

                 flash(wmensagem, 'alert-success')
                 return redirect(url_for('home', lote_id=lote.id))

    else:
        abort(403)
    return render_template('venderlote.html',lote_id=lote.id,
                           form=form,lote=lote)

@app.route("/venderlote/<lote_id>/aprovar", methods=["GET","POST"])
@login_required
def aprovar_venda(lote_id):
    lote=Lote.query.get(lote_id)
    if current_user.permission_level=='supervisor':
        #current_user==lote.autor_lote or
        lote.data_aprovacao = datetime.now()
        lote.status='Vendido'
        database.session.commit()
        flash(f'lote {lote.lote} aprovado com sucesso','alert-danger')
        return redirect(url_for('home', lote_id=lote.id))

    else:
        abort(403)

@app.route("/venderlote/<lote_id>/solicitar_aprovacao", methods=["GET", "POST"])
@login_required
def solicitar_aprovacao(lote_id):
    lote = Lote.query.get(lote_id)
    if lote:
        campos_faltando= verificar_dados_nao_preenchidos(lote)  # Salva o resultado da função
        if campos_faltando:  # Substitua `dados_nao_preenchidos` por `campos_faltando`
            complemento_dados_n_p = f'Dados incompletos: {", ".join(campos_faltando)}'

        if current_user.permission_level == 'supervisor' or current_user==lote.autor_lote:
            # lote.data_solicitacao_aprov = datetime.now()
            lote.status = 'Aguardando aprovação'
            database.session.commit()
            flash(f'Solicitação de aprovação enviada {lote.lote} {complemento_dados_n_p}', 'alert-danger')
            return redirect(url_for('home', lote_id=lote.id))
        else:
            abort(403)



@app.route("/venderlote/<lote_id>/exportar", methods=["GET", "POST"])
@login_required
def exportar_lote_para_txt(lote_id):
    lote = Lote.query.get(lote_id)  # Busca o lote pelo ID
    if lote:
        lista_cabecalho=['id',
        'lote',
        'status',
        'data_venda',
        'data_aprovacao',
        'area',
        'tabela_preco',
        'entrada',
        'entrada_vezes',
        'prestacao',
        'prestacao_vezes',
        'comprador',
        'nacionalidade',
        'profissao',
        'cpf_cnpj',
        'rg',
        'email_comprador',
        'celular',
        'endereco',
        'cidade',
        'uf',
        'bairro',
        'cep',
        'regime_casamento',
        'conjuge',
        'cpf_cnpj_conj',
        'rg_conj',
        'nacionalidade_conj',
        'profissao_conj',
        'estado_civil_conj',
        'email_conj',
        'celular_conj',
        'id_usuario',
        'id_tabela']

        lista_dados = [
            str(lote.id),
            lote.lote,
            lote.status,
            lote.data_venda.strftime('%d/%m/%Y') if lote.data_venda else '',
            lote.data_aprovacao.strftime('%d/%m/%Y') if lote.data_aprovacao else '',
            str(lote.area),
            lote.tabela_preco,
            str(lote.entrada),
            str(lote.entrada_vezes),
            str(lote.prestacao),
            str(lote.prestacao_vezes),
            lote.comprador,
            lote.nacionalidade,
            lote.profissao,
            lote.cpf_cnpj,
            lote.rg,
            lote.email_comprador,
            lote.celular,
            lote.endereco,
            lote.cidade,
            lote.uf,
            lote.bairro,
            lote.cep,
            lote.regime_casamento,
            lote.conjuge,
            lote.cpf_cnpj_conj,
            lote.rg_conj,
            lote.nacionalidade_conj,
            lote.profissao_conj,
            lote.estado_civil_conj,
            lote.email_conj,
            lote.celular_conj,
            str(lote.id_usuario),
            str(lote.id_tabela)
        ]
        dados_cabecalho='; '.join(lista_cabecalho)+ '\n'
        dados_lote = '; '.join(lista_dados) + '\n'
        dados_lote=dados_cabecalho+dados_lote
        try:
            # Obter o nome do usuário atual
            nome_usuario = os.getlogin()

            # Construir o caminho para a pasta de Downloads
            caminho_downloads = f'C:\\Users\\{nome_usuario}\\Downloads\\lote {lote.lote} exportado.txt'
            with open(caminho_downloads, 'w') as arquivo:
                arquivo.write(dados_lote)

            flash(f'Dados lote {lote.lote} exportados com sucesso!', 'alert-success')
        except PermissionError:
            #print("Erro: O arquivo está em uso. Feche o arquivo e tente novamente.")
            flash('Erro: O arquivo está em uso. Feche o arquivo e tente novamente.', 'alert-danger')
            return redirect(url_for('home'))

        return redirect(url_for('home'))
    else:

        flash('Lote não encontrado.', 'alert-danger')

@app.route('/imprimir_dados/<int:lote_id>', methods=['GET'])
def imprimir_dados(lote_id):
    # Buscar o lote pelo ID
    lote = Lote.query.get(lote_id)
    if lote is None:
        flash('Lote não encontrado.', 'alert-danger')
        return redirect(url_for('home'))  # Redireciona para a página inicial ou outra página

    # Renderiza o template de impressão com os dados do lote
    return render_template('imprimir_dados.html', lote=lote)


@app.route('/imprimir_dados_lgpd/<int:lote_id>', methods=['GET'])
def imprimir_dados_lgpd(lote_id):
    # Buscar o lote pelo ID
    lote = Lote.query.get(lote_id)
    if lote is None:
        flash('Lote não encontrado.', 'alert-danger')
        return redirect(url_for('home'))  # Redireciona para a página inicial ou outra página

    # Renderiza o template de impressão com os dados do lote
    return render_template('imprimir_lgpd.html', lote=lote)

################################
@app.route("/venderlote/<lote_id>/cancelarvenda", methods=["GET", "POST"])
@login_required
def cancelar_venda(lote_id):
    lote = Lote.query.get(lote_id)
    if lote:
        if current_user.permission_level == 'supervisor' or current_user==lote.autor_lote:
            # Guarda os dados do lote a ser cancelado
            dados_cancelados = {
                'lote': lote.lote,
                'data_venda': lote.data_venda,
                'data_aprovacao': lote.data_aprovacao,
                'area': lote.area,
                'tabela_preco': lote.tabela_preco,
                'entrada': lote.entrada,
                'entrada_vezes': lote.entrada_vezes,
                'prestacao': lote.prestacao,
                'prestacao_vezes': lote.prestacao_vezes,
                'comprador': lote.comprador,
                'nacionalidade': lote.nacionalidade,
                'profissao': lote.profissao,
                'cpf_cnpj': lote.cpf_cnpj,
                'rg': lote.rg,
                'email_comprador': lote.email_comprador,
                'celular': lote.celular,
                'endereco': lote.endereco,
                'cidade': lote.cidade,
                'uf': lote.uf,
                'bairro': lote.bairro,
                'cep': lote.cep,
                'regime_casamento': lote.regime_casamento,
                'conjuge': lote.conjuge,
                'cpf_cnpj_conj': lote.cpf_cnpj_conj,
                'rg_conj': lote.rg_conj,
                'email_conj': lote.email_conj,
                'celular_conj': lote.celular_conj,
                'id_usuario': lote.id_usuario,
                'id_tabela': lote.id_tabela,
            }

            # Limpa os dados do lote
            id_registro_lote=lote.id
            lote.status = 'Disponivel'
            lote.data_venda = None
            lote.data_aprovacao = None
            lote.entrada = None
            lote.entrada_vezes = None
            lote.prestacao = None
            lote.prestacao_vezes = None
            lote.comprador = None
            lote.nacionalidade = None
            lote.profissao = None
            lote.cpf_cnpj = None
            lote.rg = None
            lote.email_comprador = None
            lote.celular = None
            lote.endereco = None
            lote.cidade = None
            lote.uf = None
            lote.bairro = None
            lote.cep = None
            lote.regime_casamento = None
            lote.conjuge = None
            lote.cpf_cnpj_conj = None
            lote.rg_conj = None
            lote.email_conj = None
            lote.celular_conj = None
            lote.id_usuario = None
            database.session.commit()

            # Salva os dados da venda cancelada
            novo_lote_cancelado = Lote(
                lote=dados_cancelados['lote'],
                status='Cancelado',
                data_venda=dados_cancelados['data_venda'],
                data_aprovacao=dados_cancelados['data_aprovacao'],
                area=dados_cancelados['area'],
                tabela_preco=dados_cancelados['tabela_preco'],
                entrada=dados_cancelados['entrada'],
                entrada_vezes=dados_cancelados['entrada_vezes'],
                prestacao=dados_cancelados['prestacao'],
                prestacao_vezes=dados_cancelados['prestacao_vezes'],
                comprador=dados_cancelados['comprador'],
                nacionalidade=dados_cancelados['nacionalidade'],
                profissao=dados_cancelados['profissao'],
                cpf_cnpj=dados_cancelados['cpf_cnpj'],
                rg=dados_cancelados['rg'],
                email_comprador=dados_cancelados['email_comprador'],
                celular=dados_cancelados['celular'],
                endereco=dados_cancelados['endereco'],
                cidade=dados_cancelados['cidade'],
                uf=dados_cancelados['uf'],
                bairro=dados_cancelados['bairro'],
                cep=dados_cancelados['cep'],
                regime_casamento=dados_cancelados['regime_casamento'],
                conjuge=dados_cancelados['conjuge'],
                cpf_cnpj_conj=dados_cancelados['cpf_cnpj_conj'],
                rg_conj=dados_cancelados['rg_conj'],
                email_conj=dados_cancelados['email_conj'],
                celular_conj=dados_cancelados['celular_conj'],
                id_usuario=dados_cancelados['id_usuario'],
                id_tabela=dados_cancelados['id_tabela']
            )
            database.session.add(novo_lote_cancelado)
            database.session.commit()
            flash(f'Venda {lote.lote} Cancelada com sucesso', 'alert-danger')
            return redirect(url_for('home', lote_id=id_registro_lote))
        else:
            abort(403)
    else:
        flash('Lote não encontrado', 'alert-danger')

# @app.route('/show_db_uri')
# def show_db_uri():
#     return f'DATABASE_URL: {db_uri}'
# @app.route('/show_db_uri')
# def show_db_uri():
#     return render_template('show_db_uri.html', db_uri=db_uri)
