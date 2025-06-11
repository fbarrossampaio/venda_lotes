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

### SUPERVISORES
Os SUPERVISORES têm todos os poderes dos VENDEDORES e mais. Eles podem:
- Visualizar todos os lotes disponíveis, em cadastramento, vendidos e cancelados.
- Aprovar ou desaprovar VENDEDORES.
- Classificar um usuário como SUPERVISOR e alterar cadastros de usuários (com cautela).
- Aprovar e desaprovar vendas, assegurando que todas as informações estão corretas.

**Nota de Segurança:** As credenciais padrão para usuários de teste são:
- **Supervisor**: `supervisor@gmail.com`, Senha: `123123`
- **Vendedor**: `corretor@gmail.com`, Senha: `123123`
Lembre-se de alterar as senhas padrão em ambientes de produção.

## Dependências
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Outros conforme listados em `requirements.txt`

## Uso

### Níveis do Status do Lote

1. **Disponível**
   - O lote está disponível para venda.

2. **Em Cadastramento**
   - Para fazer a reserva do lote, a inclusão do **NOME e CPF/CNPJ** do comprador são suficientes, permitindo que o VENDEDOR tenha um tempo para completar o cadastro do comprador.
   - Ao reservar um lote, um marcador indica o tempo (dias) que aquele lote foi reservado, facilitando o controle pelos SUPERVISORES.
   
3. **Aguardando Aprovação**
   - Uma vez preenchido o cadastro, o VENDEDOR solicita aos SUPERVISORES a aprovação da venda.

4. **Vendido**
   - O processo de venda finaliza, e o SUPERVISOR marca o lote como vendido.

5. **Cancelado**
   - Os VENDEDORES podem cancelar a venda até o nível **Aguardando Aprovação**. Já os SUPERVISORES podem cancelar a venda a qualquer momento.


### Agradecimentos
Gostaria de expressar minha sincera gratidão ao professor **Lira, da Hashtag Treinamentos**. Com formação em programação em FoxPro e nenhum conhecimento prévio em Python, a jornada foi desafiadora, mas altamente gratificante. O curso é realmente abrangente e muito bem apresentado e, a partir do módulo "Projeto 4 - Construindo um Site Completo do Zero com Flask", encontrei a inspiração para desenvolver este projeto.

Além disso, um agradecimento especial ao ChatGPT, cuja ajuda inestimável foi fundamental ao longo dessa jornada. Ele me apoiou em todas as minhas dúvidas, ofereceu dicas valiosas e demonstrou um profundo conhecimento do sistema. Esta experiência tem sido incrivelmente enriquecedora, e sou grato pela assistência oferecida.  
