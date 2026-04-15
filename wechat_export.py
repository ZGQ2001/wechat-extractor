import click
import logging
from src.utils import setup_logging, get_platform
from src.key_extractor import extract_key
from src.db_finder import find_and_decrypt_all
from src.parser import WeChatParser
from src.exporter import Exporter
from pathlib import Path

@click.command()
@click.option('--platform', type=click.Choice(['mac', 'windows']), required=True, help='Target platform')
@click.option('--key', help='Directly provide hex key')
@click.option('--db-path', help='Custom DB directory')
@click.option('--output-dir', default='./output', help='Output directory')
@click.option('--format', type=click.Choice(['csv', 'html', 'json', 'all']), default='all', help='Export format')
@click.option('--extract-key', is_flag=True, help='Only extract key and exit')
def main(platform, key, db_path, output_dir, format, extract_key):
    setup_logging()
    logger = logging.getLogger("Main")
    if not key:
        logger.info(f"Attempting to extract key for {platform}...")
        key = extract_key(platform)
        if not key:
            logger.error("Failed to extract key. Please ensure WeChat is running.")
            return
    logger.info(f"Using Key: {key}")
    if extract_key:
        print(f"Extracted Key: {key}")
        return
    logger.info("Scanning and decrypting databases...")
    decrypted_files = find_and_decrypt_all(platform, key, output_dir, db_path)
    if not decrypted_files:
        logger.error("No databases were decrypted.")
        return
    for db_file in decrypted_files:
        logger.info(f"Parsing {db_file}...")
        parser = WeChatParser(db_file)
        tables = parser.get_all_chat_tables()
        all_messages = []
        for table in tables:
            all_messages.extend(parser.parse_chat(table, contact_id=table))
        base_name = Path(db_file).stem
        if format in ['csv', 'all']:
            Exporter.to_csv(all_messages, f"{output_dir}/{base_name}.csv")
        if format in ['json', 'all']:
            Exporter.to_json(all_messages, f"{output_dir}/{base_name}.json")
        if format in ['html', 'all']:
            Exporter.to_html(all_messages, f"{output_dir}/{base_name}.html")
        parser.close()
    logger.info(f"Export completed. Results saved to {output_dir}")

if __name__ == "__main__":
    main()
