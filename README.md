# SISTEMA DE VENDA DE LOTES

Este programa foi desenvolvido para otimizar as vendas de terrenos de um **LOTEAMENTO**, visando atender os interesses do **LOTEADOR/INCORPORADOR**.

Um dos principais desafios na venda de um loteamento é o controle do status de cada lote (se está vendido ou disponível). Isso é importante para evitar o risco de dois corretores venderem o mesmo lote.

## Cadastro de Imobiliárias
Permite que **VÁRIAS IMOBILIÁRIAS** se cadastrem e, sob a autorização do **SUPERVISOR** do sistema, façam parte do corpo de vendas desse empreendimento.

## Usuários
Os usuários são divididos em dois grupos:
- **VENDEDORES**
- **SUPERVISORES**

### VENDEDORES
Os VENDEDORES devem fazer o pré-cadastro na área de login e aguardar sua liberação feita pelos SUPERVISORES para então começar as vendas. Após a liberação, poderão ver os lotes disponíveis para venda, os lotes que venderam e alterar o seu próprio perfil.

Ao reservar um lote, o VENDEDOR informa o comprador (com nome e CPF/CNPJ) e um marcador indica o tempo (dias) que aquele lote foi reservado, facilitando o controle pelos SUPERVISORES.

### SUPERVISORES
Os SUPERVISORES têm todos os poderes dos VENDEDORES e mais. Eles podem:
- Visualizar todos os lotes disponíveis, em cadastramento, vendidos e cancelados.
- Aprovar ou desaprovar VENDEDORES.
- Classificar um usuário como SUPERVISOR e alterar cadastros de usuários (com cautela).
- Aprovar e desaprovar vendas, assegurando que todas as informações estão corretas.

### Níveis do status do lote
- **Disponível**
- **Em cadastramento:** Para fazer a reserva do lote a inclusão do **NOME e CPF/CNPJ** do comprador são suficientes. Permitindo que o vendedor tenha um tempo para completar o cadastro do comprador. 
- **Aguardando aprovação:** Uma vez preenchido o cadastro o vendedor solicita a aprovação da venda. 
- **Vendido**

**Nota de Segurança:** As credenciais padrão para usuários de teste são:
- **Supervisor**: `supervisor@gmail.com`, Senha: `123123`
- **Vendedor**: `corretor@gmail.com`, Senha: `123123`
Lembre-se de alterar as senhas padrão em ambientes de produção.

## Dependências
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Outros conforme listados em `requirements.txt`

## Instalação
Instruções sobre como instalar e rodar a aplicação localmente.

## Uso
Instruções básicas sobre como utilizar o sistema, incluindo comandos específicos e interações.

