import datetime
from azure.identity import DefaultAzureCredential
from azure.mgmt.consumption import ConsumptionManagementClient

# Configuração do cliente Azure
credential = DefaultAzureCredential()
subscription_id = 'YOUR_SUBSCRIPTION_ID'
consumption_client = ConsumptionManagementClient(credential, subscription_id)

# Função para obter e listar os serviços e valores de gastos
def list_costs_by_service(start_date, end_date):
    """
    Obtém e lista os custos dos serviços Azure para o período de tempo especificado.
    """
    
    if not start_date or not end_date:
        return

    query_options = {
        "filter": "properties/usageEnd ge " + start_date.strftime('%Y-%m-%dT%H:%M:%SZ') + " and properties/usageEnd le " + end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    }

    results = consumption_client.usage_details.list(query_options, raw=True)

    for result in results:
        service_name = result['properties']['instanceName']
        cost = result['properties']['pretaxCost']
        print(f"Serviço: {service_name}, Custo: ${cost:.2f}")

# Função para obter o período desejado de forma interativa
def get_custom_date_range():
    """
    Solicita ao usuário que insira as datas de início e término para a análise de custos.
    As datas devem ser inseridas no formato AAAA-MM-DD.
    """

    print("Digite o período desejado para análise de custos:")
    start_date_str = input("Data de início (AAAA-MM-DD): ")
    end_date_str = input("Data de término (AAAA-MM-DD): ")

    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
        return start_date, end_date
    except ValueError:
        print("Formato de data inválido. Use o formato AAAA-MM-DD.")
        return get_custom_date_range()
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.")
        return None

if __name__ == '__main__':
    start_date, end_date = get_custom_date_range()
    if start_date and end_date:
        list_costs_by_service(start_date, end_date)
