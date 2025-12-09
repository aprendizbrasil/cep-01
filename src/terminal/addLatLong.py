import csv
import sys
import os

# Adiciona o diretório raiz ao path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.api.getCepInfoV2 import get_cep_info

def process_csv(input_path, output_path):
    """
    Lê um CSV com colunas No;Bairro;Cep-Ini, consulta a API para obter
    latitude e longitude de cada CEP, e grava um novo CSV com colunas Lat e Long.
    """
    # Verifica se o arquivo de entrada existe
    if not os.path.exists(input_path):
        print(f"Erro: Arquivo de entrada '{input_path}' não encontrado.")
        return False
    
    # Abre o arquivo de entrada com encoding Latin-1
    try:
        with open(input_path, 'r', encoding='latin-1') as infile:
            # Detecta delimitador (ponto‑e‑vírgula)
            sample = infile.read(1024)
            infile.seek(0)
            delimiter = ';' if ';' in sample else ','
            
            reader = csv.DictReader(infile, delimiter=delimiter)
            fieldnames = reader.fieldnames
            
            # Verifica se as colunas Lat e Long já existem
            has_lat = 'Lat' in fieldnames
            has_long = 'Long' in fieldnames
            
            # Define os fieldnames de saída (mantém os existentes)
            new_fieldnames = fieldnames.copy()
            if not has_lat:
                new_fieldnames.append('Lat')
            if not has_long:
                new_fieldnames.append('Long')
            
            # Abre o arquivo de saída (também Latin-1)
            with open(output_path, 'w', newline='', encoding='latin-1') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=new_fieldnames, delimiter=delimiter)
                writer.writeheader()
                
                # Processa cada linha
                for row in reader:
                    cep = row.get('Cep-Ini', '').strip()
                    lat = ''
                    long = ''
                    
                    if cep:
                        try:
                            # Consulta a API
                            api_response = get_cep_info(cep)
                            # Extrai coordenadas do resultado
                            coordinates = api_response.get('result', {}).get('coordinates', {})
                            lat_raw = coordinates.get('latitude', '')
                            long_raw = coordinates.get('longitude', '')
                            # Converte ponto para vírgula (formato brasileiro)
                            lat = str(lat_raw).replace('.', ',') if lat_raw != '' else ''
                            long = str(long_raw).replace('.', ',') if long_raw != '' else ''
                        except Exception as e:
                            # Em caso de erro, mantém vazio e imprime mensagem
                            print(f"Erro ao processar CEP {cep}: {e}")
                            lat = ''
                            long = ''
                    
                    # Atualiza as colunas Lat e Long (se existirem, sobrescreve; se não, cria)
                    row['Lat'] = lat
                    row['Long'] = long
                    
                    # Escreve a linha no arquivo de saída
                    writer.writerow(row)
                    
                    # Imprime a linha no terminal (conforme solicitado)
                    print(f"No: {row.get('No', '')}, "
                          f"Bairro: {row.get('Bairro', '')}, "
                          f"CEP: {cep}, "
                          f"Lat: {lat}, "
                          f"Long: {long}")
    
    except Exception as e:
        print(f"Erro inesperado ao processar CSV: {e}")
        return False
    
    print(f"\nProcessamento concluído. Arquivo salvo em: {output_path}")
    return True

if __name__ == "__main__":
    # Caminhos padrão
    input_csv = os.path.join('sources', 'Cidades-Bairros-CEPs.csv')
    output_csv = os.path.join('sources', 'Cidades-Bairros-CEPs-com-coordenadas.csv')
    
    # Executa o processamento
    success = process_csv(input_csv, output_csv)
    sys.exit(0 if success else 1)
