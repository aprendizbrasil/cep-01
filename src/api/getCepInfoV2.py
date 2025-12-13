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
    
def _call_brasil_aberto_api(cep_clean, config):
    """Consulta a API Brasil Aberto."""
    base_url = config['api']['base_url']
    token = config['api']['bearer_token']
    url = f"{base_url}/v2/zipcode/{cep_clean}"
    headers = {
        'accept': 'application/json',
        'Bearer': token
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()

def _call_viacep_api(cep_clean):
    """Consulta a API ViaCEP."""
    url = f"https://viacep.com.br/ws/{cep_clean}/json/"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    if data.get('erro'): # ViaCEP retorna {'erro': true} para CEPs não encontrados
        raise requests.exceptions.RequestException(f"CEP {cep_clean} não encontrado na ViaCEP.")
    
    # Formata a resposta da ViaCEP para ser compatível com a estrutura da Brasil Aberto
    # Coordenadas serão deixadas vazias conforme solicitado
    return {
        "meta": {"currentPage": 1, "itemsPerPage": 1, "totalOfItems": 1},
        "result": {
            "zipcode": cep_clean,
            "street": data.get('logradouro', ''),
            "complement": data.get('complemento', ''),
            "district": data.get('bairro', ''),
            "city": data.get('localidade', ''),
            "state": data.get('uf', ''),
            "stateShortname": data.get('uf', ''),
            "ibgeId": data.get('ibge', ''),
            "coordinates": {"latitude": "", "longitude": ""}
        }
    }

def get_cep_info(cep):
    """Consulta APIs de CEP com fallback para ViaCEP."""
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
    
    api_errors = []

    # Tentar Brasil Aberto API
    try:
        print(f"Tentando Brasil Aberto para CEP: {cep_clean}")
        result = _call_brasil_aberto_api(cep_clean, config)
        result['source_api'] = 'Brasil Aberto'
        return result
    except (requests.exceptions.RequestException, requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        api_errors.append(f"Brasil Aberto falhou: {e}")
        print(f"Brasil Aberto falhou para CEP {cep_clean}: {e}. Tentando ViaCEP...")

    # Fallback para ViaCEP API
    try:
        print(f"Tentando ViaCEP para CEP: {cep_clean}")
        result = _call_viacep_api(cep_clean)
        result['source_api'] = 'ViaCEP'
        return result
    except (requests.exceptions.RequestException, requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        api_errors.append(f"ViaCEP falhou: {e}")
        print(f"ViaCEP falhou para CEP {cep_clean}: {e}.")

    # Se todas falharem
    raise Exception(f"Todas as APIs de CEP falharam para {cep_clean}. Erros: {'; '.join(api_errors)}")


if __name__ == "__main__":
    # Teste simples do módulo
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
