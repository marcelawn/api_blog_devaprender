from flask import Flask,jsonify,request,make_response
from estrutura_banco_de_dados import Autor,Postagem,app,db
import jwt
import json
from functools import wraps
from datetime import datetime,timedelta,timezone

# Criando a condição de token obrigatorio
def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = None
        # Verificar se um token foi enviado
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'mensagem':'Token não foi incluído!'},401)
        # Se temos um token, validar o acesso consultando o banco de dados
        try:
            resultado = jwt.decode(token,app.config['SECRET_KEY'],algorithms=["HS256"])
            autor = Autor.query.filter_by(id_autor=resultado['id_autor']).first()
        except:
            return jsonify({'mensagem':'Token é inválido'},401)
        return f(autor,*args,**kwargs)
    return decorated



# Criando uma rota de login
@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Login inválido',401,{'WWW-Authenticate':'Basic realm="Login obrigatório"'})
    usuario = Autor.query.filter_by(nome=auth.username).first()
    if not usuario:
        return make_response('Login inválido',401,{'WWW-Authenticate':'Basic realm="Login obrigatório"'})
    if auth.password == usuario.senha:
        token = jwt.encode({'id_autor': usuario.id_autor,'exp': datetime.now(timezone.utc) + timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    return make_response('Login inválido',401,{'WWW-Authenticate':'Basic realm="Login obrigatório"'})
    
@app.route('/autores') 
@token_obrigatorio
def obter_autores(autor):
   autores =  Autor.query.all()
   lista_de_autores = []
   for autor in autores:
        autor_atual = {}
        autor_atual['id_autor'] = autor.id_autor
        autor_atual['nome'] = autor.nome
        autor_atual['email'] = autor.email
        lista_de_autores.append(autor_atual)

   return jsonify({'autores':lista_de_autores})


@app.route('/autores/<int:id_autor>',methods=['GET'])
@token_obrigatorio
def obter_autores_com_id(autor,id_autor):
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify(f'Autor não encontrado!')
    autor_atual = {}
    autor_atual['id_autor'] = autor.id_autor
    autor_atual['nome'] = autor.nome
    autor_atual['email'] = autor.email

    return jsonify(f'Você buscou pelo autor: {autor_atual}')
    # para formatar corretamente
    ## return jsonify({'autor': autor_atual})
    

@app.route('/autores',methods=['POST'])
@token_obrigatorio
def novo_autor(autor):
    novo_autor = request.get_json()
    autor = Autor(nome=novo_autor['nome'],senha=novo_autor['senha'],email=novo_autor['email'])

    db.session.add(autor)
    db.session.commit()

    return jsonify({'mensagem': 'Usuário criado com sucesso!'},200)

@app.route('/autores/<int:id_autor>',methods=['PUT'])
@token_obrigatorio
def alterar_autor(autor,id_autor):
    usuario_a_alterar = request.get_json()
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify({'mensagem':'Usuário não encontrado!'},404)
    try:
        if usuario_a_alterar['nome']:
            autor.nome = usuario_a_alterar['nome']
    except:
        pass
    try:
        if usuario_a_alterar['email']:
            autor.email = usuario_a_alterar['email']
    except:
        pass
    try:
        if usuario_a_alterar['senha']:
            autor.senha = usuario_a_alterar['senha']
    except:
        pass
    
    db.session.commit()
    return jsonify({'mensagem': 'Usuário alterado com sucesso!'},200)
    

@app.route('/autores/<int:id_autor>',methods=['DELETE'])
@token_obrigatorio
def excluir_autor(autor,id_autor):
    autor_existente = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor_existente:
        return jsonify({'mensagem': 'Este autor não foi encontrado!'})
    db.session.delete(autor_existente)
    db.session.commit()
    return jsonify({'mensagem': 'Autor excluído com sucesso!'})

# Obter postagem por id - GET https://localhost:5000/postagem/1


@app.route('/postagem/<int:id_postagem>', methods=['GET'])
@token_obrigatorio
def obter_postagem_por_indice(autor, id_postagem):
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    postagem_atual = {}
    try:
        postagem_atual['titulo'] = postagem.titulo
    except:
        pass
    postagem_atual['id_autor'] = postagem.id_autor

    return jsonify({'postagens': postagem_atual})

# Criar uma nova postagem - POST https://localhost:5000/postagem


@app.route('/postagem', methods=['POST'])
@token_obrigatorio
def nova_postagem(autor):
    nova_postagem = request.get_json()
    postagem = Postagem(
        titulo=nova_postagem['titulo'], id_autor=nova_postagem['id_autor'])

    db.session.add(postagem)
    db.session.commit()

    return jsonify({'mensagem': 'Postagem criada com sucesso'})

# Alterar uma postagem existente - PUT https://localhost:5000/postagem/1


@app.route('/postagem/<int:id_postagem>', methods=['PUT'])
@token_obrigatorio
def alterar_postagem(autor, id_postagem):
    postagem_alterada = request.get_json()
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    try:
        postagem.titulo = postagem_alterada['titulo']
    except:
        pass
    try:
        postagem.id_autor = postagem_alterada['id_autor']
    except:
        pass

    db.session.commit()
    return jsonify({'mensagem': 'Postagem alterada com sucessso'})

# Excluir uma postagem - DELETE - https://localhost:5000/postagem/1


@app.route('/postagem/<int:id_postagem>', methods=['DELETE'])
@token_obrigatorio
def excluir_postagem(autor, id_postagem):
    postagem_a_ser_excluida = Postagem.query.filter_by(
        id_postagem=id_postagem).first()
    if not postagem_a_ser_excluida:
        return jsonify({'mensagem': 'Não foi encontrado uma postagem com este id'})
    db.session.delete(postagem_a_ser_excluida)
    db.session.commit()

    return jsonify({'mensagem': 'Postagem excluída com sucesso!'})




app.run(port=5000,host='localhost',debug=True)

