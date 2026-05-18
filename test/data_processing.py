import os
import configparser
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd

# Nastavení logování
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("app_operation.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class DataProcessing:
    def __init__(self, config_path: str):
        """Inicializace třídy a načtení konfigurace z INI souboru."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Konfigurační soubor {config_path} neexistuje.")
        
        self.config = configparser.ConfigParser()
        self.config.read(config_path, encoding="utf-8")
        
        try:
            self.smtp_server = self.config['SMTP']['server']
            self.smtp_port = int(self.config['SMTP']['port'])
            self.smtp_user = self.config['SMTP']['username']
            self.smtp_password = self.config['SMTP']['password']
            self.sender = self.config['SMTP']['sender']
            self.recipient = self.config['SMTP']['recipient']
            logging.info("Konfigurace úspěšně načtena.")
        except KeyError as e:
            logging.error(f"Chybí klíč v konfiguračním souboru: {e}")
            raise

        self.df = None
        self.file_base_name = ""

    def load_excel(self, file_path: str):
        """Načte Excel soubor do pandas DataFrame a explicitně ošetří číselné sloupce."""
        if not os.path.exists(file_path):
            logging.error(f"Soubor {file_path} nebyl nalezen.")
            raise FileNotFoundError(f"Soubor {file_path} neexistuje.")
        
        logging.info(f"Načítám soubor {file_path}...")
        self.df = pd.read_excel(file_path, engine='openpyxl') 
        self.file_base_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # Explicitně definujw sloupce, které reprezentují reálná čísla (měření/plochy)
        numeric_columns = ['Plocha VB (VFK GP)', 'Plocha VB (TAB)', 'Délka']
        
        for col in numeric_columns:
            if col in self.df.columns:
                try:
                    # Převe na string, nahradí českou čárku tečkou a převede na číslo.
                    # Znaky jako 'X' se bezpečně změní na NaN.
                    sanitized = self.df[col].astype(str).str.replace(',', '.', regex=False)
                    self.df[col] = pd.to_numeric(sanitized, errors='coerce')
                    logging.info(f"Sloupec '{col}' byl úspěšně zkonvertován na numerický typ.")
                except Exception as e:
                    logging.warning(f"Chyba při konverzi sloupce {col}: {e}")

        logging.info(f"Soubor {file_path} úspěšně načten a pročištěn. Počet řádků: {len(self.df)}")
    def generate_statistics(self) -> str:
        """Provede detailní statistické vyhodnocení a uloží ho do .log souboru."""
        if self.df is None:
            raise ValueError("Data nejsou načtena. Nejdříve spusťte load_excel().")

        log_filename = f"{self.file_base_name}_statistika.log"
        logging.info(f"Generuji statistiku do souboru {log_filename}...")

        lines = []
        lines.append(f"Statistické vyhodnocení pro soubor: {self.file_base_name}")
        lines.append("-" * 50)
        lines.append(f"Celkový počet záznamů (řádků): {len(self.df)}")
        lines.append(f"Celkový počet sloupců: {len(self.df.columns)}\n")

        for col in self.df.columns:
            lines.append(f"--- Sloupec: {col} ---")
            lines.append(f"Počet unikátních dat: {self.df[col].nunique()}")
            lines.append(f"Počet prázdných záznamů: {self.df[col].isna().sum()}")
            
            # Kontrola na numerický typ
            if pd.api.types.is_numeric_dtype(self.df[col]) and not pd.api.types.is_bool_dtype(self.df[col]):
                # Vynechá sloupce, které jsou komplet prázdné
                if self.df[col].notna().sum() > 0:
                    lines.append(f"Průměrná hodnota: {self.df[col].mean():.2f}")
                    lines.append(f"Minimální hodnota: {self.df[col].min()}")
                    lines.append(f"Maximální hodnota: {self.df[col].max()}")
                else:
                    lines.append("Sloupec je zcela prázdný (statistické hodnoty nelze spočítat).")
            else:
                lines.append("Sloupec není numerického typu (statistika min/max/průměr vynechána).")
            lines.append("")

        with open(log_filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logging.info("Statistika úspěšně uložena.")
        return log_filename

    def save_to_csv(self) -> str:
        """Uloží pročištěná data jako CSV v UTF-8."""
        if self.df is None:
            raise ValueError("Data nejsou načtena.")

        csv_filename = f"{self.file_base_name}.csv"
        logging.info(f"Ukládám data do CSV: {csv_filename}...")
        self.df.to_csv(csv_filename, index=False, encoding="utf-8")
        logging.info("CSV soubor úspěšně uložen.")
        return csv_filename

    def send_email(self, attachment_path: str):
        """Odešle e-mail s přílohou přes nakonfigurovaný SMTP."""
        if not os.path.exists(attachment_path):
            raise FileNotFoundError(f"Příloha {attachment_path} neexistuje.")

        logging.info(f"Připravuji e-mail pro {self.recipient}...")
        
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = self.recipient
        msg['Subject'] = f"Automatický export: {os.path.basename(attachment_path)}"
        
        body = "Dobrý den,\nv příloze zasílám vygenerovaný soubor na základě zadání.\n\nS pozdravem,\nAutomatický Python Skript"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        filename = os.path.basename(attachment_path)
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
            msg.attach(part)

        logging.info(f"Připojování k SMTP serveru {self.smtp_server}:{self.smtp_port}...")
        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.sender, self.recipient, msg.as_string())
            logging.info("E-mail byl úspěšně odeslán!")
        except Exception as e:
            logging.error(f"Chyba při odesílání e-mailu: {e}")
            raise