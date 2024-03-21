from analise_de_custos_azure import get_custom_date_range, list_costs_by_service

def main():
    """
    Função principal que solicita ao usuário um intervalo de datas e lista os custos dos serviços Azure para esse intervalo.
    """
    start_date, end_date = get_custom_date_range()
    list_costs_by_service(start_date, end_date)

if __name__ == "__main__":
    main()
