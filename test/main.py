from data_processing import DataProcessing

def main():
    # Inicializace třídy s konfigurací
    processor = DataProcessing(config_path="config.ini")
    
    # 1. Načtení excelu
    input_file = "223344.xlsx"
    processor.load_excel(input_file)
    
    # 2. Generování statistik
    processor.generate_statistics()
    
    # 3. Uložení do CSV
    csv_file = processor.save_to_csv()
    
    # 4. Odeslání e-mailem
    processor.send_email(attachment_path=csv_file)

if __name__ == "__main__":
    main()


# Poznámka: Seznam server odmítne ověření neboť je heslo vymyšlené (z bezpečnostních důvodů).