import json
import requests
import os
import sys

# Adiciona o diretório raiz ao path para importar configurações
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def get_cep_info(cep):
    """
    Consulta a API Brasil Aberto para obter informações de um CEP.
    
    Args:
        cep (str): CEP no formato '12345678' (com ou sem hífen).
    
    Returns:
        dict: Resposta bruta da API (JSON decodificado) em caso de sucesso.
    
    Raises:
        ValueError: Se o CEP for inválido (não contém 8 dígitos).
        requests.exceptions.RequestException: Em caso de erro de rede ou resposta não‑200.
    """
    # Remove caracteres não numéricos
    cep_clean = ''.join(filter(str.isdigit, cep))
    if len(cep_clean) != 8:
        raise ValueError(f"CEP inválido: '{cep}'. Deve conter 8 dígitos.")
    
    # Carrega configurações
    try:
        with open('.settings.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        raise RuntimeError("Arquivo de configuração .settings.json não encontrado.")
    except json.JSONDecodeError:
        raise RuntimeError("Erro ao decodificar .settings.json.")
    
    base_url = config['api']['base_url']
    token = config['api']['bearer_token']
    
    url = f"{base_url}/v2/zipcode/{cep_clean}"
    headers = {
        'accept': 'application/json',
        'Bearer': token
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Levanta exceção para status 4xx/5xx
        return response.json()  # Retorna a resposta bruta (dict)
    except requests.exceptions.Timeout:
        raise requests.exceptions.RequestException("Timeout ao consultar a API.")
    except requests.exceptions.ConnectionError:
        raise requests.exceptions.RequestException("Erro de conexão com a API.")
    except requests.exceptions.HTTPError as e:
        # Tenta extrair detalhes da resposta de erro
        try:
            error_detail = response.json()
        except:
            error_detail = response.text
        raise requests.exceptions.RequestException(
            f"Erro HTTP {response.status_code}: {error_detail}"
        )


if __name__ == "__main__":
    # Teste simples do módulo
    import sys
    if len(sys.argv) > 1:
        cep = sys.argv[1]
    else:
        cep = input("Digite um CEP para teste: ")
    try:
        result = get_cep_info(cep)
        print("Resposta da API:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Erro: {e}")
