import os
import sys

# Adiciona o diretório 'src/web' ao path para que o Flask possa encontrar 'routes'
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'web'))

# Importa a aplicação Flask do módulo routes
from routes import app

if __name__ == '__main__':
    # Configurações de execução
    # Em produção, você deve usar um servidor WSGI como Gunicorn ou Waitress
    # e desativar o debug.
    # Por exemplo: waitress-serve --host=0.0.0.0 --port=5000 app:app
    app.run(debug=True, host="0.0.0.0", port=5000)
