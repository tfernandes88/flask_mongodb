from flask import Flask
from flask import render_template
from flask import request
from flask import redirect 
from flask import url_for
from flask import flash
from flask import jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from pymongo import MongoClient
from bson.objectid import ObjectId

"""
Inicia a aplicação Flask
"""

app = Flask(__name__)
app.secret_key = '12345'

'''
# MongoDB Connection
// criei um container para realização dos testes.
'''
client = MongoClient('mongodb://localhost:27017/')
db = client.flask_mongo_crud
collection = db.livros

'''
# WTForms para adicionar / atualizar
'''

class ItemForm(FlaskForm):
    nomeLivro = StringField('Nome', validators=[DataRequired()])
    catLivro = StringField('Categoria', validators=[DataRequired()])
    autorLivro = StringField('Autor', validators=[DataRequired()])
    anoLivro = StringField('Ano', validators=[DataRequired()])
    submit = SubmitField('Save')
    
'''
# Rota principal
'''

@app.route('/')
def index():
    livros = collection.find()
    return render_template('index.html', livros=livros)

'''
# Rota para adicionar um livro
'''

@app.route('/add', methods=['GET','POST'])
def add():
    form = ItemForm()
    if form.validate_on_submit():
        data = {
            'nomeLivro': form.nomeLivro.data,
            'catLivro': form.catLivro.data,
            'autorLivro': form.autorLivro.data,
            'anoLivro': form.anoLivro.data
        }
        collection.insert_one(data)
        flash('O livro foi adicionado com sucesso!', 'success')
        return redirect(url_for('index'))
    return render_template('add_update.html', form=form, title='Adicionar Livro')

'''
# Rota para adicionar um livro
'''

@app.route('/update/<livro_id>', methods=['GET','POST'])
def update(livro_id):
    livro = collection.find_one({'_id': ObjectId(livro_id)})
    if not livro:
        flash('Livro não foi encontrado', 'danger')
        return redirect(url_for('index'))
    
    form = ItemForm(data=livro)
    if form.validate_on_submit():
        collection.update_one(
            {'_id': ObjectId(livro_id)},
            {'$set': {
                    'nomeLivro': form.nomeLivro.data,
                    'catLivro': form.catLivro.data,
                    'autorLivro': form.autorLivro.data,
                    'anoLivro': form.nomeLivro.data}}
        )
        flash('Livro foi atualizado com sucesso.', 'success')
        return redirect(url_for('index'))
    return render_template('add_update.html', form=form, title='Update Livro')

'''
# Rota para visualizar o livro_id
'''

@app.get('/view/<livro_id>/')
def view(livro_id):
    query={
        '_id': ObjectId(livro_id)
    }
    livro = collection.find_one(query)
    
    if not livro:
        return jsonify({
            'message':'Livro não foi encontrado'
        }), 404
    # Convertendo ObjectId e retornando os dados do livro
    livro['_id'] = str(livro['_id'])
    return jsonify({
        'data':livro
    }), 200

'''
# Rota para atualizar via API.
'''

@app.put('/update/<livro_id>/')
def update_livro(livro_id):
    query={
        '_id': ObjectId(livro_id)
    }
    content = {
        '$set': dict(request.json)
    }
    livro = collection.update_one(query, content)
    
    if not livro.matched_count:
        return {
            'message': 'Failed to update. Record is not found'
        }, 500
    return {'message': 'Update success'}, 200

"""
@ Rota para adicionar via API
"""

@app.post('/create/')
def create_livro():
    content = dict(request.json)

    # Insere o documento no banco de dados
    result = collection.insert_one(content)

    # Retorna uma mensagem de sucesso com o ID do novo documento
    return {
        'message': 'Livro criado com sucesso',
        'id': str(result.inserted_id)
    }, 201

'''
# Rota para deletar o ID
'''

@app.route('/delete/<livro_id>')
def delete(livro_id):
    collection.delete_one({'_id': ObjectId(livro_id)})
    flash('Livro deletado com sucesso', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(port=5000, debug=True)



