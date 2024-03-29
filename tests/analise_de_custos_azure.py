from azure.identity import DefaultAzureCredential
from azure.mgmt.consumption import ConsumptionManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import ResourceGroup
from msrest.exceptions import HttpOperationError

import datetime
import pytz

# Configuração do cliente Azure
subscription_id = 'YOUR_SUB'  # Substitua YOUR_SUBSCRIPTION_ID pelo seu ID de assinatura real
credential = DefaultAzureCredential()
consumption_client = ConsumptionManagementClient(credential, subscription_id)
resource_client = ResourceManagementClient(credential, subscription_id)

local_timezone = pytz.timezone('America/Sao_Paulo')  # Fuso horário local

def list_costs_by_service(start_date, end_date):
    """
    Lista os custos reais dos serviços Azure para o período especificado.
    
    Args:
        start_date (datetime.datetime): Data de início do período de análise.
        end_date (datetime.datetime): Data de término do período de análise.
    """
    filter_str = _build_filter_string(start_date, end_date)
    print("Filtro usado:", filter_str)
    
    try:
        results = _get_usage_details(filter_str)
    except Exception as e:
        print("Erro ao obter os detalhes de uso:", e)
        return

    print("\nResumo de Custos Azure:")
    print("-" * 80)
    print("| {:<40} | {:<15} | {:<15} | {:<25} |".format("Serviço", "Custo", "Data de Uso", "Tipo de Serviço"))
    print("-" * 80)
    
    for result in results:
        service_name = _extract_service_name(result.instance_name)
        service_cost = result.cost_in_usd
        usage_date = _get_formatted_usage_date(result.date)
        resource_type = _get_resource_type(service_name)

        print("| {:<40} | {:<15.2f} | {:<15} | {:<25} |".format(service_name, service_cost, usage_date, resource_type))

    print("-" * 80)

def _build_filter_string(start_date, end_date):
    """
    Constrói a string de filtro para a consulta de detalhes de uso.
    """
    return f"properties/usageEnd ge '{start_date.strftime('%Y-%m-%dT%H:%M:%SZ')}' and properties/usageEnd le '{end_date.strftime('%Y-%m-%dT%H:%M:%SZ')}'"

def _get_usage_details(filter_str):
    """
    Obtém os detalhes de uso com base no filtro fornecido.
    """
    return consumption_client.usage_details.list(scope=f"/subscriptions/{subscription_id}", filter=filter_str)

def _extract_service_name(instance_name):
    """
    Extrai o nome do serviço a partir do nome da instância.
    
    Args:
        instance_name (str): Nome da instância do serviço.
    
    Returns:
        str: Nome do serviço extraído.
    """
    service_name_parts = instance_name.split('/')
    return service_name_parts[-1] if service_name_parts else "Desconhecido"

def _get_formatted_usage_date(date):
    """
    Formata a data de uso para incluir dia, mês e horário.
    
    Args:
        date (datetime.datetime): Data de uso a ser formatada.
    
    Returns:
        str: Data formatada no formato 'dd/mm/aaaa'.
    """
    local_date = date.replace(tzinfo=pytz.utc).astimezone(local_timezone)
    return local_date.strftime('%d/%m/%Y')

def _get_resource_type(service_name):
    """
    Obtém o tipo de serviço associado ao nome do serviço.
    """
    try:
        resources = resource_client.resources.list(filter=f"resourceType eq 'Microsoft.Compute/virtualMachines' and name eq '{service_name}'")
        for resource in resources:
            return resource.type
    except HttpOperationError as ex:
        print("Erro ao acessar a API de Gerenciamento de Recursos:", ex.response.text)
    return "Desconhecido"

def get_custom_date_range():
    """
    Solicita ao usuário datas de início e término para análise de custos.
    
    Returns:
        tuple: Tupla contendo a data de início e a data de término fornecidas pelo usuário.
    """
    while True:
        start_date_str = input("Data de início (AAAA-MM-DD): ")
        end_date_str = input("Data de término (AAAA-MM-DD): ")
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
            if start_date < end_date:
                return start_date, end_date
            else:
                print("Erro: A data de início deve ser anterior à data de término.")
        except ValueError:
            print("Formato de data inválido. Use o formato AAAA-MM-DD.")

if __name__ == '__main__':
    print("Digite o período desejado para análise de custos:")
    start_date, end_date = get_custom_date_range()
    list_costs_by_service(start_date, end_date)
