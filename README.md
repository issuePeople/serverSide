# IssuePeople: serverSide

Repositori amb el server side del projecte d'ASW (primera entrega).

## Membres de l'equip

Nora Caballero de Llanos

Pau Duran Manzano

Àngel Prat Vilà

Sol Torralba Calero


## Enllaços

- Taiga: https://tree.taiga.io/project/angelprat-asw
- Desplegament a AWS: http://issuepeople-env.eba-bhtdckwp.us-west-2.elasticbeanstalk.com/issues/
- Desplegament a AWS (API): http://issuepeople-env.eba-bhtdckwp.us-west-2.elasticbeanstalk.com/api/
- Desplegament a AWS (documentació): http://issuepeople-env.eba-bhtdckwp.us-west-2.elasticbeanstalk.com/api/doc/


## Execució i ús en local

### Primera posada en marxa
- Clonar el repositori amb la comanda git clone
- Entrar dins la carpeta del projecte
- Crear l'entorn virtual: python3 -m venv env
- Entrar a l'entorn virtual: source env/bin/activate
- Instal·lar els requeriments: pip install -r requirements.txt
- Crear la BD de development: python manage.py migrate
- Posar en marxa: python manage.py runserver

### Per executar
- Entrar al virtual environment: source env/bin/activate
- Posar en marxa: python manage.py runserver

### Per fer migracions (durant el desenvolupament)
- Generar els fitxers: python manage.py makemigrations
- Migrar la BD: pyhton manage.py migrate
