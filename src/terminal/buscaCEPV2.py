import sys
import json
import os # Importar o módulo os
# Adiciona o diretório raiz ao path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.api.getCepInfoV2 import get_cep_info

def run_cli_cep_search():
    """
    Entrada principal do sistema: solicita um CEP e exibe a resposta bruta da API.
    """
    print("=== Sistema de Pesquisa de CEP ===")
    print("Forneça um CEP (ex: 27267430 ou 27267-430)")
    
    # Lê o CEP do terminal
    cep = input("CEP: ").strip()
    
    if not cep:
        print("Nenhum CEP informado. Encerrando.")
        return
    
    try:
        # Chama a função que consulta a API
        response = get_cep_info(cep)
        
        # Exibe a resposta bruta (JSON) de forma legível
        print("\n--- Resposta da API ---")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
    except ValueError as e:
        print(f"\nErro de validação: {e}")
    except Exception as e:
        print(f"\nErro ao consultar a API: {e}")
    
    print("\nPressione Enter para sair...")
    input()

if __name__ == "__main__":
    run_cli_cep_search()
